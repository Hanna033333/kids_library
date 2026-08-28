"""데이터 동기화 API 라우터"""
from fastapi import APIRouter, HTTPException, status
import os
from core.database import supabase

import sys
import os as _os
# childbook_crawler는 scripts/crawling/ 디렉터리로 이동된 일회성 크롤링 스크립트입니다.
# 이 엔드포인트는 ENV=development 로 명시적으로 설정된 경우에만 동작합니다 (화이트리스트 방식, fail-closed).
_crawling_dir = _os.path.join(_os.path.dirname(__file__), '..', 'scripts', 'crawling')
sys.path.insert(0, _os.path.abspath(_crawling_dir))


router = APIRouter(prefix="/api/sync", tags=["sync"])



@router.post("/childbook/recommendations")
def sync_childbook():
    """
    어린이 도서 연구회 추천 도서 수집 및 Supabase 저장
    """
    # 화이트리스트 방식: ENV가 명시적으로 "development"가 아니면 항상 차단 (fail-closed).
    # 기존에는 ENV == "production" 일 때만 막는 fail-open 구조라 ENV 값이 비어 있으면
    # 상용 서버에서도 무인증으로 크롤링/DB upsert가 실행될 수 있었습니다.
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Sync API is only enabled when ENV=development"
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






