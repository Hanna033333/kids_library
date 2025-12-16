"""데이터 동기화 API 라우터"""
from fastapi import APIRouter
from core.database import supabase

from childbook_crawler import fetch_all_childbook_recommendations

router = APIRouter(prefix="/api/sync", tags=["sync"])



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

