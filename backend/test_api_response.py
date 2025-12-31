"""백엔드 API 테스트"""
import requests

url = "http://localhost:8000/api/books/list"
params = {"page": 1, "limit": 1000}

try:
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    
    print(f"API Response:")
    print(f"  Total: {data.get('total')}")
    print(f"  Data length: {len(data.get('data', []))}")
    print(f"  Total pages: {data.get('total_pages')}")
    print(f"  Page: {data.get('page')}")
    print(f"  Limit: {data.get('limit')}")
    
except Exception as e:
    print(f"Error: {e}")
