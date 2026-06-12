from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')  # 백그라운드 실행
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

print("🔍 Selenium으로 ISBN 크롤링 테스트")
print()

# 드라이버 초기화
driver = webdriver.Chrome(options=chrome_options)

try:
    # 상세 페이지 접근
    url = "https://www.snlib.go.kr/pg/menu/10519/program/30009/plusSearchResultDetail.do?recKey=1949734267&bookKey=1949734269"
    
    print(f"페이지 로딩 중: {url}")
    driver.get(url)
    
    # 페이지 로딩 대기
    time.sleep(3)
    
    # 표준번호 찾기
    print("\n=== 표준번호 찾기 ===")
    
    # 방법 1: XPath로 찾기
    try:
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '표준번호')]")
        if elements:
            print(f"찾음! 요소 개수: {len(elements)}")
            for elem in elements:
                print(f"텍스트: {elem.text}")
                # 다음 형제 요소 찾기
                try:
                    parent = elem.find_element(By.XPATH, "..")
                    siblings = parent.find_elements(By.XPATH, "./*")
                    for sib in siblings:
                        if 'ISBN' in sib.text.upper():
                            print(f"ISBN 발견: {sib.text}")
                except:
                    pass
    except Exception as e:
        print(f"에러: {e}")
    
    # 방법 2: 전체 페이지 텍스트에서 ISBN 검색
    print("\n=== 전체 페이지 텍스트에서 ISBN 검색 ===")
    page_text = driver.find_element(By.TAG_NAME, "body").text
    isbn_matches = re.findall(r'ISBN[:\s-]*(\d{13}|\d{10})', page_text, re.IGNORECASE)
    if isbn_matches:
        print(f"찾은 ISBN: {isbn_matches}")
    else:
        print("ISBN 못 찾음")
    
    # 방법 3: 페이지 소스 확인
    print("\n=== 페이지 소스 일부 ===")
    print(driver.page_source[:2000])
    
finally:
    driver.quit()

print("\n✅ 테스트 완료!")
