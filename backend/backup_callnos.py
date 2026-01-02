#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
현재 청구기호 데이터 백업 (CSV)
"""

import csv
from datetime import datetime
from supabase_client import supabase

print("="*80)
print("청구기호 데이터 백업")
print("="*80)

# 모든 책의 청구기호 조회
response = supabase.table("childbook_items").select(
    "id, title, author, publisher, pangyo_callno, web_scraped_callno"
).execute()

books = response.data

print(f"\n총 {len(books)}권 조회 완료")

# CSV 파일명 (타임스탬프 포함)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"callno_backup_{timestamp}.csv"

# CSV로 저장
with open(filename, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    
    # 헤더
    writer.writerow([
        "ID",
        "제목",
        "저자",
        "출판사",
        "기존_청구기호(pangyo_callno)",
        "웹스크래핑_청구기호(web_scraped_callno)",
        "백업_일시"
    ])
    
    # 데이터
    backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for book in books:
        writer.writerow([
            book.get('id'),
            book.get('title', ''),
            book.get('author', ''),
            book.get('publisher', ''),
            book.get('pangyo_callno', ''),
            book.get('web_scraped_callno', ''),
            backup_time
        ])

print(f"✅ 백업 완료: {filename}")
print(f"   - 총 {len(books)}권 저장됨")

# 통계
with_pangyo = sum(1 for b in books if b.get('pangyo_callno'))
with_web = sum(1 for b in books if b.get('web_scraped_callno'))

print(f"\n📊 통계:")
print(f"   - 기존 청구기호 있음: {with_pangyo}권")
print(f"   - 웹 스크래핑 청구기호 있음: {with_web}권")

print("\n" + "="*80)
