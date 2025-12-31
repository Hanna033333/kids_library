"""API 테스트 - limit 100으로"""
import requests

url = "http://localhost:8000/api/books/list"
params = {"page": 1, "limit": 100}

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\nAPI Response:")
        print(f"  Total: {data.get('total')}")
        print(f"  Data length: {len(data.get('data', []))}")
        print(f"  Total pages: {data.get('total_pages')}")
        print(f"  Page: {data.get('page')}")
        print(f"  Limit: {data.get('limit')}")
        
        # 여러 페이지 테스트
        print(f"\n페이지 2 테스트:")
        r2 = requests.get(url, params={"page": 2, "limit": 100}, timeout=10)
        data2 = r2.json()
        print(f"  Page 2 data length: {len(data2.get('data', []))}")
        
        print(f"\n페이지 6 테스트:")
        r6 = requests.get(url, params={"page": 6, "limit": 100}, timeout=10)
        data6 = r6.json()
        print(f"  Page 6 data length: {len(data6.get('data', []))}")
        
    else:
        print(f"Error: {r.text}")
    
except Exception as e:
    print(f"Error: {e}")
