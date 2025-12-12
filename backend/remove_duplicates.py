"""
childbook_items 테이블에서 title, author, publisher가 동일한 중복 데이터 제거
각 그룹에서 하나만 남기고 나머지 삭제
"""
from supabase_client import supabase
from collections import defaultdict

print("=" * 60)
print("중복 데이터 제거")
print("=" * 60)
print()

try:
    # 먼저 전체 데이터 수 확인
    print("전체 데이터 수 확인 중...")
    count_result = supabase.table("childbook_items").select("*", count="exact").execute()
    count_before = count_result.count if hasattr(count_result, 'count') else 0
    print(f"삭제 전 총 도서 수: {count_before}건")
    print()
    
    # 모든 데이터 조회 (페이지네이션)
    print("데이터 조회 중...")
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        data = supabase.table("childbook_items").select("*").range(offset, offset + page_size - 1).execute()
        
        if not data.data or len(data.data) == 0:
            break
        
        all_data.extend(data.data)
        offset += page_size
        
        if offset % 5000 == 0:
            print(f"  {offset}건 조회 중...")
        
        if len(data.data) < page_size:
            break
    
    print(f"총 {len(all_data)}건 조회 완료")
    print()
    
    # 중복 찾기: (title, author, publisher) 조합으로 그룹화
    print("중복 데이터 검색 중...")
    groups = defaultdict(list)
    
    for item in all_data:
        title = str(item.get('title', '')).strip().lower() if item.get('title') else ''
        author = str(item.get('author', '')).strip().lower() if item.get('author') else ''
        publisher = str(item.get('publisher', '')).strip().lower() if item.get('publisher') else ''
        
        # 키 생성 (title, author, publisher 조합)
        key = (title, author, publisher)
        groups[key].append(item)
    
    # 중복이 있는 그룹 찾기
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"중복 그룹 수: {len(duplicate_groups)}개")
    
    # 삭제할 ID 목록 생성 (각 그룹에서 첫 번째 것만 남기고 나머지 삭제)
    delete_ids = []
    total_duplicates = 0
    
    for key, items in duplicate_groups.items():
        # 첫 번째 항목은 유지, 나머지는 삭제 대상
        for item in items[1:]:
            delete_ids.append(item.get('id'))
            total_duplicates += 1
    
    print(f"삭제 대상: {total_duplicates}건")
    print()
    
    if not delete_ids:
        print("중복 데이터가 없습니다.")
    else:
        print("삭제 시작...")
        print("-" * 60)
        
        deleted_count = 0
        error_count = 0
        
        # 배치로 삭제
        batch_size = 100
        
        for i in range(0, len(delete_ids), batch_size):
            batch = delete_ids[i:i+batch_size]
            for id_val in batch:
                try:
                    supabase.table("childbook_items").delete().eq("id", id_val).execute()
                    deleted_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"  ID {id_val} 삭제 오류: {e}")
            
            if (i + batch_size) % 500 == 0 or i + batch_size >= len(delete_ids):
                print(f"  {min(i + batch_size, len(delete_ids))}/{len(delete_ids)} 삭제 중...")
        
        print("-" * 60)
        print(f"✅ 삭제 완료!")
        print(f"   삭제됨: {deleted_count}건")
        print(f"   오류: {error_count}건")
        
        # 삭제 후 데이터 수 확인
        try:
            updated = supabase.table("childbook_items").select("*", count="exact").execute()
            count_after = updated.count if hasattr(updated, 'count') else 0
            print(f"\n삭제 후 총 도서 수: {count_after}권 (-{count_before - count_after})")
        except Exception as e:
            print(f"\n최종 데이터 확인 중 오류: {e}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()







