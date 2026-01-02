#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
업데이트 실패한 책 확인 (파일 저장)
"""

from supabase_client import supabase

# 처음 50권 중 web_scraped_callno가 NULL인 책 조회
response = supabase.table("childbook_items").select(
    "id, title, author, publisher, pangyo_callno, web_scraped_callno"
).limit(50).execute()

all_books = response.data

# 업데이트 실패한 책
failed_books = [book for book in all_books if not book.get('web_scraped_callno')]

with open("failed_books_list.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("업데이트 실패한 책 목록\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"총 조회: {len(all_books)}권\n")
    f.write(f"업데이트 성공: {len(all_books) - len(failed_books)}권\n")
    f.write(f"업데이트 실패: {len(failed_books)}권\n\n")
    
    f.write("="*80 + "\n")
    f.write("실패한 책 상세 정보\n")
    f.write("="*80 + "\n\n")
    
    for i, book in enumerate(failed_books, 1):
        f.write(f"{i}. [{book['id']}] {book['title']}\n")
        f.write(f"   저자: {book.get('author', '없음')}\n")
        f.write(f"   출판사: {book.get('publisher', '없음')}\n")
        f.write(f"   기존 청구기호: {book.get('pangyo_callno', '없음')}\n\n")
    
    f.write("="*80 + "\n")

print(f"결과 저장 완료: failed_books_list.txt")
print(f"업데이트 실패: {len(failed_books)}권")
