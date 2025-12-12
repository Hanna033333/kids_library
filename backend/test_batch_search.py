"""
작은 배치(10개)로 웹사이트 검색 테스트
"""
from supabase_client import supabase
from search_pangyo_website import search_callno_from_website
import csv
import time

print("=" * 60)
print("웹사이트 검색 테스트 (10개 항목)")
print("=" * 60)
print()

# CSV 파일에서 처음 10개만 읽기
csv_filename = "no_callno_items.csv"
print(f"CSV 파일 읽기: {csv_filename}")

test_items = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            if idx >= 10:  # 10개만
                break
            
            child_id = row.get('id', '').strip()
            isbn = row.get('isbn', '').strip()
            title = row.get('title', '').strip()
            
            if child_id and (isbn or title):
                test_items.append({
                    'child_id': int(child_id),
                    'isbn': isbn,
                    'title': title
                })
    
    print(f"테스트 항목: {len(test_items)}개")
except Exception as e:
    print(f"오류: {e}")
    exit(1)

print()

# 각 항목 검색 및 결과 출력
print("웹사이트 검색 테스트 시작...")
print()

success_count = 0
fail_count = 0
not_found_count = 0

for idx, item in enumerate(test_items):
    child_id = item['child_id']
    isbn = item['isbn']
    title = item['title']
    
    print(f"[{idx + 1}/{len(test_items)}] ID: {child_id}")
    print(f"  제목: {title[:50]}")
    print(f"  ISBN: {isbn}")
    print("  검색 중...", end=" ", flush=True)
    
    start_time = time.time()
    try:
        callno = search_callno_from_website(isbn, title)
        elapsed = time.time() - start_time
        
        if callno and len(callno.strip()) > 0:
            print(f"✅ 찾음: {callno} ({elapsed:.1f}초)")
            success_count += 1
            
            # 실제 업데이트는 하지 않고 결과만 출력
            print(f"  → 업데이트 예정: pangyo_callno = '{callno}'")
        else:
            print(f"❌ 찾지 못함 ({elapsed:.1f}초)")
            not_found_count += 1
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 오류: {e} ({elapsed:.1f}초)")
        fail_count += 1
    
    print()
    
    # 요청 간 딜레이 (웹사이트 부하 방지)
    if idx < len(test_items) - 1:  # 마지막 항목이 아니면
        time.sleep(3)

print()
print("=" * 60)
print("테스트 결과")
print("=" * 60)
print(f"총 테스트: {len(test_items)}개")
print(f"✅ 찾음: {success_count}개")
print(f"❌ 찾지 못함: {not_found_count}개")
print(f"⚠️  오류: {fail_count}개")
print("=" * 60)

