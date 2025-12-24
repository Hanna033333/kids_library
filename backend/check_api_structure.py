"""API 응답 구조 확인"""
import requests
import json
from core.config import DATA4LIBRARY_KEY
from core.database import supabase

PANGYO_LIB_CODE = "141231"

# 실제 DB에서 책 가져오기
response = supabase.table("childbook_items")\
    .select("isbn, title")\
    .not_.is_("isbn", "null")\
    .limit(1)\
    .execute()

book = response.data[0]
isbn = book['isbn']
title = book['title']

print(f"Testing: {title}")
print(f"ISBN: {isbn}\n")

url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_LIB_CODE,
    "type": "ISBN",
    "keyword": isbn,
    "startDt": "2000-01-01",
    "endDt": "2025-12-31",
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

resp = requests.get(url, params=params, timeout=10)
data = resp.json()

# JSON 저장
with open('api_response_structure.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Response saved to api_response_structure.json")
print(f"\nResponse keys: {list(data.keys())}")

if 'response' in data:
    print(f"Response.response keys: {list(data['response'].keys())}")
    
    if 'docs' in data['response']:
        docs = data['response']['docs']
        print(f"\nNumber of docs: {len(docs)}")
        if docs:
            print(f"First doc keys: {list(docs[0].keys())}")
            if 'doc' in docs[0]:
                print(f"First doc.doc keys: {list(docs[0]['doc'].keys())}")
                print(f"\nvol field: '{docs[0]['doc'].get('vol', 'NOT FOUND')}'")
