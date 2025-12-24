"""권차 정보를 DB에 저장 (정확한 매칭)"""
import asyncio
import aiohttp
import re
from core.database import supabase
from core.config import DATA4LIBRARY_KEY
from services.loan_status import fetch_loan_status_batch

PANGYO_LIB_CODE = "141231"

def normalize_isbn(isbn: str) -> str:
    """ISBN 정규화"""
    if not isbn:
        return ""
    return re.sub(r"[^0-9]", "", isbn)

def normalize_title(title: str) -> str:
    """제목 정규화"""
    if not title:
        return ""
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"[^a-zA-Z0-9가-힣]", "", title)
    return title.lower()

async def fetch_and_match_volume(session, book):
    """ISBN으로 조회 후 제목/청구기호로 정확한 권차 매칭"""
    isbn = normalize_isbn(book.get('isbn', ''))
    title = book.get('title', '')
    callno = book.get('pangyo_callno', '')
    
    if not isbn:
        return None
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "ISBN",
        "keyword": isbn,
        "startDt": "2000-01-01",
        "endDt": "2025-12-31",
        "pageNo": 1,
        "pageSize": 50,
        "format": "json"
    }
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            data = await response.json()
            docs = data.get("response", {}).get("docs", [])
            
            if not docs:
                return None
            
            # 제목 정규화
            norm_db_title = normalize_title(title)
            
            # 매칭 시도
            for d in docs:
                doc = d.get("doc", {})
                api_title = doc.get("bookname", "")
                api_vol = doc.get("vol", "").strip()
                api_class_no = doc.get("class_no", "")
                
                norm_api_title = normalize_title(api_title)
                
                # 1. 제목 정확 매칭
                if norm_api_title == norm_db_title and api_vol:
                    return api_vol
                
                # 2. 제목 부분 매칭 (3글자 이상)
                if len(norm_db_title) >= 3:
                    if norm_db_title in norm_api_title or norm_api_title in norm_db_title:
                        if api_vol:
                            return api_vol
            
            # 매칭 실패 시 첫 번째 결과의 vol 반환 (있으면)
            first_doc = docs[0].get("doc", {})
            first_vol = first_doc.get("vol", "").strip()
            return first_vol if first_vol else None
            
    except Exception as e:
        print(f"Error for {title}: {e}")
        return None

async def update_volumes_to_db():
    """권차 정보를 DB에 업데이트"""
    
    print("📚 전체 도서 목록 조회 중...")
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .execute()
    
    books = response.data
    books_with_isbn = [book for book in books if book.get('isbn') and book.get('isbn').strip()]
    
    print(f"✅ ISBN 있는 도서: {len(books_with_isbn)}권")
    
    print("\n🔍 대출 상태 확인 중...")
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    # 미소장이 아닌 책만 필터링
    owned_books = []
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status and loan_status.get('status') != '미소장':
            owned_books.append(book)
        elif not loan_status:
            owned_books.append(book)
    
    print(f"✅ 소장 도서: {len(owned_books)}권")
    
    print(f"\n🔍 권차 정보 조회 및 DB 업데이트 중...")
    print("(이 작업은 약 5-10분 소요될 수 있습니다...)")
    
    updated_count = 0
    failed_count = 0
    semaphore = asyncio.Semaphore(10)
    
    async def process_book(session, book, index):
        nonlocal updated_count, failed_count
        
        async with semaphore:
            if index % 50 == 0:
                print(f"  진행 중: {index}/{len(owned_books)} (업데이트: {updated_count}, 실패: {failed_count})")
            
            vol = await fetch_and_match_volume(session, book)
            await asyncio.sleep(0.2)
            
            if vol:
                try:
                    supabase.table("childbook_items")\
                        .update({"vol": vol})\
                        .eq("id", book['id'])\
                        .execute()
                    updated_count += 1
                    return True
                except Exception as e:
                    print(f"  ❌ DB 업데이트 실패 ({book['title'][:20]}): {e}")
                    failed_count += 1
                    return False
            else:
                failed_count += 1
                return False
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_book(session, book, i) for i, book in enumerate(owned_books, 1)]
        await asyncio.gather(*tasks)
    
    print(f"\n{'='*60}")
    print(f"✅ 총 {updated_count}권 업데이트 완료")
    print(f"❌ 매칭/업데이트 실패: {failed_count}권")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(update_volumes_to_db())
