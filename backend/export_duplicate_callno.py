"""
중복 청구기호를 가진 책들을 CSV 파일로 추출
"""
from supabase_client import supabase
from collections import defaultdict
import csv
import json

print("=" * 60)
print("중복 청구기호 항목 추출")
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
            base_callno = callno
            if '-' in callno:
                parts = callno.rsplit('-', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    base_callno = parts[0]
            
            callno_groups[base_callno].append({
                'isbn13': item.get('isbn13', ''),
                'title': item.get('title', ''),
                'author': item.get('author', ''),
                'callno': callno,
                'base_callno': base_callno,
            })
    
    # 중복이 있는 그룹 찾기 (2개 이상)
    duplicate_groups = {k: v for k, v in callno_groups.items() if len(v) >= 2}
    
    print(f"중복 청구기호 그룹 수: {len(duplicate_groups)}개")
    print()
    
    # 중복 항목들을 평탄화하여 리스트로 만들기
    duplicate_items = []
    for base_callno, books in sorted(duplicate_groups.items()):
        for book in books:
            duplicate_items.append({
                '기본청구기호': base_callno,
                '현재청구기호': book['callno'],
                'ISBN': book['isbn13'],
                '제목': book['title'],
                '저자': book['author'],
                '중복수': len(books),
            })
    
    # CSV 파일로 저장
    csv_filename = 'duplicate_callno_items.csv'
    if duplicate_items:
        with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['기본청구기호', '현재청구기호', 'ISBN', '제목', '저자', '중복수']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(duplicate_items)
        
        print(f"✅ CSV 파일 저장 완료: {csv_filename}")
        print(f"   총 {len(duplicate_items)}건 저장됨")
    else:
        print("중복 청구기호가 없습니다.")
    
    # JSON 파일로도 저장 (선택사항)
    json_filename = 'duplicate_callno_items.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(duplicate_items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON 파일 저장 완료: {json_filename}")
    print()
    
    # 통계 출력
    print("=" * 60)
    print("통계:")
    print("=" * 60)
    print(f"전체 도서 수: {len(all_data)}권")
    print(f"고유 청구기호 수: {len(callno_groups)}개")
    print(f"중복 청구기호 그룹 수: {len(duplicate_groups)}개")
    print(f"중복 청구기호를 가진 도서 수: {len(duplicate_items)}권")
    print()
    
    # 그룹별 요약 출력
    print("=" * 60)
    print("중복 청구기호 그룹 요약:")
    print("=" * 60)
    for base_callno, books in sorted(duplicate_groups.items()):
        print(f"\n기본 청구기호: {base_callno}")
        print(f"  중복 수: {len(books)}권")
        for i, book in enumerate(books, 1):
            print(f"  {i}. {book['title'][:50]}")
            print(f"     ISBN: {book['isbn13']}")
            print(f"     현재 청구기호: {book['callno']}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()






