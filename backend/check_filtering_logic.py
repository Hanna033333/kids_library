"""
필터링 로직 확인: ISBN 또는 pangyo_callno가 없는 항목이 정말 3,123개인지 확인
"""
from supabase_client import supabase

print("=" * 60)
print("필터링 로직 확인")
print("=" * 60)
print()

# 전체 항목 수
total = supabase.table("childbook_items").select("*", count="exact").execute()
total_count = total.count if hasattr(total, 'count') else len(total.data) if total.data else 0

print(f"전체 childbook_items: {total_count:,}개")
print()

# 전체 데이터를 페이지별로 가져와서 정확히 계산
has_isbn_count = 0
has_pangyo_count = 0
both_complete_count = 0
missing_both_count = 0
missing_isbn_only = 0
missing_pangyo_only = 0

page = 0
page_size = 1000

print("데이터 분석 중...")
while True:
    res = supabase.table("childbook_items").select("isbn,pangyo_callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn = item.get("isbn")
        pangyo_callno = item.get("pangyo_callno")
        
        has_isbn = isbn and len(str(isbn).strip()) > 0
        has_pangyo = pangyo_callno and len(str(pangyo_callno).strip()) > 0
        
        if has_isbn:
            has_isbn_count += 1
        if has_pangyo:
            has_pangyo_count += 1
        if has_isbn and has_pangyo:
            both_complete_count += 1
        if not has_isbn and not has_pangyo:
            missing_both_count += 1
        if not has_isbn and has_pangyo:
            missing_isbn_only += 1
        if has_isbn and not has_pangyo:
            missing_pangyo_only += 1
    
    if len(res.data) < page_size:
        break
    page += 1

# 처리 대상 (ISBN 또는 pangyo_callno 없음)
# 즉, 둘 중 하나라도 없으면 처리 대상
processing_target = missing_both_count + missing_isbn_only + missing_pangyo_only

print()
print("=" * 60)
print("분석 결과")
print("=" * 60)
print()
print(f"전체: {total_count:,}개")
print()
print(f"✅ 완료 (둘 다 있음): {both_complete_count:,}개 ({both_complete_count/total_count*100:.1f}%)")
print()
print(f"❌ 처리 대상 (ISBN 또는 pangyo_callno 없음): {processing_target:,}개")
print(f"   - 둘 다 없음: {missing_both_count:,}개")
print(f"   - ISBN만 없음: {missing_isbn_only:,}개")
print(f"   - pangyo_callno만 없음: {missing_pangyo_only:,}개")
print()
print(f"ISBN 있음: {has_isbn_count:,}개 ({has_isbn_count/total_count*100:.1f}%)")
print(f"pangyo_callno 있음: {has_pangyo_count:,}개 ({has_pangyo_count/total_count*100:.1f}%)")
print()
print("=" * 60)

