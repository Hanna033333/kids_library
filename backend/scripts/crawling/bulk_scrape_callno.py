#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
전체 레코드 청구기호 스크래핑 (테스트 50개 제외)
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
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def search_pangyo_library_selenium(driver, title: str, author: str, publisher: str) -> Optional[str]:
    """
    Selenium을 사용하여 판교 도서관 검색
    
    Args:
        driver: Selenium WebDriver
        title: 책 제목
        author: 저자
        publisher: 출판사
    
    Returns:
        청구기호 (찾지 못하면 None)
    """
    try:
        # 검색 페이지 로드
        search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
        driver.get(search_url)
        
        # 페이지 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchKeyword1"))
        )
        
        # 검색 폼 작성
        driver.find_element(By.ID, "searchKeyword1").send_keys(title)
        if author:
            driver.find_element(By.ID, "searchKeyword2").send_keys(author)
        if publisher:
            driver.find_element(By.ID, "searchKeyword3").send_keys(publisher)
        
        # 판교도서관 선택
        driver.find_element(By.ID, "searchLibrary").send_keys("판교도서관")
        
        # 검색 버튼 클릭
        driver.find_element(By.ID, "searchBtn").click()
        
        # 결과 로드 대기
        time.sleep(2)
        
        # 검색 결과 확인
        try:
            result_list = driver.find_elements(By.CSS_SELECTOR, "ul.resultList li")
            
            if not result_list:
                return None
            
            # 첫 번째 결과에서 청구기호 추출
            first_result = result_list[0]
            
            # dd.author 요소들 찾기
            author_dds = first_result.find_elements(By.CSS_SELECTOR, "dd.author")
            
            for dd in author_dds:
                text = dd.text
                
                if '청구기호' in text:
                    # 청구기호 추출
                    match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
                    if match:
                        return match.group(1).strip()
            
            # 전체 텍스트에서 찾기
            all_text = first_result.text
            match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', all_text)
            if match:
                return match.group(1).strip()
            
            return None
            
        except Exception as e:
            print(f"      결과 파싱 오류: {e}")
            return None
            
    except Exception as e:
        print(f"      검색 오류: {e}")
        return None


def bulk_scrape_callnos():
    """
    전체 레코드 청구기호 스크래핑 (테스트 50개 제외)
    """
    print("\n📊 DB에서 책 정보 조회 중...")
    
    # 전체 레코드 조회 (web_scraped_callno가 NULL인 것만)
    # 처음 50개는 이미 테스트했으므로 offset 50부터 시작
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher, web_scraped_callno"
    ).is_("web_scraped_callno", "null").execute()
    
    all_books = response.data
    
    all_books = response.data
    
    # Process all books found (since we query for NULL)
    books = all_books
    
    print(f"✅ 전체 {len(all_books)}권 중 처리 대상: {len(books)}권")
    # print(f"   (처음 50권은 이미 테스트 완료)\n")
    
    if not books:
        print("⚠️  처리할 책이 없습니다.")
        return
    
    # Chrome 드라이버 설정
    print("🌐 Chrome 드라이버 초기화 중...", flush=True)
    driver = setup_driver()
    
    stats = {
        "total": len(books),
        "searched": 0,
        "found": 0,
        "not_found": 0,
        "updated": 0,
        "errors": 0
    }
    
    # 로그 파일 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"bulk_scrape_log_{timestamp}.txt"
    
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            log_file.write(f"=== 청구기호 스크래핑 로그 ===\n")
            log_file.write(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"처리 대상: {len(books)}권\n\n")
            
            # 각 책에 대해 검색
            for i, book in enumerate(books, 1):
                book_id = book['id']
                title = book.get('title', '')
                author = book.get('author', '')
                publisher = book.get('publisher', '')
                
                if not title:
                    msg = f"[{i}/{len(books)}] ⚠️  제목 없음 - ID: {book_id}"
                    print(msg)
                    log_file.write(msg + "\n")
                    continue
                
                print(f"[{i}/{len(books)}] 🔍 검색 중: {title[:30]}...")
                
                # 판교 도서관 검색
                callno = search_pangyo_library_selenium(driver, title, author or '', publisher or '')
                stats["searched"] += 1
                
                if callno:
                    stats["found"] += 1
                    msg = f"   ✅ 청구기호 발견: {callno}"
                    print(msg)
                    log_file.write(f"[{i}] {title} -> {callno}\n")
                    
                    # DB 업데이트
                    try:
                        supabase.table("childbook_items").update({
                            "web_scraped_callno": callno
                        }).eq("id", book_id).execute()
                        
                        stats["updated"] += 1
                        print(f"   💾 DB 업데이트 완료")
                        
                    except Exception as e:
                        error_msg = f"   ❌ DB 업데이트 오류: {e}"
                        print(error_msg)
                        log_file.write(f"   ERROR: {e}\n")
                        stats["errors"] += 1
                else:
                    stats["not_found"] += 1
                    msg = f"   ⚠️  청구기호 없음"
                    print(msg)
                    log_file.write(f"[{i}] {title} -> NOT FOUND\n")
                    
                    # DB 업데이트 (재시도 방지 위해 "NotFound"로 저장)
                    try:
                        supabase.table("childbook_items").update({
                            "web_scraped_callno": "NotFound"
                        }).eq("id", book_id).execute()
                        stats["updated"] += 1  # 처리된 것으로 간주
                    except Exception as e:
                        print(f"   ❌ DB 업데이트 오류 (NotFound): {e}")
                
                # 진행 상황 출력 (50개마다)
                if i % 50 == 0:
                    progress_msg = f"\n--- 진행률: {i}/{len(books)} ({i*100//len(books)}%) ---"
                    detail_msg = f"    발견: {stats['found']}권 | 미발견: {stats['not_found']}권 | 업데이트: {stats['updated']}권\n"
                    print(progress_msg)
                    print(detail_msg)
                    log_file.write(f"\n{progress_msg}\n{detail_msg}\n")
                    log_file.flush()  # 중간 저장
                
                # 서버 부하 방지를 위한 딜레이 (매 10개마다 3초 대기)
                if i % 10 == 0:
                    time.sleep(3)
            
            # 최종 결과 로그
            log_file.write(f"\n\n=== 최종 결과 ===\n")
            log_file.write(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"총 책 수: {stats['total']}권\n")
            log_file.write(f"검색 시도: {stats['searched']}권\n")
            log_file.write(f"청구기호 발견: {stats['found']}권\n")
            log_file.write(f"청구기호 미발견: {stats['not_found']}권\n")
            log_file.write(f"DB 업데이트: {stats['updated']}권\n")
            log_file.write(f"오류: {stats['errors']}건\n")
            if stats['searched'] > 0:
                success_rate = stats['found'] / stats['searched'] * 100
                log_file.write(f"성공률: {success_rate:.1f}%\n")
    
    finally:
        # 드라이버 종료
        driver.quit()
        print("\n🌐 Chrome 드라이버 종료")
    
    return stats, log_filename


def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("📚 전체 레코드 청구기호 스크래핑 (테스트 50개 제외)")
    print("="*80 + "\n")
    
    # 스크래핑 시작
    print("🔍 판교 도서관 검색 시작...\n")
    stats, log_filename = bulk_scrape_callnos()
    
    # 결과 출력
    print("\n" + "="*80)
    print("📊 최종 결과")
    print("="*80)
    print(f"  - 총 책 수: {stats['total']}권")
    print(f"  - 검색 시도: {stats['searched']}권")
    print(f"  - 청구기호 발견: {stats['found']}권")
    print(f"  - 청구기호 미발견: {stats['not_found']}권")
    print(f"  - DB 업데이트: {stats['updated']}권")
    print(f"  - 오류: {stats['errors']}건")
    
    if stats['found'] > 0:
        success_rate = (stats['found'] / stats['searched'] * 100) if stats['searched'] > 0 else 0
        print(f"  - 성공률: {success_rate:.1f}%")
    
    print(f"\n📝 로그 파일: {log_filename}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
