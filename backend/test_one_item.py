"""단일 항목으로 웹사이트 검색 테스트"""
from search_pangyo_website import search_callno_from_website
import time

print("=" * 60)
print("단일 항목 웹사이트 검색 테스트")
print("=" * 60)
print()

# CSV 첫 번째 항목
isbn = "9788936442484"
title = "거짓말이 가득"
child_id = 7669

print(f"ID: {child_id}")
print(f"제목: {title}")
print(f"ISBN: {isbn}")
print()
print("웹사이트 검색 중...")
print()

start_time = time.time()
try:
    callno = search_callno_from_website(isbn, title)
    elapsed = time.time() - start_time
    
    print(f"소요 시간: {elapsed:.1f}초")
    print()
    
    if callno and len(callno.strip()) > 0:
        print(f"✅ 청구기호 찾음: {callno}")
        print()
        print(f"업데이트 예정:")
        print(f"  childbook_items 테이블")
        print(f"  ID: {child_id}")
        print(f"  pangyo_callno: '{callno}'")
    else:
        print(f"❌ 청구기호 찾지 못함")
        print("  (웹사이트에서 해당 책을 찾지 못했거나 청구기호가 없을 수 있습니다)")
        
except Exception as e:
    elapsed = time.time() - start_time
    print(f"❌ 오류 발생: {e}")
    print(f"소요 시간: {elapsed:.1f}초")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

