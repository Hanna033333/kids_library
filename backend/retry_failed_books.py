#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
실패한 책들 재검색 - 출판사 제외 (제목 + 저자만)
"""

import sys
import io
import time
import re
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
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def search_pangyo_library_no_publisher(driver, title: str, author: str):
    """출판사 없이 제목과 저자만으로 검색"""
    try:
        # 검색 페이지 로드
        search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
        driver.get(search_url)
        
        # 페이지 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchKeyword1"))
        )
        
        # 검색 폼 작성 (출판사 제외)
        driver.find_element(By.ID, "searchKeyword1").send_keys(title)
        if author:
            driver.find_element(By.ID, "searchKeyword2").send_keys(author)
        
        # 판교도서관 선택
        driver.find_element(By.ID, "searchLibrary").send_keys("판교도서관")
        
        # 검색 버튼 클릭
        driver.find_element(By.ID, "searchBtn").click()
        
        # 결과 로드 대기
        time.sleep(2)
        
        # 검색 결과 확인
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
        print(f"      검색 오류: {e}")
        return None


def retry_failed_books():
    """실패한 책들 재검색"""
    print("\n" + "="*80)
    print("📚 실패한 책 재검색 (출판사 제외)")
    print("="*80 + "\n")
    
    # 처음 50권 중 web_scraped_callno가 NULL인 책 조회
    response = supabase.table("childbook_items").select(
        "id, title, author, publisher"
    ).limit(50).execute()
    
    all_books = response.data
    
    # web_scraped_callno 확인
    response2 = supabase.table("childbook_items").select(
        "id, web_scraped_callno"
    ).limit(50).execute()
    
    callno_map = {book['id']: book.get('web_scraped_callno') for book in response2.data}
    
    # 실패한 책만 필터링
    failed_books = [book for book in all_books if not callno_map.get(book['id'])]
    
    print(f"재검색 대상: {len(failed_books)}권\n")
    
    # Chrome 드라이버 설정
    print("🌐 Chrome 드라이버 초기화 중...")
    driver = setup_driver()
    
    stats = {
        "total": len(failed_books),
        "found": 0,
        "not_found": 0,
        "updated": 0,
        "errors": 0
    }
    
    try:
        for i, book in enumerate(failed_books, 1):
            book_id = book['id']
            title = book.get('title', '')
            author = book.get('author', '')
            
            if not title:
                print(f"[{i}/{len(failed_books)}] ⚠️  제목 없음 - ID: {book_id}")
                continue
            
            print(f"[{i}/{len(failed_books)}] 🔍 재검색: {title[:30]}...")
            print(f"   저자: {author[:30] if author else '없음'}")
            
            # 판교 도서관 검색 (출판사 제외)
            callno = search_pangyo_library_no_publisher(driver, title, author or '')
            
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
            
            print()
    
    finally:
        driver.quit()
        print("🌐 Chrome 드라이버 종료\n")
    
    return stats


def main():
    """메인 실행 함수"""
    stats = retry_failed_books()
    
    # 결과 출력
    print("="*80)
    print("📊 재검색 결과")
    print("="*80)
    print(f"  - 재검색 대상: {stats['total']}권")
    print(f"  - 청구기호 발견: {stats['found']}권")
    print(f"  - 청구기호 미발견: {stats['not_found']}권")
    print(f"  - DB 업데이트: {stats['updated']}권")
    print(f"  - 오류: {stats['errors']}건")
    
    if stats['found'] > 0:
        success_rate = (stats['found'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  - 성공률: {success_rate:.1f}%")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
