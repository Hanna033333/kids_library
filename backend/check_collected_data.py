"""
수집된 데이터 확인 및 분석
"""
from supabase_client import supabase
import json

print("=" * 60)
print("수집된 library_items 데이터 확인")
print("=" * 60)
print()

# 데이터 조회
result = supabase.table("library_items").select("*").limit(20).execute()

print(f"총 {len(result.data)}건 확인")
print()

for i, book in enumerate(result.data[:10], 1):
    print(f"{i}. {book.get('title', 'N/A')[:50]}")
    print(f"   callno: {book.get('callno', 'N/A')}")
    print(f"   ISBN: {book.get('isbn13', 'N/A')}")
    print()

# callno 패턴 분석
callno_patterns = {}
for book in result.data:
    callno = book.get('callno', '')
    if callno:
        if callno.startswith('아'):
            pattern = '아로 시작'
        elif callno.startswith('유'):
            pattern = '유로 시작'
        elif callno and callno[0].isdigit():
            pattern = '숫자로 시작'
        elif callno and callno[0].isalpha():
            pattern = '한글로 시작'
        else:
            pattern = '기타'
    else:
        pattern = '없음'
    
    callno_patterns[pattern] = callno_patterns.get(pattern, 0) + 1

print("\ncallno 패턴 분석:")
for pattern, count in callno_patterns.items():
    print(f"  {pattern}: {count}건")






