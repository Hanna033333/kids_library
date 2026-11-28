"""책 검색 및 조회 API 라우터"""
from fastapi import APIRouter, Query, Body, HTTPException, status, BackgroundTasks
from typing import Optional, List, Union, Dict
from datetime import datetime
import logging
from services.search import search_books_service
from services.loan_status import fetch_loan_status_batch
from core.database import supabase

router = APIRouter(prefix="/api/books", tags=["books"])
logger = logging.getLogger(__name__)

@router.get("/search")
def search_books(
    q: Optional[str] = Query(None, description="검색어 (제목, 저자, 키워드)"),
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    category: Optional[str] = Query(None, description="카테고리 (예: '동화', '과학' 등)"),
    curation: Optional[str] = Query(None, description="큐레이션 테마 필터 (예: '가족사랑', 'caldecott' 등)"),
    sort: Optional[str] = Query("title", description="정렬 기준 ('title', 'callno', 'confidence_score_desc', 'popular')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    include_library_info: bool = Query(False, description="도서관 소장 정보 포함 여부"),
    tag: Optional[str] = Query(None, description="세부 태그 필터 (예: '초등1학년' 등)"),
    library: Optional[str] = Query(None, description="선택된 도서관 이름 (청구기호순 정렬 기준)")
):
    """
    책 검색 및 필터링
    """
    return search_books_service(q=q, age=age, category=category, curation=curation, sort=sort, page=page, limit=limit, include_library_info=include_library_info, tag=tag, library=library)


@router.get("/list")
def get_books_list(
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    category: Optional[str] = Query(None, description="카테고리 (예: '동화', '과학' 등)"),
    sort: Optional[str] = Query("title", description="정렬 기준 ('title', 'callno', 'confidence_score_desc', 'popular')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    include_library_info: bool = Query(False, description="도서관 소장 정보 포함 여부"),
    tag: Optional[str] = Query(None, description="세부 태그 필터 (예: '초등1학년' 등)"),
    library: Optional[str] = Query(None, description="선택된 도서관 이름 (청구기호순 정렬 기준)")
):
    """
    전체 목록 조회 (페이지네이션 포함)
    """
    return search_books_service(age=age, category=category, sort=sort, page=page, limit=limit, include_library_info=include_library_info, tag=tag, library=library)


from pydantic import BaseModel

class LoanStatusRequest(BaseModel):
    book_ids: List[int]
    library_name: Optional[str] = "판교도서관"
    lib_code: Optional[str] = None
    include_callno: bool = False


def _cache_callno_to_db(book_id: int, library_name: str, callno: str) -> None:
    """On-Demand로 조회된 전국 도서관 청구기호를 book_library_info에 백그라운드 캐싱"""
    try:
        supabase.table("book_library_info").upsert(
            {
                "book_id": book_id,
                "library_name": library_name,
                "callno": callno,
            },
            on_conflict="book_id,library_name",
        ).execute()
    except Exception as e:
        logger.warning(f"Failed to cache on-demand callno ({library_name}, book {book_id}): {e}")


@router.post("/loan-status")
async def get_loan_status(
    background_tasks: BackgroundTasks,
    req: Union[LoanStatusRequest, List[int]] = Body(..., description="대출 정보 조회 요청"),
):
    """
    여러 책의 특정 도서관 대출 정보를 병렬로 조회 (전국 1,600+ 공공도서관 단일 실시간 구조)
    - 모든 도서관에 대해 정보나루 bookExist 실시간 조회 (소장 10분 / 미소장 24시간 캐싱)
    - DB book_library_info에 청구기호가 이미 있으면 우선 첨부
    - 단건 상세(include_callno=True)에서 소장 확인 + DB 청구기호 누락 시 itemSrch On-Demand 조회 및 DB 자동 캐싱
    """
    from services.library_registry import find_library
    from services.loan_status import LIBRARY_CODE_MAP, fetch_callno_on_demand

    if isinstance(req, list):
        book_ids = req
        library_name = "판교도서관"
        lib_code = None
        include_callno = False
    else:
        book_ids = req.book_ids
        library_name = req.library_name or "판교도서관"
        lib_code = req.lib_code
        include_callno = bool(req.include_callno)

    if len(book_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 최대 50개의 도서 ID만 요청할 수 있습니다."
        )

    target_lib = find_library(library_name=library_name, lib_code=lib_code)
    resolved_lib_code = (
        (target_lib["code"] if target_lib else None)
        or lib_code
        or LIBRARY_CODE_MAP.get(library_name)
    )
    resolved_lib_name = (target_lib["name"] if target_lib else None) or library_name
    library_homepage = target_lib.get("homepage", "") if target_lib else ""

    # DB에서 책 정보 및 청구기호 정보를 단일 쿼리로 비동기(스레드풀) 조회
    import asyncio

    def _fetch_books_and_callnos():
        return (
            supabase.table("childbook_items")
            .select("id, isbn, book_library_info(library_name, callno)")
            .in_("id", book_ids)
            .execute()
        )

    books_data = await asyncio.to_thread(_fetch_books_and_callnos)

    if not books_data.data:
        return {}

    # 각 도서별 선택 도서관 청구기호 소유 여부 및 캐시된 청구기호 매핑
    callno_map: Dict[int, str] = {}
    for book in books_data.data:
        b_id = book["id"]
        if resolved_lib_name:
            for info in (book.get("book_library_info") or []):
                lib_name = info.get("library_name") or ""
                callno = (info.get("callno") or "").strip()
                if (
                    callno
                    and callno != "없음"
                    and (
                        resolved_lib_name.lower() == lib_name.lower()
                        or resolved_lib_name.lower() in lib_name.lower()
                    )
                ):
                    callno_map[b_id] = callno
                    break

    # 전국 모든 도서관 동일하게 bookExist 실시간 병렬 조회
    books_to_fetch = [{"id": b["id"], "isbn": b.get("isbn")} for b in books_data.data]

    loan_statuses = {}
    if books_to_fetch:
        loan_statuses = await fetch_loan_status_batch(
            books_to_fetch,
            library_name=resolved_lib_name,
            lib_code=resolved_lib_code,
        )

    # 결과 누락 책 폴백 + DB에 이미 캐싱된 청구기호 및 도서관 홈페이지 정보 첨부
    for book in books_data.data:
        b_id = book["id"]
        if b_id not in loan_statuses:
            loan_statuses[b_id] = {
                "available": None,
                "status": "미소장",
                "updated_at": datetime.now().isoformat()
            }
        # DB에 이미 있는 청구기호와 도서관 홈페이지 정보 첨부
        if b_id in callno_map:
            loan_statuses[b_id] = {**loan_statuses[b_id], "callno": callno_map[b_id]}
        if library_homepage:
            loan_statuses[b_id] = {**loan_statuses[b_id], "library_homepage": library_homepage}

    # On-Demand 청구기호 조회 (안 2): 단건/소수 상세 요청(<= 3권) + 소장 확인 + DB 청구기호 없음
    if include_callno and resolved_lib_code and len(books_data.data) <= 3:
        for book in books_data.data:
            b_id = book["id"]
            isbn = (book.get("isbn") or "").strip()
            st = loan_statuses.get(b_id, {}).get("status")
            if isbn and st in ("대출가능", "대출중") and b_id not in callno_map:
                on_demand_callno = await fetch_callno_on_demand(isbn, resolved_lib_code)
                if on_demand_callno:
                    loan_statuses[b_id] = {**loan_statuses[b_id], "callno": on_demand_callno}
                    background_tasks.add_task(_cache_callno_to_db, b_id, resolved_lib_name, on_demand_callno)

    return loan_statuses


@router.post("/by-ids")
def get_books_by_ids(book_ids: List[int] = Body(..., description="책 ID 리스트")):
    """
    여러 책의 상세 정보를 ID로 조회 (FastAPI 스레드풀 실행으로 이벤트 루프 블로킹 방지)
    """
    if not book_ids:
        return []

    if len(book_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 최대 50개의 도서 ID만 요청할 수 있습니다."
        )

    data = supabase.table("childbook_items").select("*, library_info:book_library_info(library_name, callno)").in_("id", book_ids).execute()

    # 순서 유지 (입력받은 ID 순서대로)
    id_map = {book['id']: book for book in data.data}
    ordered_data = [id_map[bid] for bid in book_ids if bid in id_map]

    return ordered_data


def update_description_bg(book_id: int, description: str):
    """백그라운드에서 알라딘 도서 설명을 DB에 업데이트합니다."""
    try:
        supabase.table("childbook_items").update({"description": description}).eq("id", book_id).execute()
    except Exception as e:
        logger.error(f"Failed to update Aladin description in background for book {book_id}: {e}")


@router.get("/{book_id}")
def get_book_detail(book_id: int, background_tasks: BackgroundTasks):
    """
    책 상세 정보 및 찜 횟수 조회 (FastAPI 스레드풀에서 실행하여 동기 API 호출 블로킹 방지)
    """
    # 1. 책 정보 조회
    book_data = supabase.table("childbook_items").select("*").eq("id", book_id).execute()

    if not book_data.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="도서를 찾을 수 없습니다.")

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
                            # DB 업데이트를 백그라운드 태스크로 넘겨 즉각적인 API 반환 보장
                            background_tasks.add_task(update_description_bg, book_id, description)
                            book["description"] = description
            except Exception as e:
                logger.error(f"Error fetching Aladin description for book {book_id}: {e}")

    # 3. 찜 횟수 조회 (Count)
    count_data = supabase.table("wishlists").select("id", count="exact").eq("book_id", book_id).execute()
    book["save_count"] = count_data.count if count_data.count is not None else 0

    # 4. 도서관 청구기호 조회
    try:
        lib_data = supabase.table("book_library_info").select("library_name, callno").eq("book_id", book_id).execute()
        book["library_info"] = lib_data.data if lib_data.data else []
    except Exception as e:
        logger.error(f"Error fetching library info for book {book_id}: {e}")
        book["library_info"] = []

    return book
