#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Selenium 간단 테스트 - 1권만
"""

import sys
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*80)
print("Selenium 테스트 시작")
print("="*80)

# Chrome 옵션 설정
print("\n1. Chrome 드라이버 설정 중...")
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

try:
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Chrome 드라이버 초기화 완료")
    
    # 검색 페이지 접속
    print("\n2. 검색 페이지 접속 중...")
    search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
    driver.get(search_url)
    print("✅ 페이지 로드 완료")
    
    # 검색 폼 대기
    print("\n3. 검색 폼 찾는 중...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchKeyword1"))
    )
    print("✅ 검색 폼 발견")
    
    # 검색어 입력
    print("\n4. 검색어 입력 중...")
    title = "곰돌이 푸"
    author = "밀른"
    
    driver.find_element(By.ID, "searchKeyword1").send_keys(title)
    driver.find_element(By.ID, "searchKeyword2").send_keys(author)
    driver.find_element(By.ID, "searchLibrary").send_keys("판교도서관")
    print(f"✅ 검색어 입력 완료: {title} / {author}")
    
    # 검색 실행
    print("\n5. 검색 버튼 클릭...")
    driver.find_element(By.ID, "searchBtn").click()
    
    # 결과 대기
    print("   결과 로딩 중...")
    time.sleep(3)
    
    # 결과 확인
    print("\n6. 검색 결과 확인 중...")
    result_list = driver.find_elements(By.CSS_SELECTOR, "ul.resultList li")
    print(f"✅ 검색 결과: {len(result_list)}건")
    
    if result_list:
        print("\n7. 청구기호 추출 중...")
        first_result = result_list[0]
        
        # 제목
        try:
            title_elem = first_result.find_element(By.CSS_SELECTOR, "dt.title a")
            print(f"   제목: {title_elem.text}")
        except:
            pass
        
        # 청구기호
        author_dds = first_result.find_elements(By.CSS_SELECTOR, "dd.author")
        
        found_callno = False
        for dd in author_dds:
            text = dd.text
            
            if '청구기호' in text:
                print(f"   청구기호 섹션: {text[:100]}")
                
                match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
                if match:
                    callno = match.group(1).strip()
                    print(f"   ✅ 청구기호: {callno}")
                    found_callno = True
                    break
        
        if not found_callno:
            print("   ⚠️  청구기호를 찾지 못했습니다")
    else:
        print("⚠️  검색 결과가 없습니다")
    
    print("\n" + "="*80)
    print("✅ 테스트 완료!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        driver.quit()
        print("\n🌐 Chrome 드라이버 종료")
    except:
        pass
