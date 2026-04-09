"""
찜하기(Wishlist) API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/wishlists", tags=["wishlists"])
security = HTTPBearer()

# Supabase 클라이언트
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


# ============================================
# Pydantic 모델
# ============================================

class BookInfo(BaseModel):
    id: int
    title: str
    author: str
    cover_image: str
    callno: str


class WishlistItem(BaseModel):
    id: int
    book: BookInfo
    created_at: datetime


class WishlistResponse(BaseModel):
    data: List[WishlistItem]
    total: int
    page: int
    limit: int


class AddWishlistRequest(BaseModel):
    book_id: int


class CheckWishlistRequest(BaseModel):
    book_ids: List[int]


# ============================================
# 인증 헬퍼 함수
# ============================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰에서 현재 사용자 정보 추출"""
    token = credentials.credentials
    
    # QA 전용 테스터 토큰 처리
    if token == "TEST_QA_TOKEN" and os.getenv("ENV") != "production":
        from types import SimpleNamespace
        print("[DEBUG] QA Tester Token detected in Wishlists")
        return SimpleNamespace(
            id="00000000-0000-0000-0000-000000000000",
            email="qa-tester@checkjari.com",
            app_metadata={'provider': 'kakao'},
            user_metadata={'provider_id': 'qa-tester-001'}
        )

    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


# ============================================
# API 엔드포인트
# ============================================

@router.get("", response_model=WishlistResponse)
async def get_wishlists(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """찜 목록 조회"""
    # QA 전용 테스터 처리
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {
            "data": [],
            "total": 0,
            "page": page,
            "limit": limit
        }

    try:
        offset = (page - 1) * limit
        
        # 찜 목록 조회 (책 정보 JOIN)
        response = supabase.table("wishlists").select(
            "id, created_at, book:childbook_items(id, title, author, cover_image, callno)"
        ).eq("user_id", current_user.id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        # 전체 개수 조회
        count_response = supabase.table("wishlists").select("id", count="exact").eq("user_id", current_user.id).execute()
        total = count_response.count
        
        return {
            "data": response.data,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wishlists: {str(e)}"
        )


@router.post("")
async def add_wishlist(
    request: AddWishlistRequest,
    current_user = Depends(get_current_user)
):
    """찜 추가"""
    # QA 전용 테스터 처리
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {"id": 0, "user_id": current_user.id, "book_id": request.book_id, "created_at": datetime.now()}

    try:
        response = supabase.table("wishlists").insert({
            "user_id": current_user.id,
            "book_id": request.book_id
        }).execute()
        
        return response.data[0]
    except Exception as e:
        # 중복 에러 처리
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book already in wishlist"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add wishlist: {str(e)}"
        )


@router.delete("/{wishlist_id}")
async def remove_wishlist(
    wishlist_id: int,
    current_user = Depends(get_current_user)
):
    """찜 삭제"""
    # QA 전용 테스터 처리
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {"message": "Wishlist item removed (QA Mock)"}

    try:
        # 본인의 찜인지 확인 (RLS가 자동으로 처리하지만 명시적으로 체크)
        response = supabase.table("wishlists").delete().eq("id", wishlist_id).eq("user_id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist item not found"
            )
        
        return {"message": "Wishlist item removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove wishlist: {str(e)}"
        )


@router.post("/check", response_model=Dict[str, bool])
async def check_wishlists(
    request: CheckWishlistRequest,
    current_user = Depends(get_current_user)
):
    """찜 여부 확인 (여러 책 동시)"""
    # QA 전용 테스터 처리
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {str(book_id): False for book_id in request.book_ids}

    try:
        response = supabase.table("wishlists").select("book_id").eq("user_id", current_user.id).in_("book_id", request.book_ids).execute()
        
        wishlisted_book_ids = {item["book_id"] for item in response.data}
        
        return {str(book_id): book_id in wishlisted_book_ids for book_id in request.book_ids}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check wishlists: {str(e)}"
        )
