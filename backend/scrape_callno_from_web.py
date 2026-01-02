#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Selenium을 사용한 판교 도서관 청구기호 스크래핑
"""

import sys
import io
import time
import re
from typing import Optional
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


def scrape_callnos_selenium(limit: int = 50):
    """
    Selenium을 사용하여 청구기호 스크래핑
    
    Args:
        limit: 처리할 책 수
    """
    print("\n📊 DB에서 책 정보 조회 중...")
    
    # DB에서 책 조회
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher, pangyo_callno"
    ).limit(limit).execute()
    
    books = response.data
    
    print(f"✅ DB에서 {len(books)}권 조회 완료\n")
    
    # Chrome 드라이버 설정
    print("🌐 Chrome 드라이버 초기화 중...")
    driver = setup_driver()
    
    stats = {
        "total": len(books),
        "searched": 0,
        "found": 0,
        "not_found": 0,
        "updated": 0,
        "errors": 0
    }
    
    try:
        # 각 책에 대해 검색
        for i, book in enumerate(books, 1):
            book_id = book['id']
            title = book.get('title', '')
            author = book.get('author', '')
            publisher = book.get('publisher', '')
            
            if not title:
                print(f"[{i}/{len(books)}] ⚠️  제목 없음 - ID: {book_id}")
                continue
            
            print(f"[{i}/{len(books)}] 🔍 검색 중: {title[:30]}...")
            
            # 판교 도서관 검색
            callno = search_pangyo_library_selenium(driver, title, author or '', publisher or '')
            stats["searched"] += 1
            
            if callno:
                stats["found"] += 1
                print(f"   ✅ 청구기호 발견: {callno}")
                
                # DB 업데이트
                try:
                    supabase.table("childbook_items").update({
                        "web_scraped_callno": callno
                    }).eq("id", book_id).execute()
                    
                    stats["updated"] += 1
                    print(f"   💾 DB 업데이트 완료")
                    
                except Exception as e:
                    print(f"   ❌ DB 업데이트 오류: {e}")
                    stats["errors"] += 1
            else:
                stats["not_found"] += 1
                print(f"   ⚠️  청구기호 없음")
            
            # 진행 상황 출력 (10개마다)
            if i % 10 == 0:
                print(f"\n--- 진행률: {i}/{len(books)} ({i*100//len(books)}%) ---")
                print(f"    발견: {stats['found']}권 | 미발견: {stats['not_found']}권 | 업데이트: {stats['updated']}권\n")
    
    finally:
        # 드라이버 종료
        driver.quit()
        print("\n🌐 Chrome 드라이버 종료")
    
    return stats


def check_column_exists() -> bool:
    """web_scraped_callno 컬럼 존재 여부 확인"""
    print("\n🔧 web_scraped_callno 컬럼 확인 중...")
    
    try:
        response = supabase.table("childbook_items").select("web_scraped_callno").limit(1).execute()
        print("✅ web_scraped_callno 컬럼이 존재합니다.\n")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'column' in error_msg or 'does not exist' in error_msg:
            print(f"❌ web_scraped_callno 컬럼이 없습니다.")
            print("\n" + "="*80)
            print("📝 다음 SQL을 Supabase SQL Editor에서 실행해주세요:")
            print("="*80)
            print("ALTER TABLE childbook_items ADD COLUMN IF NOT EXISTS web_scraped_callno TEXT;")
            print("="*80 + "\n")
            return False
        else:
            print(f"⚠️  확인 중 오류: {e}")
            print("계속 진행을 시도합니다...\n")
            return True


def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("📚 판교 도서관 청구기호 스크래핑 (Selenium)")
    print("="*80 + "\n")
    
    # 컬럼 확인
    if not check_column_exists():
        print("\n⚠️  먼저 web_scraped_callno 컬럼을 추가해주세요.")
        return
    
    # 스크래핑 시작
    print("🔍 판교 도서관 검색 시작...\n")
    stats = scrape_callnos_selenium(limit=50)
    
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
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
