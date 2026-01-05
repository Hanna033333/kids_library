
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_driver():
    print("Testing ChromeDriver...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Driver initialized successfully.")
        driver.get("https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do")
        print(f"Title: {driver.title}")
        driver.quit()
        print("Driver quit.")
    except Exception as e:
        print(f"Driver failed: {e}")

if __name__ == "__main__":
    test_driver()
