"""책 검색 서비스"""
from core.database import supabase
from typing import Optional


def build_search_query(
    q: Optional[str] = None,
    age: Optional[str] = None,
    category: Optional[str] = None,
    sort: str = "pangyo_callno"
):
    """
    책 검색 쿼리 빌더
    - pangyo_callno가 있는 책만 필터링
    - 검색어, 연령, 카테고리 필터링
    - 정렬
    """
    # 기본 쿼리: pangyo_callno가 있는 책만
    # count="planned" 사용으로 성능 최적화 (예상 개수 사용)
    query = supabase.table("childbook_items").select("*", count="planned")
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    
    # 카테고리 필터링
    if category and category != "전체":
        query = query.eq("category", category)
    
    # 검색어 필터링
    if q:
        q = q.strip()
        if q:
            query = query.or_(f"title.ilike.%{q}%,author.ilike.%{q}%")
    
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
    
    return query


def search_books_service(
    q: Optional[str] = None,
    age: Optional[str] = None,
    category: Optional[str] = None,
    sort: str = "pangyo_callno",
    page: int = 1,
    limit: int = 20
):
    """
    책 검색 및 필터링 서비스
    """
    # 쿼리 빌드
    query = build_search_query(q=q, age=age, category=category, sort=sort)
    
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






