"""
library_items 테이블에서 중복 청구기호 찾기
같은 청구기호를 가진 책들(권차 기호가 필요한 경우)을 찾습니다.
"""
from supabase_client import supabase
from collections import defaultdict

print("=" * 60)
print("중복 청구기호 찾기")
print("=" * 60)
print()

try:
    # 전체 데이터 조회
    print("데이터 조회 중...")
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        data = supabase.table("library_items").select("*").range(offset, offset + page_size - 1).execute()
        
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
    
    # 청구기호별로 그룹화 (권차 기호 제외한 부분으로)
    print("중복 청구기호 검색 중...")
    callno_groups = defaultdict(list)
    
    for item in all_data:
        callno = item.get('callno', '')
        if callno:
            # 권차 기호 제외한 기본 청구기호 추출
            # 예: '유 808.9-ㅇ175ㅇ-204' -> '유 808.9-ㅇ175ㅇ'
            # 또는 '유 808.9-ㅇ175ㅇ' -> '유 808.9-ㅇ175ㅇ'
            base_callno = callno
            # 마지막 '-' 뒤의 숫자가 권차 기호일 수 있음
            if '-' in callno:
                parts = callno.rsplit('-', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    # 마지막 부분이 숫자면 권차 기호로 간주
                    base_callno = parts[0]
            
            callno_groups[base_callno].append({
                'isbn13': item.get('isbn13', ''),
                'title': item.get('title', ''),
                'author': item.get('author', ''),
                'callno': callno,
            })
    
    # 중복이 있는 그룹 찾기 (2개 이상)
    duplicate_groups = {k: v for k, v in callno_groups.items() if len(v) >= 2}
    
    print(f"중복 청구기호 그룹 수: {len(duplicate_groups)}개")
    print()
    
    if duplicate_groups:
        print("=" * 60)
        print("중복 청구기호 목록:")
        print("=" * 60)
        print()
        
        total_duplicates = 0
        for base_callno, books in sorted(duplicate_groups.items()):
            print(f"기본 청구기호: {base_callno}")
            print(f"  중복 수: {len(books)}권")
            print()
            
            for i, book in enumerate(books, 1):
                print(f"  {i}. {book['title'][:50]}")
                print(f"     ISBN: {book['isbn13']}")
                print(f"     현재 청구기호: {book['callno']}")
                print()
            
            total_duplicates += len(books)
            print("-" * 60)
            print()
        
        print(f"총 {total_duplicates}권이 중복 청구기호를 가지고 있습니다.")
        print()
        print("이 책들에 대해서만 웹사이트 크롤링으로 권차 기호를 가져올 수 있습니다.")
    else:
        print("중복 청구기호가 없습니다.")
    
    # 통계 출력
    print()
    print("=" * 60)
    print("통계:")
    print("=" * 60)
    print(f"전체 도서 수: {len(all_data)}권")
    print(f"고유 청구기호 수: {len(callno_groups)}개")
    print(f"중복 청구기호 그룹 수: {len(duplicate_groups)}개")
    
    if duplicate_groups:
        duplicate_count = sum(len(v) for v in duplicate_groups.values())
        print(f"중복 청구기호를 가진 도서 수: {duplicate_count}권")
        print(f"크롤링 대상 도서 수: {duplicate_count}권")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()






