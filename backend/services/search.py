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
    # count="exact" 사용으로 정확한 개수 반환
    query = supabase.table("childbook_items").select("*", count="exact")
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    
    # 숨김 처리된 책 제외
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    
    # 카테고리 필터링
    if category and category != "전체":
        query = query.eq("category", category)
    
    # 검색어 필터링 (제목 또는 저자에 검색어 포함)
    if q:
        q = q.strip()
        if q:
            # OR는 title/author 내부에만 적용, 전체 쿼리와는 AND로 결합
            query = query.or_(f"title.ilike.%{q}%,author.ilike.%{q}%")
    
    # 연령 필터링 (각 연령대별 OR는 유지하되, 전체 쿼리와는 AND로 결합)
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
    # 필요한 컬럼만 선택 (성능 최적화)
    columns = "id,title,author,publisher,pangyo_callno,vol,category,age,image_url"
    
    # 쿼리 빌드 - estimated count 사용 (훨씬 빠름)
    query = supabase.table("childbook_items").select(columns, count="estimated")
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    
    # 카테고리 필터링
    if category and category != "전체":
        query = query.eq("category", category)
    
    # 검색어 필터링 (제목 또는 저자에 검색어 포함)
    if q:
        q = q.strip()
        if q:
            # OR는 title/author 내부에만 적용, 전체 쿼리와는 AND로 결합
            query = query.or_(f"title.ilike.%{q}%,author.ilike.%{q}%")
    
    # 연령 필터링 - 괄호로 감싸서 AND 조건으로 결합
    if age:
        age = age.strip()
        if age:
            age_conditions = []
            if age == "0-3":
                # 0세, 1세, 2세, 3세 (유아 제외 - 4세 이상 수준)
                age_conditions = ["age.ilike.%0세%", "age.ilike.%1세%", "age.ilike.%2세%", "age.ilike.%3세%"]
            elif age == "4-7":
                # 3세, 4세, 5세, 6세, 7세, 유아 포함 (범위 확대)
                age_conditions = ["age.ilike.%3세%", "age.ilike.%4세%", "age.ilike.%5세%", "age.ilike.%6세%", "age.ilike.%7세%", "age.ilike.%유아%"]
            elif age == "8-12":
                # 7세, 8세, 9세, 10세, 11세, 12세 포함 (범위 확대)
                age_conditions = ["age.ilike.%7세%", "age.ilike.%8세%", "age.ilike.%9세%", "age.ilike.%10세%", "age.ilike.%11세%", "age.ilike.%12세%"]
            elif age == "13+":
                # 11세부터, 13세부터, 16세부터를 포함
                age_conditions = ["age.ilike.%11세%", "age.ilike.%13세%", "age.ilike.%16세%"]
            else:
                age_conditions = [f"age.ilike.%{age}%"]
            
            if age_conditions:
                # OR 조건을 괄호로 감싸서 적용
                query = query.or_(",".join(age_conditions))
    
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







