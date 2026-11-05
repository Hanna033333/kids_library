"""책 검색 서비스"""
from core.database import supabase
from typing import Optional

AGE_VALUES = {
    "0-3": ["0-3", "0~3세", "0-2세", "3세부터"],
    "4-7": ["4-7", "4~7세", "5세부터", "7세부터"],
    "8-12": ["8-12", "8~12세", "8세부터", "9세부터"],
    "13+": ["13+"],
    "teen": ["13+"],
}

SPECIAL_CURATION_PARAMS = {
    "caldecott", "winter-vacation", "겨울방학", "summer-vacation", "여름방학",
    "여름방학2026", "research-council", "어린이도서연구회", "textbook", "교과서수록",
}

def search_books_service(
    q: Optional[str] = None,
    age: Optional[str] = None,
    category: Optional[str] = None,  # deprecated — 하위 호환용, 무시됨
    curation: Optional[str] = None,
    sort: str = "title",
    page: int = 1,
    limit: int = 20,
    include_library_info: bool = False,
    tag: Optional[str] = None,
    library: Optional[str] = None
):
    """
    책 검색 및 필터링 서비스
    """
    # 필요한 컬럼만 선택 (성능 최적화 및 다중 도서관 정보 조인)
    columns = "id,title,author,publisher,vol,category,age,image_url,curation_tag,curation_note,confidence_score,national_loan_count"
    if include_library_info:
        columns += ",library_info:book_library_info(library_name, callno)"
    
    # 쿼리 빌드 - 정확한 개수 반환 및 PMF 지표 확보를 위해 count="exact" 복원
    query = supabase.table("childbook_items").select(columns, count="exact")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")
    query = query.not_.ilike("image_url", "%noimg%")
    
    # category 필터링 제거됨 (큐레이션 태그 체계로 대체)
        
    # 큐레이션 필터링
    if curation:
        curation = curation.strip()
        if curation:
            curation_mapping = {
                '겨울방학': '겨울방학2026',
                'winter-vacation': '겨울방학2026',
                '여름방학': '여름방학2026',
                'summer-vacation': '여름방학2026',
                '어린이도서연구회': '어린이도서연구회',  # Backward compatibility
                'research-council': '어린이도서연구회',
                '교과서수록': '교과서수록',
                'textbook': '교과서수록'
            }
            db_curation_tag = curation_mapping.get(curation, curation)
            special_tags = ['겨울방학2026', '여름방학2026', '어린이도서연구회', 'caldecott', '교과서수록']
            
            # curation 파라미터 내의 쉼표/큰따옴표/백슬래시 이스케이프 및 인용 처리 적용
            safe_curation = db_curation_tag.replace('\\', '\\\\').replace('"', '\\"').replace(',', '\\,')
            
            if db_curation_tag in special_tags:
                query = query.ilike('curation_tag', f'%{safe_curation}%')
            else:
                or_filter = f'curation_tag.eq."{safe_curation}",curation_tag.like."{safe_curation},%",curation_tag.eq."#{safe_curation}",curation_tag.like."#{safe_curation},%"'
                query = query.or_(or_filter)

    # 태그 필터링 (교과서 수록도서 학년 등)
    if tag:
        tag = tag.strip().lstrip("#")
        if tag:
            safe_tag = tag.replace('\\', '\\\\').replace('"', '\\"').replace(',', '\\,')
            query = query.ilike('curation_tag', f'%{safe_tag}%')
    
    # 검색어 필터링 (제목 또는 저자에 검색어 포함)
    # 한국어 띄어쓰기 불일치 대응: 토큰별 AND 검색
    # 예) "수다쟁이 숲" → "수다쟁이" 포함 AND "숲" 포함 → "수다쟁이숲에 놀러와!" 히트
    # PostgREST ParserError 방지를 위해 검색어 q 내의 백슬래시(\), 쉼표(,) 및 큰따옴표(") 이스케이프 및 인용 처리 적용
    if q:
        q = q.strip()
        tokens = [t for t in q.split() if t]
        for token in tokens:
            safe_token = token.replace('\\', '\\\\').replace('"', '\\"').replace(',', '\\,')
            query = query.or_(
                f'title.ilike."%{safe_token}%",'
                f'author.ilike."%{safe_token}%",'
                f'publisher.ilike."%{safe_token}%",'
                f'curation_tag.ilike."%{safe_token}%"'
            )
    
    # 프론트 AGE_MAP과 동일한 레거시 값까지 한 곳에서 처리합니다.
    if age:
        age = age.strip()
        if age:
            age_values = AGE_VALUES.get(age, [age])
            query = query.in_("age", age_values)
    
    # 정렬
    is_callno_sort = sort in ("callno", "pangyo_callno")
    if is_callno_sort and (age or curation in SPECIAL_CURATION_PARAMS) and not library:
        is_callno_sort = False
        sort = "title"

    if is_callno_sort:
        target_library = (library or "판교도서관").strip()
        # 도서관별 청구기호순 정렬: book_library_info의 해당 도서관 callno 오름차순 (소장 도서 우선, 미소장 도서는 뒤로)
        result = query.order("title").execute()
        all_rows = result.data or []
        total = len(all_rows)
        if all_rows:
            book_ids = [r["id"] for r in all_rows]
            callno_map = {}
            for i in range(0, len(book_ids), 500):
                chunk = book_ids[i:i + 500]
                lib_res = supabase.table("book_library_info") \
                    .select("book_id, callno") \
                    .eq("library_name", target_library) \
                    .in_("book_id", chunk) \
                    .execute()
                for item in (lib_res.data or []):
                    cn = (item.get("callno") or "").strip()
                    if cn and cn != "없음":
                        callno_map[item["book_id"]] = cn

            all_rows.sort(key=lambda r: (
                0 if r["id"] in callno_map else 1,
                callno_map.get(r["id"], ""),
                r.get("title") or ""
            ))
        offset = (page - 1) * limit
        paged_data = all_rows[offset:offset + limit]
        return {
            "data": paged_data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total else 1
        }

    if sort == "confidence_score_desc":
        query = query.order("confidence_score", desc=True)
    elif sort in {"popular", "national_loan_count", "national_loan_count_desc"}:
        query = query.order("national_loan_count", desc=True, nullsfirst=False)
    else:  # 기본값: title (ㄱㄴㄷ순)
        query = query.order("title")

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
