#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
업데이트 실패한 책 확인
"""

from supabase_client import supabase

print("="*80)
print("업데이트 실패한 책 확인")
print("="*80)

# 처음 50권 중 web_scraped_callno가 NULL인 책 조회
response = supabase.table("childbook_items").select(
    "id, title, author, publisher, pangyo_callno, web_scraped_callno"
).limit(50).execute()

all_books = response.data

# 업데이트 실패한 책 (web_scraped_callno가 NULL)
failed_books = [book for book in all_books if not book.get('web_scraped_callno')]

print(f"\n총 조회: {len(all_books)}권")
print(f"업데이트 성공: {len(all_books) - len(failed_books)}권")
print(f"업데이트 실패: {len(failed_books)}권\n")

print("="*80)
print("업데이트 실패한 책 목록")
print("="*80)

for i, book in enumerate(failed_books, 1):
    print(f"\n{i}. [{book['id']}] {book['title'][:50]}")
    print(f"   저자: {book.get('author', '없음')[:40]}")
    print(f"   출판사: {book.get('publisher', '없음')[:40]}")
    print(f"   기존 청구기호: {book.get('pangyo_callno', '없음')}")

print("\n" + "="*80)
