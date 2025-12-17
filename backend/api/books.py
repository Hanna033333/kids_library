"""책 검색 및 조회 API 라우터"""
from fastapi import APIRouter, Query, Body
from typing import Optional, List
from services.search import search_books_service
from services.loan_status import fetch_loan_status_batch
from core.database import supabase

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("/search")
def search_books(
    q: Optional[str] = Query(None, description="검색어 (제목, 저자, 키워드)"),
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    책 검색 및 필터링 (pangyo_callno가 있는 책만 표시)
    """
    return search_books_service(q=q, age=age, sort=sort, page=page, limit=limit)


@router.get("/list")
def get_books_list(
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    전체 목록 조회 (pangyo_callno가 있는 책만 표시, 페이지네이션 포함)
    """
    return search_books_service(age=age, sort=sort, page=page, limit=limit)


@router.get("")
def get_books():
    """
    전체 목록 조회 (기존 API - 호환성 유지)
    """
    data = supabase.table("childbook_items").select("*").order("title").execute()
    return data.data


@router.get("/debug/env")
def check_env():
    """환경변수 설정 확인 (디버그용)"""
    from core.config import DATA4LIBRARY_KEY
    return {
        "DATA4LIBRARY_KEY_exists": DATA4LIBRARY_KEY is not None,
        "DATA4LIBRARY_KEY_length": len(DATA4LIBRARY_KEY) if DATA4LIBRARY_KEY else 0,
        "DATA4LIBRARY_KEY_preview": DATA4LIBRARY_KEY[:10] + "..." if DATA4LIBRARY_KEY else "NOT SET"
    }


@router.post("/loan-status")
async def get_loan_status(book_ids: List[int] = Body(..., description="책 ID 리스트")):
    """
    여러 책의 대출 정보를 병렬로 조회
    
    Args:
        book_ids: 조회할 책 ID 리스트
        
    Returns:
        {book_id: loan_info} 형태의 딕셔너리
    """
    # DB에서 책 정보 조회 (ISBN 필요)
    books_data = supabase.table("childbook_items").select("id, isbn").in_("id", book_ids).execute()
    
    if not books_data.data:
        return {}
    
    # 대출 정보 병렬 조회
    loan_statuses = await fetch_loan_status_batch(books_data.data)
    
    return loan_statuses



