#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
웹 스크래핑 청구기호와 기존 청구기호 비교
"""

from supabase_client import supabase

print("="*80)
print("청구기호 비교 분석")
print("="*80)

# web_scraped_callno가 있는 책들 조회
response = supabase.table("childbook_items").select(
    "id, title, author, pangyo_callno, web_scraped_callno"
).not_.is_("web_scraped_callno", "null").limit(50).execute()

books = response.data

print(f"\n총 조회: {len(books)}권 (웹 스크래핑 성공)\n")

# 청구기호 비교
same_count = 0
different_count = 0
different_books = []

for book in books:
    original = book.get('pangyo_callno', '').strip()
    scraped = book.get('web_scraped_callno', '').strip()
    
    if original and scraped:
        if original == scraped:
            same_count += 1
        else:
            different_count += 1
            different_books.append(book)

print("="*80)
print("비교 결과")
print("="*80)
print(f"  - 동일: {same_count}권")
print(f"  - 다름: {different_count}권")
print(f"  - 기존 청구기호 없음: {len(books) - same_count - different_count}권")
print()

if different_books:
    print("="*80)
    print("청구기호가 다른 책 목록")
    print("="*80)
    
    for i, book in enumerate(different_books, 1):
        print(f"\n{i}. [{book['id']}] {book['title'][:50]}")
        print(f"   저자: {book.get('author', '없음')[:40]}")
        print(f"   기존 청구기호: {book.get('pangyo_callno', '없음')}")
        print(f"   웹 스크래핑:   {book.get('web_scraped_callno', '없음')}")

print("\n" + "="*80)

# 파일로도 저장
with open("callno_comparison.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("청구기호 비교 분석\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"총 조회: {len(books)}권\n")
    f.write(f"동일: {same_count}권\n")
    f.write(f"다름: {different_count}권\n")
    f.write(f"기존 청구기호 없음: {len(books) - same_count - different_count}권\n\n")
    
    if different_books:
        f.write("="*80 + "\n")
        f.write("청구기호가 다른 책 목록\n")
        f.write("="*80 + "\n\n")
        
        for i, book in enumerate(different_books, 1):
            f.write(f"{i}. [{book['id']}] {book['title']}\n")
            f.write(f"   저자: {book.get('author', '없음')}\n")
            f.write(f"   기존 청구기호: {book.get('pangyo_callno', '없음')}\n")
            f.write(f"   웹 스크래핑:   {book.get('web_scraped_callno', '없음')}\n\n")

print("결과 저장: callno_comparison.txt")
