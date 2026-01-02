#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
전체 레코드 청구기호 스크래핑 테스트 (간단 버전)
"""

import sys
import io
from supabase_client import supabase

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("스크립트 시작...")

# DB 연결 테스트
print("\n📊 DB에서 책 정보 조회 중...")

try:
    # 전체 레코드 조회 (web_scraped_callno가 NULL인 것만)
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher, web_scraped_callno"
    ).is_("web_scraped_callno", "null").execute()
    
    all_books = response.data
    
    print(f"✅ 전체 조회 완료: {len(all_books)}권")
    
    # 처음 50개 제외
    books = all_books[50:] if len(all_books) > 50 else []
    
    print(f"✅ 처리 대상: {len(books)}권 (처음 50권 제외)")
    
    # 처음 5개만 출력
    print("\n처리 대상 책 (처음 5개):")
    for i, book in enumerate(books[:5], 1):
        print(f"  {i}. {book.get('title', 'N/A')}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n테스트 완료!")
