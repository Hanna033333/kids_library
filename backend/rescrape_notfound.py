#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotFound 책들 재스크래핑
"""

import sys
import time
import re
from datetime import datetime
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from supabase_client import supabase


def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def search_pangyo_library_selenium(driver, title: str, author: str, publisher: str) -> Optional[str]:
    """Selenium을 사용하여 판교 도서관 검색 (다단계 + 여러 결과 확인)"""
    
    # 다단계 검색 시도
    search_attempts = [
        ("제목+저자+출판사", title, author, publisher),
        ("제목+저자", title, author, ""),
        ("제목만", title, "", "")
    ]
    
    for attempt_name, search_title, search_author, search_publisher in search_attempts:
        try:
            search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
            driver.get(search_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchKeyword1"))
            )
            
            driver.find_element(By.ID, "searchKeyword1").send_keys(search_title)
            if search_author:
                driver.find_element(By.ID, "searchKeyword2").send_keys(search_author)
            if search_publisher:
                driver.find_element(By.ID, "searchKeyword3").send_keys(search_publisher)
            
            driver.find_element(By.ID, "searchLibrary").send_keys("판교도서관")
            driver.find_element(By.ID, "searchBtn").click()
            
            time.sleep(2)
            
            try:
                result_list = driver.find_elements(By.CSS_SELECTOR, "ul.resultList li")
                
                if not result_list:
                    continue  # 다음 검색 시도
                
                # 여러 결과 확인 (최대 3개)
                for idx, result in enumerate(result_list[:3], 1):
                    author_dds = result.find_elements(By.CSS_SELECTOR, "dd.author")
                    
                    for dd in author_dds:
                        text = dd.text
                        if '청구기호' in text:
                            match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
                            if match:
                                callno = match.group(1).strip()
                                print(f"      [{attempt_name}] {idx}번째 결과에서 발견")
                                return callno
                    
                    # dd.author에서 못 찾으면 전체 텍스트에서 찾기
                    all_text = result.text
                    match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', all_text)
                    if match:
                        callno = match.group(1).strip()
                        print(f"      [{attempt_name}] {idx}번째 결과에서 발견")
                        return callno
                
            except Exception as e:
                print(f"      결과 파싱 오류 ({attempt_name}): {e}")
                continue
                
        except Exception as e:
            print(f"      검색 오류 ({attempt_name}): {e}")
            continue
    
    # 모든 시도 실패
    return None


def rescrape_notfound():
    """NotFound 책들 재스크래핑"""
    print("\n📊 NotFound 책 재스크래핑 시작...\n")
    
    # NotFound 책들 조회
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher"
    ).eq("web_scraped_callno", "NotFound").execute()
    
    books = response.data
    
    print(f"✅ 재스크래핑 대상: {len(books)}권\n")
    
    if not books:
        print("⚠️  재스크래핑할 책이 없습니다.")
        return
    
    print("🌐 Chrome 드라이버 초기화 중...", flush=True)
    driver = setup_driver()
    
    stats = {
        "total": len(books),
        "searched": 0,
        "found": 0,
        "still_not_found": 0,
        "updated": 0,
        "errors": 0
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"rescrape_log_{timestamp}.txt"
    
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            log_file.write(f"=== NotFound 재스크래핑 로그 ===\n")
            log_file.write(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"처리 대상: {len(books)}권\n\n")
            
            for i, book in enumerate(books, 1):
                book_id = book['id']
                title = book.get('title', '')
                author = book.get('author', '')
                publisher = book.get('publisher', '')
                
                if not title:
                    continue
                
                print(f"[{i}/{len(books)}] 🔍 검색 중: {title[:30]}...")
                
                callno = search_pangyo_library_selenium(driver, title, author or '', publisher or '')
                stats["searched"] += 1
                
                if callno:
                    stats["found"] += 1
                    print(f"   ✅ 청구기호 발견: {callno}")
                    log_file.write(f"[{i}] {title} -> {callno}\n")
                    
                    try:
                        supabase.table("childbook_items").update({
                            "web_scraped_callno": callno
                        }).eq("id", book_id).execute()
                        
                        stats["updated"] += 1
                        print(f"   💾 DB 업데이트 완료")
                        
                    except Exception as e:
                        print(f"   ❌ DB 업데이트 오류: {e}")
                        log_file.write(f"   ERROR: {e}\n")
                        stats["errors"] += 1
                else:
                    stats["still_not_found"] += 1
                    print(f"   ⚠️  여전히 없음")
                    log_file.write(f"[{i}] {title} -> STILL NOT FOUND\n")
                
                if i % 50 == 0:
                    progress_msg = f"\n--- 진행률: {i}/{len(books)} ({i*100//len(books)}%) ---"
                    detail_msg = f"    새로 발견: {stats['found']}권 | 여전히 없음: {stats['still_not_found']}권\n"
                    print(progress_msg)
                    print(detail_msg)
                    log_file.write(f"\n{progress_msg}\n{detail_msg}\n")
                    log_file.flush()
                
                if i % 10 == 0:
                    time.sleep(3)
            
            log_file.write(f"\n\n=== 최종 결과 ===\n")
            log_file.write(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"총 책 수: {stats['total']}권\n")
            log_file.write(f"검색 시도: {stats['searched']}권\n")
            log_file.write(f"새로 발견: {stats['found']}권\n")
            log_file.write(f"여전히 없음: {stats['still_not_found']}권\n")
            log_file.write(f"DB 업데이트: {stats['updated']}권\n")
            log_file.write(f"오류: {stats['errors']}건\n")
    
    finally:
        driver.quit()
        print("\n🌐 Chrome 드라이버 종료")
    
    return stats, log_filename


def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("📚 NotFound 책 재스크래핑")
    print("="*80 + "\n")
    
    stats, log_filename = rescrape_notfound()
    
    print("\n" + "="*80)
    print("📊 최종 결과")
    print("="*80)
    print(f"  - 총 책 수: {stats['total']}권")
    print(f"  - 검색 시도: {stats['searched']}권")
    print(f"  - 새로 발견: {stats['found']}권")
    print(f"  - 여전히 없음: {stats['still_not_found']}권")
    print(f"  - DB 업데이트: {stats['updated']}권")
    print(f"  - 오류: {stats['errors']}건")
    
    print(f"\n📝 로그 파일: {log_filename}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
