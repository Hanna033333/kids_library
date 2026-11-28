"""전국 공공도서관 검색 API 라우터"""
from typing import Optional
from fastapi import APIRouter, Query
from services.library_registry import search_libraries

router = APIRouter(prefix="/api/libraries", tags=["libraries"])


@router.get("")
def list_libraries(
    q: Optional[str] = Query(None, description="도서관명 또는 주소/동네명 검색어"),
    region: Optional[str] = Query(None, description="시/도 필터 (예: 서울, 경기, 부산)"),
    lat: Optional[float] = Query(None, description="현재 위도 (가까운 순 정렬)"),
    lng: Optional[float] = Query(None, description="현재 경도 (가까운 순 정렬)"),
    limit: int = Query(30, ge=1, le=100, description="최대 반환 개수"),
):
    """전국 1,600+ 공공도서관 검색 및 내 주변 도서관 조회"""
    return search_libraries(q=q, region=region, lat=lat, lng=lng, limit=limit)

