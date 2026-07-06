"""책 검색 서비스"""
from core.database import supabase
from typing import Optional

def search_books_service(
    q: Optional[str] = None,
    age: Optional[str] = None,
    category: Optional[str] = None,
    curation: Optional[str] = None,
    sort: str = "pangyo_callno",
    page: int = 1,
    limit: int = 20,
    include_library_info: bool = False
):
    """
    책 검색 및 필터링 서비스
    """
    # 필요한 컬럼만 선택 (성능 최적화 및 다중 도서관 정보 조인)
    columns = "id,title,author,publisher,pangyo_callno,vol,category,age,image_url,curation_tag,curation_note,confidence_score,national_loan_count"
    if include_library_info:
        columns += ",library_info:book_library_info(library_name, callno)"
    
    # 쿼리 빌드 - 정확한 개수 반환 및 PMF 지표 확보를 위해 count="exact" 복원
    query = supabase.table("childbook_items").select(columns, count="exact")
    query = query.not_.is_("pangyo_callno", "null")
    query = query.neq("pangyo_callno", "없음")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    
    # 카테고리 필터링
    if category and category != "전체":
        query = query.eq("category", category)
        
    # 큐레이션 필터링
    if curation:
        curation = curation.strip()
        if curation:
            curation_mapping = {
                '겨울방학': '겨울방학2026',
                'winter-vacation': '겨울방학2026',
                '어린이도서연구회': '어린이도서연구회',
                'research-council': '어린이도서연구회'
            }
            db_curation_tag = curation_mapping.get(curation, curation)
            special_tags = ['겨울방학2026', '어린이도서연구회', 'caldecott']
            
            if db_curation_tag in special_tags:
                query = query.ilike('curation_tag', f'%{db_curation_tag}%')
            else:
                or_filter = f'curation_tag.eq."{db_curation_tag}",curation_tag.like."{db_curation_tag},%",curation_tag.eq."#{db_curation_tag}",curation_tag.like."#{db_curation_tag},%"'
                query = query.or_(or_filter)
    
    # 검색어 필터링 (제목 또는 저자에 검색어 포함)
    # PostgREST ParserError 방지를 위해 검색어 q 내의 쉼표(,) 및 큰따옴표(") 이스케이프 및 인용 처리 적용
    if q:
        q = q.strip()
        if q:
            safe_q = q.replace('"', '\\"').replace(',', '\\,')
            query = query.or_(f'title.ilike."%{safe_q}%",author.ilike."%{safe_q}%"')
    
    # 연령 필터링 - 괄호로 감싸서 AND 조건으로 결합
    if age:
        age = age.strip()
        if age:
            age_conditions = []
            if age == "0-3":
                age_conditions = ["age.eq.0세부터", "age.eq.1세부터", "age.eq.2세부터", "age.eq.3세부터", "age.eq.0-3"]
            elif age == "4-7":
                age_conditions = ["age.eq.4세부터", "age.eq.5세부터", "age.eq.6세부터", "age.eq.7세부터", "age.eq.4-7", "age.ilike.%유아%"]
            elif age == "8-12":
                age_conditions = ["age.eq.8세부터", "age.eq.9세부터", "age.eq.10세부터", "age.eq.11세부터", "age.eq.12세부터", "age.eq.8-12"]
            elif age == "13+" or age == "teen":
                age_conditions = ["age.eq.13세부터", "age.eq.16세부터", "age.eq.13+", "age.eq.teen"]
            else:
                age_conditions = [f"age.ilike.%{age}%"]
            
            if age_conditions:
                # OR 조건을 괄호로 감싸서 적용
                query = query.or_(",".join(age_conditions))
    
    # 정렬
    if sort == "title":
        query = query.order("title")
    elif sort == "confidence_score_desc":
        query = query.order("confidence_score", desc=True)
    else:  # 기본값: pangyo_callno
        query = query.order("pangyo_callno")

    # 페이지네이션
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)
    
    # 실행
    result = query.execute()
    
    total = result.count if hasattr(result, 'count') and result.count is not None else len(result.data)
    
    return {
        "data": result.data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total else 1
    }
