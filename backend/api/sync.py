"""데이터 동기화 API 라우터"""
from fastapi import APIRouter, HTTPException, status
import os
from core.database import supabase

import sys
import os as _os
# childbook_crawler는 scripts/crawling/ 디렉터리로 이동된 일회성 크롤링 스크립트입니다.
# 운영 서버에서 이 엔드포인트는 ENV=production 시 403으로 막히므로 실제 실행되지 않습니다.
_crawling_dir = _os.path.join(_os.path.dirname(__file__), '..', 'scripts', 'crawling')
sys.path.insert(0, _os.path.abspath(_crawling_dir))


router = APIRouter(prefix="/api/sync", tags=["sync"])



@router.post("/childbook/recommendations")
def sync_childbook():
    """
    어린이 도서 연구회 추천 도서 수집 및 Supabase 저장
    """
    if os.getenv("ENV") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Sync API is disabled in production"
        )

    from childbook_crawler import fetch_all_childbook_recommendations
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






