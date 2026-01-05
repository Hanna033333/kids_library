import requests
from supabase_client import supabase
from core.config import ALADIN_TTB_KEY

def update_book_cover(book_id: int):
    """특정 책의 표지 이미지를 Aladin API로 업데이트"""
    
    # 책 정보 가져오기
    res = supabase.table("childbook_items") \
        .select("id, title, isbn, image_url") \
        .eq("id", book_id) \
        .execute()
    
    if not res.data:
        print(f"책 ID {book_id}를 찾을 수 없습니다.")
        return
    
    book = res.data[0]
    print(f"책: {book['title']}")
    print(f"ISBN: {book['isbn']}")
    print(f"현재 표지: {book['image_url']}")
    print()
    
    # Aladin API로 표지 이미지 가져오기
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13" if len(book['isbn']) == 13 else "ISBN",
        "ItemId": book['isbn'],
        "output": "js",
        "Version": "20131101",
        "Cover": "Big"  # 큰 이미지
    }
    
    print("Aladin API 호출 중...")
    response = requests.get(url, params=params, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("item", [])
        
        if items:
            cover_url = items[0].get("cover")
            print(f"새 표지 URL: {cover_url}")
            
            if cover_url:
                # DB 업데이트
                supabase.table("childbook_items") \
                    .update({"image_url": cover_url}) \
                    .eq("id", book_id) \
                    .execute()
                
                print("✅ 표지 이미지 업데이트 완료!")
            else:
                print("⚠️ 표지 이미지를 찾을 수 없습니다.")
        else:
            print("⚠️ Aladin에서 책을 찾을 수 없습니다.")
    else:
        print(f"❌ API 호출 실패: {response.status_code}")

if __name__ == "__main__":
    update_book_cover(10388)
