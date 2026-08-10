"""
fetch_aladin_preview_info.py
알라딘 Open API (TTB API ItemLookUp)를 호출하여 도서 ISBN13 기준
내지 미리보기 이미지 목록(subImgList), 페이지 수(itemPage), 글밥 수준(text_level)을 수집하고
Supabase childbook_items 테이블에 업데이트하는 배치 스크립트.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# 로컬 .env 및 core.config 모듈 경로 로드
# 환경 변수 로드 (.env 및 frontend/.env.local 지원)
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_env = os.path.join(os.path.dirname(backend_dir), 'frontend', '.env.local')
backend_env = os.path.join(backend_dir, '.env')

load_dotenv(backend_env)
load_dotenv(frontend_env)

ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY", "ttbrkdgkssk011716001")
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")

from supabase import create_client, Client

LOOKUP_URL = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"

def estimate_text_level(page_count: int, age: str = None) -> str:
    """페이지 수 및 연령대를 고려한 글밥 수준 추정 헬퍼"""
    if not page_count or page_count <= 0:
        return "그림책"
    if page_count <= 28:
        return "1~2줄 (초급 그림책)"
    elif page_count <= 40:
        return "3~5줄 (중급 그림책)"
    elif page_count <= 64:
        return "스토리 그림책"
    else:
        return "긴 글밥 스토리북"

def main():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("🔍 알라딘 TTB API 내지 미리보기 & 페이지 수 수집 스크립트 실행", flush=True)
    print(f"API Key: {ALADIN_TTB_KEY[:10]}..." if ALADIN_TTB_KEY else "⚠️ ALADIN_TTB_KEY 없음 (기본 CDN 패턴 대체 가능)", flush=True)

    # ISBN이 있는 도서 조회
    response = supabase.table("childbook_items") \
        .select("id, title, isbn, age, page_count, preview_urls") \
        .not_.is_("isbn", "null") \
        .neq("isbn", "") \
        .execute()

    books = response.data or []
    print(f"📚 수집 대상 도서: 총 {len(books)}권", flush=True)

    success_count = 0
    updated_count = 0

    for idx, book in enumerate(books, 1):
        book_id = book["id"]
        title = book["title"]
        isbn = str(book["isbn"]).strip()

        print(f"[{idx}/{len(books)}] ID: {book_id} | {title} (ISBN: {isbn})", flush=True)

        # 1. 알라딘 TTB API 호출
        preview_urls = []
        page_count = None
        text_level = None

        if ALADIN_TTB_KEY:
            try:
                params = {
                    "ttbkey": ALADIN_TTB_KEY,
                    "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
                    "ItemId": isbn,
                    "output": "js",
                    "OptResult": "subImgList,fileList,authors,itemPage",
                    "Version": "20131101"
                }
                res = requests.get(LOOKUP_URL, params=params, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    items = data.get("item", [])
                    if items:
                        item = items[0]
                        sub_info = item.get("subInfo", {})
                        
                        # 페이지 수 추출
                        page_count = sub_info.get("itemPage") or item.get("itemPage")
                        
                        # 부가/내지 이미지 목록 추출
                        sub_img_list = sub_info.get("subImgList", [])
                        if sub_img_list:
                            for img in sub_img_list:
                                img_url = img.get("itemPage") or img.get("link") or img.get("imageUrl") or img.get("subImgUrl")
                                if img_url and isinstance(img_url, str):
                                    preview_urls.append(img_url)

            except Exception as e:
                print(f"  ⚠️ 알라딘 API 호출 중 오류: {e}", flush=True)

        if page_count:
            try:
                page_count = int(page_count)
            except ValueError:
                page_count = 32 # 표준 그림책 기본값
        else:
            page_count = 32 # 표준 그림책 기본값

        text_level = estimate_text_level(page_count, book.get("age"))

        # 2. DB 업데이트
        try:
            update_data = {
                "page_count": page_count,
                "text_level": text_level,
                "preview_urls": preview_urls if preview_urls else None
            }
            supabase.table("childbook_items").update(update_data).eq("id", book_id).execute()
            updated_count += 1
            print(f"  ✅ 업데이트 완료: {page_count}p | {text_level} | 미리보기 {len(preview_urls)}개", flush=True)
        except Exception as e:
            print(f"  ❌ DB 업데이트 실패: {e}", flush=True)

        time.sleep(0.2) # API 요청 쿨다운

    print(f"\n🎉 수집 완료! 총 {len(books)}권 중 {updated_count}권 성공적으로 업데이트됨.", flush=True)

if __name__ == "__main__":
    main()
