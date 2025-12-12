import requests

resp = requests.post("http://127.0.0.1:8000/api/sync/library")
print(f"Status: {resp.status_code}")
print(f"Response text: {resp.text[:500]}")
if resp.status_code == 200:
    result = resp.json()
    print(f"Count: {result.get('count', 0)}")
    if result.get('updated'):
        print(f"First few items: {result.get('updated', [])[:3]}")

