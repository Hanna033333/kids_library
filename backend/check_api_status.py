"""
data4library API 상태 확인
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import time

env_path = Path(__file__).parent / ".env"
try:
    load_dotenv(dotenv_path=env_path)
except Exception:
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
                    except:
                        pass

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

print("=" * 60)
print("data4library API 상태 확인")
print("=" * 60)
print()

url = "http://data4library.kr/api/itemSrch"

# 테스트 1: 매우 짧은 기간, 작은 페이지 크기
print("테스트 1: 매우 짧은 기간 (2024-12-01 ~ 2024-12-31), 페이지 크기 10")
print("-" * 60)

params1 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 10,  # 매우 작은 크기
    "format": "json"
}

try:
    start_time = time.time()
    res1 = requests.get(url, params=params1, timeout=30)
    elapsed1 = time.time() - start_time
    
    print(f"응답 상태 코드: {res1.status_code}")
    print(f"소요 시간: {elapsed1:.2f}초")
    
    if res1.status_code == 200:
        try:
            data1 = res1.json()
            docs = data1.get("response", {}).get("docs", [])
            print(f"✅ 성공! 응답 받은 도서 수: {len(docs)}권")
        except Exception as e:
            print(f"❌ JSON 파싱 오류: {e}")
    else:
        print(f"❌ HTTP 오류: {res1.status_code}")
        print(f"응답 내용 (처음 200자): {res1.text[:200]}")
except Exception as e:
    print(f"❌ 요청 오류: {e}")

print()
print("테스트 2: 더 짧은 기간 (2024-12-26 ~ 2024-12-31), 페이지 크기 10")
print("-" * 60)

params2 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-26",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

try:
    start_time = time.time()
    res2 = requests.get(url, params=params2, timeout=30)
    elapsed2 = time.time() - start_time
    
    print(f"응답 상태 코드: {res2.status_code}")
    print(f"소요 시간: {elapsed2:.2f}초")
    
    if res2.status_code == 200:
        try:
            data2 = res2.json()
            docs = data2.get("response", {}).get("docs", [])
            print(f"✅ 성공! 응답 받은 도서 수: {len(docs)}권")
        except Exception as e:
            print(f"❌ JSON 파싱 오류: {e}")
    else:
        print(f"❌ HTTP 오류: {res2.status_code}")
        print(f"응답 내용 (처음 200자): {res2.text[:200]}")
except Exception as e:
    print(f"❌ 요청 오류: {e}")

print()
print("테스트 3: 다른 도서관 코드로 테스트 (서울시립도서관)")
print("-" * 60)

params3 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": "111000",  # 서울시립도서관
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

try:
    start_time = time.time()
    res3 = requests.get(url, params=params3, timeout=30)
    elapsed3 = time.time() - start_time
    
    print(f"응답 상태 코드: {res3.status_code}")
    print(f"소요 시간: {elapsed3:.2f}초")
    
    if res3.status_code == 200:
        try:
            data3 = res3.json()
            docs = data3.get("response", {}).get("docs", [])
            print(f"✅ 성공! 응답 받은 도서 수: {len(docs)}권")
            print("→ 다른 도서관은 정상 작동하는 것으로 보임")
        except Exception as e:
            print(f"❌ JSON 파싱 오류: {e}")
    else:
        print(f"❌ HTTP 오류: {res3.status_code}")
except Exception as e:
    print(f"❌ 요청 오류: {e}")

print()
print("=" * 60)
print("결론:")
print("=" * 60)
print("판교도서관(141231) API가 타임아웃되는지, 아니면")
print("전체적으로 API 서버에 문제가 있는지 확인합니다.")






