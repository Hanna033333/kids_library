"""책 검색 및 조회 API 라우터"""
from fastapi import APIRouter, Query, Body
from typing import Optional, List, Union
from datetime import datetime
from services.search import search_books_service
from services.loan_status import fetch_loan_status_batch
from core.database import supabase

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("/search")
def search_books(
    q: Optional[str] = Query(None, description="검색어 (제목, 저자, 키워드)"),
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    category: Optional[str] = Query(None, description="카테고리 (예: '동화', '과학' 등)"),
    curation: Optional[str] = Query(None, description="큐레이션 테마 필터 (예: '가족사랑', 'caldecott' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    책 검색 및 필터링 (pangyo_callno가 있는 책만 표시)
    """
    return search_books_service(q=q, age=age, category=category, curation=curation, sort=sort, page=page, limit=limit)


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





from pydantic import BaseModel

class LoanStatusRequest(BaseModel):
    book_ids: List[int]
    library_name: Optional[str] = "판교도서관"


@router.post("/loan-status")
async def get_loan_status(req: Union[LoanStatusRequest, List[int]] = Body(..., description="대출 정보 조회 요청")):
    """
    여러 책의 특정 도서관 대출 정보를 병렬로 조회 (청구기호가 없으면 API 조회 없이 '미소장'으로 즉시 응답)
    
    Args:
        req: book_ids 리스트와 library_name이 담긴 요청 객체 혹은 raw book_ids 리스트
        
    Returns:
        {book_id: loan_info} 형태의 딕셔너리
    """
    # 구버전(단순 숫자 리스트) 및 신버전(JSON Object) 요청 포맷 유연하게 대응
    if isinstance(req, list):
        book_ids = req
        library_name = "판교도서관"
    else:
        book_ids = req.book_ids
        library_name = req.library_name or "판교도서관"

    # DB에서 책 정보 및 판교 청구기호 조회
    books_data = supabase.table("childbook_items").select("id, isbn, pangyo_callno").in_("id", book_ids).execute()
    
    if not books_data.data:
        return {}
        
    # 선택된 도서관의 청구기호 정보를 book_library_info에서 조회
    lib_infos = []
    if library_name:
        lib_data = supabase.table("book_library_info") \
            .select("book_id, library_name, callno") \
            .in_("book_id", book_ids) \
            .ilike("library_name", f"%{library_name}%") \
            .execute()
        lib_infos = lib_data.data if lib_data.data else []
        
    # 각 도서별 청구기호 소유 여부 판별
    has_callno_map = {}
    for book in books_data.data:
        b_id = book['id']
        has_callno = False
        
        if library_name == "판교도서관" or not library_name:
            p_call = book.get('pangyo_callno')
            if p_call and p_call != '없음' and p_call.strip():
                has_callno = True
            else:
                for info in lib_infos:
                    if info['book_id'] == b_id and ('판교' in info['library_name']) and info.get('callno') and info['callno'] != '없음' and info['callno'].strip():
                        has_callno = True
                        break
        else:
            for info in lib_infos:
                if info['book_id'] == b_id and info.get('callno') and info['callno'] != '없음' and info['callno'].strip():
                    has_callno = True
                    break
        
        has_callno_map[b_id] = has_callno

    # 청구기호가 존재하는 책들만 대출 현황 조회 대상으로 분류
    books_to_fetch = [b for b in books_data.data if has_callno_map.get(b['id'])]
    
    loan_statuses = {}
    if books_to_fetch:
        loan_statuses = await fetch_loan_status_batch(books_to_fetch, library_name)
        
    # 청구기호가 없는 책들은 API 콜과 상관없이 '미소장'으로 덮어씀
    for book in books_data.data:
        b_id = book['id']
        if not has_callno_map.get(b_id):
            loan_statuses[b_id] = {
                "available": None,
                "status": "미소장",
                "updated_at": datetime.now().isoformat()
            }
            
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
                
                response = requests.get(url, params=params, timeout=3)
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

    # 3. 찜 횟수 조회 (Count - wishlists 테이블 기반 정상 버그 픽스)
    count_data = supabase.table("wishlists").select("id", count="exact").eq("book_id", book_id).execute()
    book["save_count"] = count_data.count if count_data.count is not None else 0

    # 4. 도서관 청구기호 조회 (Multi-Library Support)
    try:
        lib_data = supabase.table("book_library_info").select("library_name, callno").eq("book_id", book_id).execute()
        book["library_info"] = lib_data.data if lib_data.data else []
    except Exception as e:
        print(f"Error fetching library info: {e}")
        book["library_info"] = []

    return book





