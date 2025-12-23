import requests
import os
from core.config import DATA4LIBRARY_KEY
import csv

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

def test_volume_info(isbn, title, f_log):
    # 도서관별 장서 조회 API
    url = "http://data4library.kr/api/itemSrch"
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "isbn",
        "keyword": isbn,
        "format": "json",
        "startDt": "2000-01-01",
        "endDt": today,
        "pageNo": 1,
        "pageSize": 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            msg = f"Error: Status {response.status_code}"
            f_log.write(f"{isbn} | {title} | {msg}\n")
            return msg
            
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if not docs:
            msg = "No data found"
            f_log.write(f"{isbn} | {title} | {msg}\n")
            return msg
            
        results = []
        for doc_wrapper in docs:
            doc = doc_wrapper.get("doc", {})
            vol = doc.get("vol")
            results.append(f"vol: '{vol}'")
            
        msg = ", ".join(results)
        f_log.write(f"{isbn} | {title} | {msg}\n")
        return msg
    except Exception as e:
        msg = f"Error: {e}"
        f_log.write(f"{isbn} | {title} | {msg}\n")
        return msg

def main():
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY is missing!")
        return

    # 10개 테스트 데이터 (직접 지정)
    test_data = [
        ('9788949113760', '안녕, 나의 등대'),
        ('9788949111131', '고양이 폭풍'),
        ('9788949112718', '아모스와 보리스'),
        ('9788949111421', '두 듀로이'),
        ('9788949110226', '꼬마 곰 코듀로이'),
        ('9788949113609', '양배추 소년'),
        ('9788949111803', '양배추 소년'),
        ('9788936441753', '문제아'),
        ('9791185934945', '문제아'),
        ('9788931454109', '마인크래프트')
    ]
    
    with open("test_results.txt", "w", encoding="utf-8") as f_log:
        f_log.write(f"{'ISBN':15} | {'Title':20} | {'Volume Info'}\n")
        f_log.write("-" * 60 + "\n")
        
        for isbn, title in test_data:
            print(f"Testing {isbn} ({title})...")
            vol_info = test_volume_info(isbn, title, f_log)
            print(f"  -> {vol_info}")

    print("\n✅ Results saved to test_results.txt")

if __name__ == "__main__":
    main()
