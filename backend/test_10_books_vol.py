import requests
from core.config import DATA4LIBRARY_KEY
import json
import csv

PANGYO_LIB_CODE = "141231"

def get_volume_info(isbn):
    """Data4Library API로 권차 정보 조회"""
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "isbn",
        "keyword": isbn,
        "format": "json",
        "startDt": "2000-01-01",
        "endDt": "2025-12-22"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs:
            # 첫 번째 결과의 vol 정보 반환
            doc = docs[0].get("doc", {})
            vol = doc.get("vol", "")
            class_no = doc.get("class_no", "")
            return {"vol": vol, "class_no": class_no, "found": True}
        else:
            return {"vol": "", "class_no": "", "found": False}
    except Exception as e:
        return {"vol": "", "class_no": "", "found": False, "error": str(e)}

def test_10_books():
    """중복 리스트에서 10권 테스트"""
    # CSV에서 10권 읽기
    test_books = []
    with open("duplicates_for_manual_check.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
                break
            test_books.append({
                "isbn": row["ISBN"].strip(),
                "title": row["제목"],
                "callno": row["청구기호"]
            })
    
    print("=" * 80)
    print("📚 Data4Library API 권차 정보 테스트 (10권)")
    print("=" * 80)
    print(f"{'ISBN':15} | {'제목':20} | {'청구기호':15} | {'Vol'}")
    print("-" * 80)
    
    results = []
    for book in test_books:
        vol_info = get_volume_info(book["isbn"])
        vol = vol_info.get("vol", "")
        results.append({
            **book,
            "api_vol": vol,
            "api_class_no": vol_info.get("class_no", "")
        })
        
        print(f"{book['isbn']:15} | {book['title'][:20]:20} | {book['callno'][:15]:15} | {vol}")
    
    print("\n" + "=" * 80)
    print(f"✅ 테스트 완료: {len([r for r in results if r['api_vol']])}권에서 권차 정보 발견")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    test_10_books()
