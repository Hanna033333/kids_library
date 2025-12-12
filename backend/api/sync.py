"""데이터 동기화 API 라우터"""
from fastapi import APIRouter
from core.database import supabase
from crawler import fetch_library_books_child
from childbook_crawler import fetch_all_childbook_recommendations

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/library/child")
def sync_library_child(start_dt: str = "2020-01-01", end_dt: str = "2025-12-31"):
    """
    판교도서관 아동 도서(KDC 0~99) 수집 및 Supabase 저장
    
    Parameters:
    - start_dt: 시작일 (YYYY-MM-DD 형식, 기본값: 2020-01-01)
    - end_dt: 종료일 (YYYY-MM-DD 형식, 기본값: 2025-12-31)
    """
    books = fetch_library_books_child(start_dt, end_dt)
    
    for b in books:
        book_data = {
            "isbn13": b["isbn13"],
            "title": b["title"],
            "author": b["author"],
        }
        
        if b.get("callno"):
            book_data["callno"] = b["callno"]
        
        if b.get("lib_code"):
            book_data["lib_code"] = b["lib_code"]
        
        supabase.table("library_items").upsert(book_data).execute()
    
    return {"count": len(books)}


@router.post("/childbook/recommendations")
def sync_childbook():
    """
    어린이 도서 연구회 추천 도서 수집 및 Supabase 저장
    """
    books = fetch_all_childbook_recommendations()
    
    for b in books:
        book_data = {
            "title": b["title"],
            "author": b["author"],
            "publisher": b["publisher"],
        }
        
        if b.get("isbn"):
            book_data["isbn"] = b["isbn"]
        
        supabase.table("childbook_items").upsert(book_data).execute()
    
    return {"count": len(books)}

