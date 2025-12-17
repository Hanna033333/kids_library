#!/usr/bin/env python
"""
중복된 청구기호를 가진 책들에 권차정보 추가 (최종 수정판)
Data Library API의 libSrchByBook API (도서관별 장서 소장 확인) 사용
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from collections import defaultdict
from supabase_client import supabase
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

async def fetch_volume_info(session: aiohttp.ClientSession, isbn: str) -> Optional[Dict]:
    # 판교 도서관 장서 검색 API
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "ISBN",  # ISBN검색이 가장 정확함
        "keyword": isbn,
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    for attempt in range(3): # 3번 재시도
        try:
            # 타임아웃을 30초로 대폭 늘림
            async with session.get(url, params=params, timeout=30) as response:
                if response.status != 200:
                    continue
                    
                data = await response.json()
                
                # 응답 파싱
                response_data = data.get("response", {})
                docs = response_data.get("docs", [])
                
                # 권차정보 수집
                volumes = []
                for doc_wrapper in docs:
                    doc = doc_wrapper.get("doc", {})
                    # 검색한 ISBN과 일치하는지 확인 (선택 사항)
                    # if doc.get("isbn13") != isbn: continue 
                    
                    vol = doc.get("vol", "")
                    class_no = doc.get("class_no", "")
                    
                    if vol:
                        volumes.append({
                            "vol": vol.strip(),
                            "class_no": class_no
                        })
                
                if volumes:
                     return {
                        "isbn": isbn,
                        "found": True,
                        "volumes": volumes
                    }
                else:
                    # 검색은 성공했으나 결과가 없는 경우
                    return {
                        "isbn": isbn,
                        "found": False,
                        "volumes": []
                    }
                    
        except Exception as e:
            print(f"  ⚠️ 시도 {attempt+1} 실패 ({isbn}): {e}")
            await asyncio.sleep(2) # 재시도 전 대기
            
    return None

async def fetch_volumes_batch(books: List[Dict]) -> Dict[str, Dict]:
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY가 설정되지 않았습니다.")
        return {}
    
    print(f"📚 {len(books)}개의 책에 대해 권차정보 조회 중... (순차 처리)")
    
    all_results = {}
    async with aiohttp.ClientSession() as session:
        for i, book in enumerate(books):
            isbn = book['isbn']
            print(f"  📖 [{i+1}/{len(books)}] 조회: {book['title'][:20]}... ({isbn})")
            
            result = await fetch_volume_info(session, isbn)
            if result:
                all_results[isbn] = result
                # 결과가 있으면 로그 출력
                vols = result.get("volumes", [])
                if vols:
                    print(f"     ✨ 발견: vol '{vols[0]['vol']}'")
                else:
                    print(f"     💨 데이터 없음")
            else:
                print(f"     ❌ 조회 실패")
                
            # API 부하 방지를 위해 1초 대기
            await asyncio.sleep(1.0)
            
    return all_results


def find_duplicate_callnos():
    """
    중복된 청구기호를 가진 책들 찾기
    """
    print("🔍 중복된 청구기호 검색 중...")
    
    # 모든 childbook_items 조회
    response = supabase.table("childbook_items").select("id, isbn, title, pangyo_callno").execute()
    books = response.data
    
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip():
            callno_groups[callno].append(book)
    
    duplicates = {
        callno: books_list 
        for callno, books_list in callno_groups.items() 
        if len(books_list) > 1
    }
    
    print(f"✅ {len(duplicates)}개의 중복된 청구기호 발견")
    return duplicates


async def add_volume_info_to_duplicates():
    log_file = open("update_log.txt", "w", encoding="utf-8")
    def log(msg):
        print(msg)
        log_file.write(msg + "\n")
        
    log("\n" + "="*60)
    log("📚 중복 청구기호 책들에 권차정보 추가 (libSrchByBook 방식)")
    log("="*60 + "\n")
    
    duplicates = find_duplicate_callnos()
    
    if not duplicates:
        print("✅ 중복된 청구기호가 없습니다.")
        return
    
    books_to_check = []
    for callno, books_list in duplicates.items():
        for book in books_list:
            if book.get("isbn"):
                books_to_check.append(book)
    
    # 중복 제거 (같은 ISBN이 여러 번 있을 수 있음)
    unique_books_to_check = []
    seen_isbns = set()
    for book in books_to_check:
        if book['isbn'] not in seen_isbns:
            unique_books_to_check.append(book)
            seen_isbns.add(book['isbn'])
            
    print(f"\n📊 총 {len(unique_books_to_check)}개의 고유 ISBN 조회 예정\n")
    
    results = await fetch_volumes_batch(unique_books_to_check)
    
    print(f"\n🔄 데이터베이스 업데이트 시작...\n")
    updated_count = 0
    
    # 청구기호 그룹별로 처리
    for callno, books_list in duplicates.items():
        log(f"📂 청구기호: {callno}")
        
        # 권차정보 매핑
        book_vol_map = []
        for book in books_list:
            isbn = book.get("isbn")
            title = book.get("title")
            res = results.get(isbn)
            
            vol_str = "미발견"
            if res:
                if res.get("found"):
                    vols = res.get("volumes", [])
                    if vols:
                        # 첫 번째 volume 정보 사용 (보통 일치)
                        vol_str = vols[0].get("vol") or "공란"
                    else:
                        vol_str = "권차없음"
                else:
                    vol_str = "도서관미소장"
            
            book_vol_map.append({
                "book": book,
                "vol": vol_str if vol_str not in ["미발견", "공란", "권차없음", "도서관미소장"] else None,
                "status": vol_str
            })
            
            # API에서 가져온 class_no 확인
            api_class_no = ""
            if res and res.get("found"):
                vols = res.get("volumes", [])
                if vols:
                    api_class_no = vols[0].get("class_no", "")

            log(f"   - {title[:20]}... (ISBN:{isbn}) -> Vol:{vol_str}, API_CallNo:{api_class_no}")

        # 유효한 권차정보가 있으면 업데이트
        for item in book_vol_map:
            # Here we could add logic to parse volume from api_class_no if needed
            if item["vol"]:
                try:
                    supabase.table("childbook_items").update({"vol": item["vol"]}).eq("id", item["book"]["id"]).execute()
                    log(f"     ✅ 업데이트: ID {item['book']['id']} -> vol '{item['vol']}'")
                    updated_count += 1
                except Exception as e:
                    log(f"     ❌ 업데이트 실패: {e}")
        log("-" * 40)

    log(f"\n" + "="*60)
    log(f"✅ 총 {updated_count}권 업데이트 완료")
    log("="*60)
    log_file.close()

if __name__ == "__main__":
    asyncio.run(add_volume_info_to_duplicates())
