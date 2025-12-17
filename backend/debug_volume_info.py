#!/usr/bin/env python
"""
Debug: Check vol column and API response
"""

import asyncio
import aiohttp
from supabase_client import supabase
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

async def test_api():
    """API 테스트"""
    
    # 테스트 ISBN (중복된 청구기호의 첫 번째 책)
    test_isbn = "9791185934945"  # 문제아
    
    print(f"Testing API with ISBN: {test_isbn}")
    print(f"API Key exists: {bool(DATA4LIBRARY_KEY)}")
    
    url = "http://data4library.kr/api/libSrchByBook"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "isbn": test_isbn,
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as response:
            data = await response.json()
            
            print("\n=== API Response ===")
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 판교 도서관 데이터 찾기
            response_data = data.get("response", {})
            libs = response_data.get("libs", [])
            
            print(f"\n=== Libraries found: {len(libs) if isinstance(libs, list) else 1} ===")
            
            if isinstance(libs, list):
                for lib_data in libs:
                    lib = lib_data.get("lib", {})
                    lib_code = lib.get("libCode")
                    lib_name = lib.get("libName")
                    print(f"\n도서관: {lib_name} ({lib_code})")
                    
                    if lib_code == PANGYO_LIB_CODE:
                        print("  ✅ 판교 도서관 발견!")
                        books = lib_data.get("book", [])
                        if not isinstance(books, list):
                            books = [books] if books else []
                        
                        print(f"  책 개수: {len(books)}")
                        for book in books:
                            print(f"    - vol: {book.get('vol')}")
                            print(f"      callNo: {book.get('class_no')}")
                            print(f"      loanCnt: {book.get('loan_cnt')}")

def check_vol_column():
    """vol 컬럼 확인"""
    print("\n=== Checking vol column ===")
    try:
        result = supabase.table("childbook_items").select("id, vol").limit(1).execute()
        print("✅ vol 컬럼이 존재합니다!")
        print(f"Sample: {result.data}")
    except Exception as e:
        print(f"❌ vol 컬럼이 없거나 접근 불가: {e}")
        return False
    return True

if __name__ == "__main__":
    has_vol = check_vol_column()
    
    if has_vol:
        print("\n=== Testing API ===")
        asyncio.run(test_api())
    else:
        print("\n⚠️  먼저 vol 컬럼을 추가해야 합니다!")
        print("\nSupabase SQL Editor에서 다음을 실행하세요:")
        print("="*60)
        with open("migrations/007_add_vol_column.sql", "r", encoding="utf-8") as f:
            print(f.read())
        print("="*60)
