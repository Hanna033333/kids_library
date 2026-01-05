import requests
from supabase_client import supabase
from core.config import ALADIN_TTB_KEY

def test_aladin_description():
    """Aladin API 도서 소개 테스트"""
    
    print(f"ALADIN_TTB_KEY: {ALADIN_TTB_KEY[:10]}..." if ALADIN_TTB_KEY else "ALADIN_TTB_KEY: None")
    print()
    
    # description이 없는 책 하나 가져오기
    res = supabase.table("childbook_items") \
        .select("id, title, isbn, description") \
        .is_("description", "null") \
        .limit(1) \
        .execute()
    
    if not res.data:
        print("description이 없는 책이 없습니다.")
        return
    
    book = res.data[0]
    print(f"테스트 책: {book['title']}")
    print(f"ISBN: {book['isbn']}")
    print(f"현재 description: {book['description']}")
    print()
    
    # Aladin API 호출
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13" if len(book['isbn']) == 13 else "ISBN",
        "ItemId": book['isbn'],
        "output": "js",
        "Version": "20131101",
        "OptResult": "description"
    }
    
    print("Aladin API 호출 중...")
    response = requests.get(url, params=params, timeout=5)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        
        # Save to file for inspection
        import json
        with open('aladin_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Response saved to aladin_response.json")
        print(f"Response keys: {list(data.keys())}")
        
        items = data.get("item", [])
        print(f"Items type: {type(items)}")
        print(f"Items found: {len(items) if isinstance(items, list) else 'Not a list'}")
        
        if items and isinstance(items, list):
            print(f"First item keys: {list(items[0].keys())}")
            description = items[0].get("description")
            print(f"Description: {description[:200] if description else 'None'}...")
        else:
            print("No items found or items is not a list")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_aladin_description()
