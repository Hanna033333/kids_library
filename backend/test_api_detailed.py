"""백엔드 API 상세 테스트"""
import requests

url = "http://localhost:8000/api/books/list"
params = {"page": 1, "limit": 1000}

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Response Text: {r.text[:500]}")  # 처음 500자만
    
    if r.status_code == 200:
        data = r.json()
        print(f"\nParsed JSON:")
        print(f"  Keys: {list(data.keys())}")
        print(f"  Total: {data.get('total')}")
        print(f"  Data length: {len(data.get('data', []))}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
