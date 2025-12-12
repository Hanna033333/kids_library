from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase_client import supabase
from crawler import fetch_library_books_child
from childbook_crawler import fetch_all_childbook_recommendations
from datetime import datetime
from typing import Optional

app = FastAPI()

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sync_library_books_child(start_dt: str = "2020-01-01", end_dt: str = "2025-12-31"):
    """
    판교도서관 아동 도서 수집 및 Supabase 저장
    """
    books = fetch_library_books_child(start_dt, end_dt)
    
    for b in books:
        # library_items 테이블에 저장
        # 테이블 스키마에 맞게 필드 매핑
        book_data = {
            "isbn13": b["isbn13"],
            "title": b["title"],
            "author": b["author"],
        }
        
        # callno 필드가 있는 경우 추가
        if b.get("callno"):
            book_data["callno"] = b["callno"]
        
        # lib_code 필드가 있는 경우 추가
        if b.get("lib_code"):
            book_data["lib_code"] = b["lib_code"]
        
        supabase.table("library_items").upsert(book_data).execute()
    
    return {"count": len(books)}


# 1) 판교도서관 아동 도서 수집 및 동기화
@app.post("/api/sync/library/child")
def sync_library_child(start_dt: str = "2020-01-01", end_dt: str = "2025-12-31"):
    """
    판교도서관 아동 도서(KDC 0~99) 수집 및 Supabase 저장
    
    Parameters:
    - start_dt: 시작일 (YYYY-MM-DD 형식, 기본값: 2020-01-01)
    - end_dt: 종료일 (YYYY-MM-DD 형식, 기본값: 2025-12-31)
    """
    return sync_library_books_child(start_dt, end_dt)


def sync_childbook_recommendations():
    """
    어린이 도서 연구회 추천 도서 수집 및 Supabase 저장
    """
    books = fetch_all_childbook_recommendations()
    
    for b in books:
        # childbook_items 테이블에 저장
        # 테이블 스키마에 맞게 필드 매핑
        book_data = {
            "title": b["title"],
            "author": b["author"],
            "publisher": b["publisher"],
        }
        
        # ISBN이 있는 경우 추가 (크롤링한 데이터에 ISBN이 없을 수 있음)
        if b.get("isbn"):
            book_data["isbn"] = b["isbn"]
        
        supabase.table("childbook_items").upsert(book_data).execute()
    
    return {"count": len(books)}


# 2) 어린이 도서 연구회 추천 도서 수집 및 동기화
@app.post("/api/sync/childbook/recommendations")
def sync_childbook():
    """
    어린이 도서 연구회 추천 도서 수집 및 Supabase 저장
    """
    return sync_childbook_recommendations()


# 3) 전체 목록 조회 (기존 - 호환성 유지)
@app.get("/api/books")
def get_books():
    data = supabase.table("childbook_items").select("*").order("title").execute()
    return data.data


# 4) 검색 및 필터링된 목록 조회 (페이지네이션 포함)
@app.get("/api/books/search")
def search_books(
    q: Optional[str] = Query(None, description="검색어 (제목, 저자, 키워드)"),
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    책 검색 및 필터링 (pangyo_callno가 있는 책만 표시)
    
    Parameters:
    - q: 검색어 (제목, 저자, 키워드)
    - age: 연령대 구간 (예: '0-3', '4-7', '8-12' 등)
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    # 기본 필터: pangyo_callno가 있는 책만 (IS NOT NULL AND != '없음')
    query = supabase.table("childbook_items").select("*", count="exact")
    
    # pangyo_callno 필터링
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    
    # 검색어 필터링
    if q:
        q = q.strip()
        if q:
            # 제목 또는 저자에 검색어가 포함된 경우
            # Supabase PostgREST의 or_() 사용
            query = query.or_(f"title.ilike.%{q}%,author.ilike.%{q}%")
    
    # 연령 필터링
    if age:
        age = age.strip()
        if age:
            # 연령 필드에서 연령대 구간 매칭
            # 예: '0-3' -> '0세부터' 또는 '0-3세' 등 포함
            if age == "0-3":
                # 0-3세 범위: 0세부터, 1세부터, 2세부터, 3세부터 등
                query = query.or_(f"age.ilike.%0세%,age.ilike.%1세%,age.ilike.%2세%,age.ilike.%3세%,age.ilike.%{age}%")
            elif age == "4-7":
                # 4-7세 범위
                query = query.or_(f"age.ilike.%4세%,age.ilike.%5세%,age.ilike.%6세%,age.ilike.%7세%,age.ilike.%{age}%")
            elif age == "8-12":
                # 8-12세 범위
                query = query.or_(f"age.ilike.%8세%,age.ilike.%9세%,age.ilike.%10세%,age.ilike.%11세%,age.ilike.%12세%,age.ilike.%{age}%")
            elif age == "13+":
                # 13세 이상
                query = query.or_(f"age.ilike.%13세%,age.ilike.%13%")
            else:
                query = query.ilike("age", f"%{age}%")
    
    # 정렬
    if sort == "title":
        query = query.order("title")
    else:  # 기본값: pangyo_callno
        query = query.order("pangyo_callno")
    
    # 페이지네이션
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)
    
    # 실행
    result = query.execute()
    
    return {
        "data": result.data,
        "total": result.count if hasattr(result, 'count') else len(result.data),
        "page": page,
        "limit": limit,
        "total_pages": (result.count + limit - 1) // limit if hasattr(result, 'count') and result.count else 1
    }


# 5) 필터링된 전체 목록 조회 (페이지네이션 포함)
@app.get("/api/books/list")
def get_books_list(
    age: Optional[str] = Query(None, description="연령대 구간 (예: '0-3', '4-7', '8-12' 등)"),
    sort: Optional[str] = Query("pangyo_callno", description="정렬 기준 ('title' 또는 'pangyo_callno')"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수")
):
    """
    전체 목록 조회 (pangyo_callno가 있는 책만 표시, 페이지네이션 포함)
    
    Parameters:
    - age: 연령대 구간 (예: '0-3', '4-7', '8-12' 등)
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지당 항목 수 (기본값: 20, 최대: 100)
    """
    # 기본 필터: pangyo_callno가 있는 책만
    query = supabase.table("childbook_items").select("*", count="exact")
    
    # pangyo_callno 필터링
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    
    # 연령 필터링
    if age:
        age = age.strip()
        if age:
            if age == "0-3":
                query = query.or_(f"age.ilike.%0세%,age.ilike.%1세%,age.ilike.%2세%,age.ilike.%3세%,age.ilike.%{age}%")
            elif age == "4-7":
                query = query.or_(f"age.ilike.%4세%,age.ilike.%5세%,age.ilike.%6세%,age.ilike.%7세%,age.ilike.%{age}%")
            elif age == "8-12":
                query = query.or_(f"age.ilike.%8세%,age.ilike.%9세%,age.ilike.%10세%,age.ilike.%11세%,age.ilike.%12세%,age.ilike.%{age}%")
            elif age == "13+":
                query = query.or_(f"age.ilike.%13세%,age.ilike.%13%")
            else:
                query = query.ilike("age", f"%{age}%")
    
    # 정렬
    if sort == "title":
        query = query.order("title")
    else:  # 기본값: pangyo_callno
        query = query.order("pangyo_callno")
    
    # 페이지네이션
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)
    
    # 실행
    result = query.execute()
    
    return {
        "data": result.data,
        "total": result.count if hasattr(result, 'count') else len(result.data),
        "page": page,
        "limit": limit,
        "total_pages": (result.count + limit - 1) // limit if hasattr(result, 'count') and result.count else 1
    }
