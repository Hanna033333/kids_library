"""
childbook_items와 library_items를 제목 기반으로 매칭하여
owned, similarity, pangyo_callno 필드를 업데이트
"""
from supabase_client import supabase
from rapidfuzz import fuzz, process
import sys

print("=" * 60)
print("childbook_items와 판교 도서관 매칭")
print("=" * 60)
print()

# 1) childbook_items 가져오기 (전체 데이터)
print("1. childbook_items 데이터 로딩 중...")
try:
    child_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        child_items.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   ✅ {len(child_items):,}개 항목 로드 완료")
except Exception as e:
    print(f"   ❌ 오류: {e}")
    sys.exit(1)

print()

# 2) 판교 장서 가져오기 (전체 데이터)
print("2. library_items (판교 도서관) 데이터 로딩 중...")
try:
    pangyo_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("library_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        pangyo_items.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   ✅ {len(pangyo_items):,}개 항목 로드 완료")
except Exception as e:
    print(f"   ❌ 오류: {e}")
    sys.exit(1)

print()

# 3) 판교 title 리스트 만들기 (similarity search 용)
print("3. 판교 도서관 제목 리스트 생성 중...")
pangyo_titles = [p.get("title", "") for p in pangyo_items if p.get("title")]
print(f"   ✅ {len(pangyo_titles):,}개 제목 준비 완료")
print()

def find_best_match(title):
    """제목 기반 best match 찾아 similarity, index 반환"""
    if not title or not pangyo_titles:
        return None
    
    match = process.extractOne(title, pangyo_titles, scorer=fuzz.partial_ratio)
    return match  # (best_title, score, index)

# 4) childbook_items 루프 돌면서 best match 찾기
print("4. 매칭 진행 중...")
print()

updates = []
matched_count = 0
unmatched_count = 0

for idx, item in enumerate(child_items):
    title = item.get("title", "")
    
    if not title:
        updates.append({
            "id": item["id"],
            "owned": False,
            "similarity": 0,
            "pangyo_callno": None
        })
        unmatched_count += 1
        continue
    
    match_result = find_best_match(title)
    
    if match_result:
        best_title, score, match_idx = match_result
        pangyo_book = pangyo_items[match_idx]
        
        # similarity를 정수로 변환 (소수점 반올림)
        similarity_int = int(round(score))
        
        if score > 45:  # threshold
            updates.append({
                "id": item["id"],
                "owned": True,
                "similarity": similarity_int,
                "pangyo_callno": pangyo_book.get("callno")
            })
            matched_count += 1
        else:
            updates.append({
                "id": item["id"],
                "owned": False,
                "similarity": similarity_int,
                "pangyo_callno": None
            })
            unmatched_count += 1
    else:
        updates.append({
            "id": item["id"],
            "owned": False,
            "similarity": 0,
            "pangyo_callno": None
        })
        unmatched_count += 1
    
    # 진행 상황 출력 (100개마다)
    if (idx + 1) % 100 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_items)} ({matched_count}개 매칭됨)")

print()
print(f"   ✅ 매칭 완료!")
print(f"      - 매칭됨 (similarity > 45): {matched_count}개")
print(f"      - 매칭 안됨: {unmatched_count}개")
print()

# 5) supabase 업데이트 (batch 업서트)
print("5. Supabase 업데이트 중...")
print()

success_count = 0
error_count = 0

for idx, row in enumerate(updates):
    try:
        supabase.table("childbook_items").update({
            "owned": row["owned"],
            "similarity": row["similarity"],
            "pangyo_callno": row["pangyo_callno"]
        }).eq("id", row["id"]).execute()
        
        success_count += 1
        
        # 진행 상황 출력 (100개마다)
        if (idx + 1) % 100 == 0:
            print(f"   업데이트 중: {idx + 1}/{len(updates)}")
            
    except Exception as e:
        error_count += 1
        if error_count <= 5:  # 처음 5개 오류만 출력
            print(f"   ❌ ID {row['id']} 업데이트 오류: {e}")

print()
print("=" * 60)
print("✅ 완료!")
print("-" * 60)
print(f"총 처리: {len(updates)}개")
print(f"성공: {success_count}개")
if error_count > 0:
    print(f"실패: {error_count}개")
print(f"매칭됨: {matched_count}개")
print(f"매칭 안됨: {unmatched_count}개")
print("=" * 60)

