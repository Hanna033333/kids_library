#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 테스트: 컬럼 존재 확인
"""

from supabase_client import supabase

with open("column_test_result.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("Testing Supabase column...\n")
    f.write("="*80 + "\n\n")
    
    try:
        # 컬럼 존재 여부 확인
        response = supabase.table("childbook_items").select("web_scraped_callno").limit(1).execute()
        f.write("[SUCCESS] web_scraped_callno column exists!\n")
        f.write(f"Sample data: {response.data}\n")
        print("SUCCESS - Column exists!")
    except Exception as e:
        f.write(f"[ERROR] Column does not exist or other error:\n")
        f.write(f"Error: {e}\n\n")
        f.write("Please run this SQL in Supabase SQL Editor:\n")
        f.write("ALTER TABLE childbook_items ADD COLUMN IF NOT EXISTS web_scraped_callno TEXT;\n")
        print(f"ERROR - Column missing: {e}")
    
    f.write("\n" + "="*80 + "\n")

print("Results written to column_test_result.txt")
