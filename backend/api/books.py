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
    category: Optional[str] = Query(None, description="카테고리 (예: '동화', '과학' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    책 검색 및 필터링 (pangyo_callno가 있는 책만 표시)
    """
    return search_books_service(q=q, age=age, category=category, sort=sort, page=page, limit=limit)


@router.get("/list")
def get_books_list(
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    category: Optional[str] = Query(None, description="카테고리 (예: '동화', '과학' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    전체 목록 조회 (pangyo_callno가 있는 책만 표시, 페이지네이션 포함)
    """
    return search_books_service(age=age, category=category, sort=sort, page=page, limit=limit)


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


@router.post("/by-ids")
async def get_books_by_ids(book_ids: List[int] = Body(..., description="책 ID 리스트")):
    """
    여러 책의 상세 정보를 ID로 조회
    """
    print(f"DEBUG: get_books_by_ids called with: {book_ids}")
    if not book_ids:
        return []

    data = supabase.table("childbook_items").select("*").in_("id", book_ids).execute()

    # 순서 유지 (입력받은 ID 순서대로)
    id_map = {book['id']: book for book in data.data}
    ordered_data = [id_map[bid] for bid in book_ids if bid in id_map]

    return ordered_data


@router.get("/{book_id}")
async def get_book_detail(book_id: int):
    """
    책 상세 정보 및 찜 횟수 조회
    """
    # 1. 책 정보 조회
    book_data = supabase.table("childbook_items").select("*").eq("id", book_id).execute()

    if not book_data.data:
        # FastAPI에서 404 처리를 위해 HTTPException을 쓸 수도 있지만 심플하게 구현
        return None

    book = book_data.data[0]

    # 2. 알라딘 API 도서 소개 정보 (Caching)
    # DB에 설명이 없으면 알라딘 API에서 가져와서 저장
    if not book.get("description"):
        isbn = book.get("isbn")
        if isbn:
            try:
                from core.config import ALADIN_TTB_KEY
                import requests
                
                # 알라딘 ItemLookUp API 사용
                url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
                params = {
                    "ttbkey": ALADIN_TTB_KEY,
                    "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
                    "ItemId": isbn,
                    "output": "js",
                    "Version": "20131101",
                    "OptResult": "description"
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("item", [])
                    if items:
                        description = items[0].get("description")
                        if description:
                            # DB 업데이트 (백그라운드 처리 대신 즉시 업데이트로 단순화)
                            supabase.table("childbook_items").update({"description": description}).eq("id", book_id).execute()
                            book["description"] = description
            except Exception as e:
                print(f"Error fetching Aladin description: {e}")

    # 3. 찜 횟수 조회 (Count)
    count_data = supabase.table("user_saved_books").select("id", count="exact").eq("book_id", book_id).execute()
    book["save_count"] = count_data.count if count_data.count is not None else 0

    return book



