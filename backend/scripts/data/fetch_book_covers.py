import os
import re
import time
import requests
import concurrent.futures
from dotenv import load_dotenv
from typing import List, Dict, Optional
from supabase import create_client

# 환경변수 로딩
env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
ALADIN_TTBKEY = os.getenv("ALADIN_TTB_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE credentials not found")
    exit(1)

if not ALADIN_TTBKEY:
    print("❌ Error: ALADIN_TTB_KEY not found in .env file")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_title_for_search(title: str) -> str:
    """검색을 위해 부제, 특수문자, 괄호 제거"""
    t = re.sub(r'[\(\[\<].*?[\)\]\>]', '', title)
    t = re.split(r'[-–—:;=~]', t)[0]
    return t.strip()

def optimize_aladin_cover_url(url: str) -> str:
    """coversum, cover200을 cover500으로 변환하고 유효성 확인"""
    if not url:
        return ""
    
    # noimg 체크
    if any(x in url.lower() for x in ["noimg", "no_image", "nothumb", "placeholder"]):
        return ""
    
    # cover500으로 승급
    upgraded = re.sub(r'/(coversum|cover200|cover)/', '/cover500/', url)
    if upgraded != url:
        try:
            r = requests.head(upgraded, timeout=3)
            if r.status_code == 200:
                return upgraded
        except Exception:
            pass
    return url

def fetch_books_needing_images() -> List[Dict]:
    """이미지 URL이 누락된 모든 도서 조회 (페이지네이션 적용)"""
    print("이미지 URL이 누락된 도서 조회 중...")
    all_books = []
    page_size = 1000
    offset = 0

    while True:
        res = supabase.table("childbook_items") \
            .select("id, title, author, isbn, pangyo_callno") \
            .is_("image_url", "null") \
            .range(offset, offset + page_size - 1) \
            .execute()
        data = res.data
        all_books.extend(data)
        if len(data) < page_size:
            break
        offset += page_size
        
    print(f"총 {len(all_books)}권의 도서가 이미지 보정 대상입니다.")
    return all_books

def fetch_aladin_by_isbn(isbn: str) -> Optional[Dict]:
    """ISBN으로 알라딘 API 조회"""
    clean_isbn = isbn.replace("-", "").strip()
    if not clean_isbn:
        return None
        
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTBKEY,
        "itemIdType": "ISBN13" if len(clean_isbn) == 13 else "ISBN",
        "ItemId": clean_isbn,
        "output": "js",
        "Version": "20131101",
        "Cover": "Big"
    }
    
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if "item" in data and len(data["item"]) > 0:
                item = data["item"][0]
                cover = item.get("cover", "")
                isbn13 = item.get("isbn13") or item.get("isbn")
                return {"cover": cover, "isbn": isbn13}
    except Exception:
        pass
    return None

def fetch_aladin_by_title(title: str, author: str = "") -> Optional[Dict]:
    """제목 및 저자로 알라딘 API 검색"""
    clean_t = clean_title_for_search(title)
    if not clean_t:
        return None
        
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": ALADIN_TTBKEY,
        "Query": clean_t,
        "QueryType": "Title",
        "MaxResults": 5,
        "start": 1,
        "output": "js",
        "Version": "20131101",
        "Cover": "Big"
    }
    
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            items = data.get("item", [])
            for item in items:
                item_author = item.get("author", "")
                # 저자가 주어지면 매칭 확인, 없으면 첫번째 유효 커버 사용
                clean_auth = re.sub(r'[\(\[\<].*?[\)\]\>]', '', author).split('글')[0].split(',')[0].strip()
                if not clean_auth or clean_auth in item_author or item_author in clean_auth:
                    cover = item.get("cover", "")
                    isbn13 = item.get("isbn13") or item.get("isbn")
                    if cover:
                        return {"cover": cover, "isbn": isbn13}
            # 저자 매칭이 안 되어도 첫번째 아이템 반환
            if items:
                item = items[0]
                return {"cover": item.get("cover", ""), "isbn": item.get("isbn13") or item.get("isbn")}
    except Exception:
        pass
    return None

def process_book(book: Dict) -> Dict:
    book_id = book["id"]
    title = book.get("title", "")
    author = book.get("author", "")
    isbn = book.get("isbn")
    
    result_data = None
    
    # 1단계: ISBN 조회
    if isbn:
        result_data = fetch_aladin_by_isbn(isbn)
        
    # 2단계: ISBN 조회가 실패했거나 없으면 제목 검색
    if not result_data or not result_data.get("cover"):
        result_data = fetch_aladin_by_title(title, author)
        
    if result_data and result_data.get("cover"):
        cover_url = optimize_aladin_cover_url(result_data["cover"])
        if cover_url:
            update_payload = {"image_url": cover_url}
            # 기존에 ISBN이 없었는데 검색 결과로 찾은 경우 함께 업데이트
            if not isbn and result_data.get("isbn"):
                update_payload["isbn"] = result_data["isbn"]
                
            try:
                supabase.table("childbook_items").update(update_payload).eq("id", book_id).execute()
                return {"status": "success", "id": book_id, "title": title, "cover": cover_url}
            except Exception as e:
                return {"status": "db_error", "id": book_id, "title": title, "error": str(e)}
                
    return {"status": "not_found", "id": book_id, "title": title}

def main():
    books = fetch_books_needing_images()
    if not books:
        print("보정할 도서가 없습니다.")
        return

    print(f"총 {len(books)}권 처리 시작 (10개 스레드 동시 처리)...")
    
    success_list = []
    fail_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_book, book): book for book in books}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            if res["status"] == "success":
                success_list.append(res)
                print(f"[{i+1}/{len(books)}] ✅ [성공] {res['title']} -> {res['cover']}")
            else:
                fail_list.append(res)
                print(f"[{i+1}/{len(books)}] ❌ [실패] {res['title']}")

    print("\n" + "="*50)
    print(f"🎉 처리 완료!")
    print(f"- 성공: {len(success_list)}권")
    print(f"- 실패/미발견: {len(fail_list)}권")
    print("="*50)

if __name__ == "__main__":
    main()
