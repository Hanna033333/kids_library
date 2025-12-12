"""단일 항목으로 웹사이트 검색 테스트"""
from search_pangyo_website import search_callno_from_website
import time

print("테스트 시작...")
print()

# 첫 번째 항목 테스트
isbn = "9788936442484"
title = "거짓말이 가득"

print(f"검색: {title}")
print(f"ISBN: {isbn}")
print("웹사이트 검색 중... (시간이 걸릴 수 있습니다)")
print()

start_time = time.time()
callno = search_callno_from_website(isbn, title)
elapsed = time.time() - start_time

print(f"소요 시간: {elapsed:.1f}초")
if callno:
    print(f"✅ 청구기호 찾음: {callno}")
else:
    print(f"❌ 청구기호 찾지 못함")
