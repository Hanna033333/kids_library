#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
스크래핑 결과 확인
"""

from supabase_client import supabase

print("="*80)
print("스크래핑 결과 확인")
print("="*80)

# web_scraped_callno가 있는 책 조회
response = supabase.table("childbook_items").select(
    "id, title, pangyo_callno, web_scraped_callno"
).not_.is_("web_scraped_callno", "null").limit(20).execute()

books = response.data

print(f"\n청구기호가 업데이트된 책: {len(books)}권\n")

for i, book in enumerate(books, 1):
    print(f"{i}. {book['title'][:40]}")
    print(f"   기존 청구기호: {book.get('pangyo_callno', '없음')}")
    print(f"   웹 스크래핑: {book.get('web_scraped_callno', '없음')}")
    print()

# 전체 통계
total_response = supabase.table("childbook_items").select(
    "id, web_scraped_callno", count="exact"
).not_.is_("web_scraped_callno", "null").execute()

print("="*80)
print(f"전체 업데이트된 책: {total_response.count}권")
print("="*80)
