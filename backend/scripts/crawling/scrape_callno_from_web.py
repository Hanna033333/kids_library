#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Selenium을 사용한 다중 도서관 청구기호 스크래핑
지원 도서관: 판교도서관, 송파어린이도서관
"""

import sys
import io
import time
import re
import argparse
from typing import Optional, Dict, Any, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from supabase_client import supabase

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def search_pangyo_library(driver, title: str, author: str, publisher: str) -> Optional[str]:
    """
    [판교도서관] 검색 및 청구기호 추출
    URL: https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do
    """
    try:
        search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
        driver.get(search_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchKeyword1"))
        )
        
        driver.find_element(By.ID, "searchKeyword1").send_keys(title)
        if author:
            driver.find_element(By.ID, "searchKeyword2").send_keys(author)
        
        driver.find_element(By.ID, "searchLibrary").send_keys("판교도서관")
        driver.find_element(By.ID, "searchBtn").click()
        
        time.sleep(2)
        
        result_list = driver.find_elements(By.CSS_SELECTOR, "ul.resultList li")
        if not result_list:
            return None
        
        first_result = result_list[0]
        all_text = first_result.text
        
        # 청구기호 추출 (다양한 형식이 있을 수 있음)
        # 예: 청구기호 : 813.8-김12ㄱ
        match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', all_text)
        if match:
            return match.group(1).strip()
            
        return None
            
    except Exception as e:
        print(f"      [판교] 검색 오류: {e}")
        return None


def search_songpa_library(driver, title: str, author: str, publisher: str) -> Optional[str]:
    """
    [송파어린이도서관] 검색 및 청구기호 추출
    URL: https://www.splib.or.kr/spclib/index.do
    """
    try:
        search_url = "https://www.splib.or.kr/spclib/index.do"
        driver.get(search_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainSearchKeyword"))
        )
        
        driver.find_element(By.ID, "mainSearchKeyword").send_keys(title)
        driver.find_element(By.ID, "mainSearchBtn").click()
        
        time.sleep(3) # 결과 로딩 대기
        
        # 결과 리스트 확인
        results = driver.find_elements(By.CSS_SELECTOR, "ul.listWrap > li")
        if not results:
            return None
            
        # 송파어린이도서관 책인지 확인하면서 청구기호 찾기
        for item in results:
            try:
                # 도서관 이름 확인
                lib_name_el = item.find_elements(By.CSS_SELECTOR, ".bookData .book_info.info03 span:first-child")
                if not lib_name_el:
                    continue
                
                lib_name = lib_name_el[0].text
                if "송파어린이" not in lib_name:
                    continue
                
                # 청구기호 찾기
                # 구조: .bookData .book_info.info02 span (마지막 것이 보통 청구기호)
                info_spans = item.find_elements(By.CSS_SELECTOR, ".bookData .book_info.info02 span")
                if info_spans:
                    callno_text = info_spans[-1].text
                    # "아기방 833.8-하63ㄷ" 같은 형태일 수 있음. 숫자 시작 부분부터 추출하거나 그대로 사용
                    # 보통 "800..." 처럼 분류기호가 있으므로 이를 정규식으로 다듬기
                    # 예: 833.8-하63ㄷ -> 그대로 반환하거나 앞의 위치정보 제거
                    # 여기서는 전체 텍스트 반환 후 정규식으로 조금 다듬음
                    
                    # 1. "아기방 " 등 제거하고 순수 청구기호만 (숫자로 시작하는 부분 찾기)
                    # 정규식: 숫자로 시작하고 . - 등이 포함된 문자열
                    match = re.search(r'([0-9].*)', callno_text)
                    if match:
                        return match.group(1).strip()
                    return callno_text.strip()
            except Exception:
                continue
        
        return None
            
    except Exception as e:
        print(f"      [송파] 검색 오류: {e}")
        return None


# 도서관별 검색 함수 매핑
LIBRARY_SEARCH_FUNCS: Dict[str, Callable] = {
    "판교도서관": search_pangyo_library,
    "송파어린이도서관": search_songpa_library
}


def scrape_callnos_selenium(library_name: str, limit: int = 50):
    """
    Selenium을 사용하여 청구기호 스크래핑 및 저장
    """
    if library_name not in LIBRARY_SEARCH_FUNCS:
        print(f"❌ 지원하지 않는 도서관입니다: {library_name}")
        print(f"지원 목록: {', '.join(LIBRARY_SEARCH_FUNCS.keys())}")
        return

    search_func = LIBRARY_SEARCH_FUNCS[library_name]
    
    print(f"\n📊 [{library_name}] DB에서 대상 도서 조회 중 (LIMIT: {limit})...")
    
    # 1. 이미 이 도서관의 청구기호가 있는 책은 제외하고 가져오면 좋겠지만,
    #    일단은 간단하게 childbook_items에서 가져와서 book_library_info에 있는지 체크하는 방식 사용
    #    (최적화 여지 있음)
    
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher, isbn"
    ).limit(limit).execute()
    
    books = response.data
    print(f"✅ 대상 도서 {len(books)}권 조회 완료\n")
    
    print("🌐 Chrome 드라이버 초기화 중...")
    driver = setup_driver()
    
    stats = {
        "total": len(books),
        "searched": 0,
        "found": 0,
        "not_found": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0
    }
    
    try:
        for i, book in enumerate(books, 1):
            book_id = book['id']
            title = book.get('title', '')
            author = book.get('author', '')
            publisher = book.get('publisher', '')
            
            if not title:
                print(f"[{i}/{len(books)}] ⚠️  제목 없음 - ID: {book_id}")
                continue

            # 이미 데이터가 있는지 확인 (선택 사항: 덮어쓰기 여부)
            # 여기서는 upsert를 할 것이므로 굳이 확인 안 해도 되지만, 불필요한 검색을 줄이려면 체크 권장
            # check_res = supabase.table("book_library_info").select("id").eq("book_id", book_id).eq("library_name", library_name).execute()
            # if check_res.data:
            #     print(f"[{i}/{len(books)}] ⏭️  이미 존재함: {title[:20]}...")
            #     stats["skipped"] += 1
            #     continue

            print(f"[{i}/{len(books)}] 🔍 검색 중: {title[:20]}...")
            stats["searched"] += 1
            
            # 도서관별 검색 실행
            callno = search_func(driver, title, author or '', publisher or '')
            
            if callno:
                stats["found"] += 1
                print(f"   ✅ 발견: {callno}")
                
                try:
                    # book_library_info 테이블에 저장 (UPSERT)
                    # unique constraint(book_id, library_name) 필요
                    data = {
                        "book_id": book_id,
                        "library_name": library_name,
                        "callno": callno,
                        "updated_at": "now()"
                    }
                    
                    supabase.table("book_library_info").upsert(data, on_conflict="book_id, library_name").execute()
                    
                    stats["updated"] += 1
                    
                except Exception as e:
                    print(f"   ❌ DB 저장 오류: {e}")
                    stats["errors"] += 1
            else:
                stats["not_found"] += 1
                print(f"   ⚠️  없음")
            
            # 진행률 표시
            if i % 10 == 0:
                print(f"\n--- 진행률: {i}/{len(books)} ({i*100//len(books)}%) ---")
                
    finally:
        driver.quit()
        print("\n🌐 Chrome 드라이버 종료")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="도서관 청구기호 스크래핑")
    parser.add_argument("--library", type=str, default="판교도서관", help="대상 도서관 이름 (예: 송파어린이도서관)")
    parser.add_argument("--limit", type=int, default=50, help="스크래핑할 책 수")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(f"📚 도서관 청구기호 스크래핑: {args.library}")
    print("="*80)
    
    stats = scrape_callnos_selenium(args.library, args.limit)
    
    if stats:
        print("\n" + "="*80)
        print("📊 최종 결과")
        print("="*80)
        print(f"  - 대상 도서관: {args.library}")
        print(f"  - 총 책 수: {stats['total']}권")
        print(f"  - 검색 시도: {stats['searched']}권")
        print(f"  - 발견: {stats['found']}권")
        print(f"  - 미발견: {stats['not_found']}권")
        print(f"  - DB 저장: {stats['updated']}권")
        print(f"  - 오류: {stats['errors']}건")
        
        if stats['searched'] > 0:
            success_rate = (stats['found'] / stats['searched'] * 100)
            print(f"  - 성공률: {success_rate:.1f}%")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
