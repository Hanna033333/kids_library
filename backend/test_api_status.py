"""
data4library.kr API 상태 확인
"""
import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# Load environment (.env)
env_path = Path(__file__).parent / ".env"
try:
    load_dotenv(dotenv_path=env_path)
except Exception:
    # dotenv 실패 시 직접 파일 읽기
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key and value:
                                os.environ[key] = value
                        except Exception:
                            continue
        except Exception:
            pass

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"  # 판교도서관 코드

print("=" * 60)
print("data4library.kr API 상태 확인")
print("=" * 60)
print()

if not DATA4LIBRARY_KEY:
    print("❌ DATA4LIBRARY_KEY가 설정되지 않았습니다.")
    print("테스트를 중단합니다.")
    exit(1)

# 테스트 1: 간단한 요청 (최근 1주일 데이터)
print("테스트 1: 최근 1주일 데이터 요청 (페이지 크기 10)")
print("-" * 60)

try:
    # 최근 1주일
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": start_date,
        "endDt": end_date,
        "pageNo": 1,
        "pageSize": 10,
        "format": "json"
    }
    
    print(f"요청 URL: {url}")
    print(f"파라미터: {params}")
    print()
    
    response = requests.get(url, params=params, timeout=30)
    print(f"응답 상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"응답 형식: JSON")
            print(f"응답 키: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            if isinstance(data, dict):
                if 'response' in data:
                    response_data = data['response']
                    if 'result' in response_data:
                        result = response_data['result']
                        numFound = result.get('numFound', 0)
                        print(f"검색된 도서 수: {numFound}권")
                        
                        if 'item' in result:
                            items = result['item']
                            if isinstance(items, list):
                                print(f"반환된 도서 수: {len(items)}권")
                                if len(items) > 0:
                                    print(f"\n첫 번째 도서 샘플:")
                                    first_item = items[0]
                                    print(f"  제목: {first_item.get('bookname', 'N/A')}")
                                    print(f"  저자: {first_item.get('authors', 'N/A')}")
                                    print(f"  ISBN: {first_item.get('isbn13', 'N/A')}")
                                    if 'callNumbers' in first_item:
                                        print(f"  청구기호 정보: {first_item.get('callNumbers', [])}")
                        else:
                            print("응답에 'item' 키가 없습니다.")
                    else:
                        print("응답에 'result' 키가 없습니다.")
                else:
                    print("응답에 'response' 키가 없습니다.")
                    print(f"전체 응답: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
            else:
                print(f"응답이 딕셔너리가 아닙니다: {type(data)}")
                print(f"응답 내용: {str(data)[:500]}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"응답 내용 (처음 500자): {response.text[:500]}")
    else:
        print(f"❌ HTTP 오류: {response.status_code}")
        print(f"응답 내용: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ 요청 타임아웃 (30초 초과)")
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 오류: {e}")
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

# 테스트 2: 더 긴 기간 (2024년 12월만)
print("테스트 2: 2024년 12월 데이터 요청 (페이지 크기 10)")
print("-" * 60)

try:
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": "2024-12-01",
        "endDt": "2024-12-31",
        "pageNo": 1,
        "pageSize": 10,
        "format": "json"
    }
    
    print(f"요청 파라미터: {params}")
    print()
    
    response = requests.get(url, params=params, timeout=60)
    print(f"응답 상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict) and 'response' in data:
                result = data['response'].get('result', {})
                numFound = result.get('numFound', 0)
                print(f"✅ 검색된 도서 수: {numFound}권")
                print(f"✅ API 정상 작동 중")
            else:
                print(f"⚠️ 응답 형식이 예상과 다릅니다")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
    elif response.status_code == 504:
        print("❌ Gateway Timeout - API 서버가 응답하지 않습니다")
    else:
        print(f"❌ HTTP 오류: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ 요청 타임아웃 (60초 초과)")
except Exception as e:
    print(f"❌ 오류: {e}")

print()
print("=" * 60)
print("테스트 완료")
