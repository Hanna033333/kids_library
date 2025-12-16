"""책 검색 및 조회 API 라우터"""
from fastapi import APIRouter, Query
from typing import Optional
from services.search import search_books_service

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
    from core.database import supabase
    data = supabase.table("childbook_items").select("*").order("title").execute()
    return data.data


