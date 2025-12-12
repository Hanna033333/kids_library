"""
ISBN 검색 디버깅 (네이버 API 응답 확인)
"""
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
env_vars = {}
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
                            env_vars[key] = value
                    except Exception:
                        continue
    except Exception:
        pass

try:
    load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

for key, value in env_vars.items():
    if key not in os.environ:
        try:
            os.environ[key] = value
        except Exception:
            pass

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID") or env_vars.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET") or env_vars.get("NAVER_CLIENT_SECRET")

# 테스트 쿼리
test_queries = [
    ("동그란 지구의 하루", "니콜라이 포포프"),
    ("세상을 바꾼 큰 걸음", "김성훈"),
    ("아무도 모르는 작은 나라", "사토 사토루"),
]

url = "https://openapi.naver.com/v1/search/book.json"
headers = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
}

print("=" * 60)
print("네이버 API 응답 테스트")
print("=" * 60)
print()

for title, author in test_queries:
    query = f"{title} {author}".strip()
    params = {"query": query, "display": 10}
    
    print(f"검색 쿼리: {query}")
    print(f"API 키 존재: {bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)}")
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"상태 코드: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            print(f"총 결과: {total}개")
            print(f"반환된 항목: {len(items)}개")
            
            if items:
                first_item = items[0]
                print(f"첫 번째 결과:")
                print(f"  제목: {first_item.get('title', '')}")
                print(f"  저자: {first_item.get('author', '')}")
                print(f"  ISBN: {first_item.get('isbn', '')}")
                print(f"  ISBN13: {first_item.get('isbn13', '')}")
            else:
                print("  ⚠️  결과 없음")
        else:
            print(f"  ❌ 오류: {res.text[:200]}")
    except Exception as e:
        print(f"  ❌ 예외: {e}")
    
    print("-" * 60)
    print()


