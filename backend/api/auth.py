"""
회원 인증 및 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import logging
import re
from core.database import supabase

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# ============================================
# Pydantic 모델
# ============================================

class UserResponse(BaseModel):
    id: str
    email: str
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    provider: str
    agreed_to_terms: bool
    agreed_to_privacy: bool
    agreed_to_marketing: bool
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    agreed_to_marketing: Optional[bool] = None


class AgreementsRequest(BaseModel):
    agreed_to_terms: bool
    agreed_to_privacy: bool
    agreed_to_marketing: bool = False
    nickname: Optional[str] = None


# ============================================
# 인증 헬퍼 함수
# ============================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰에서 현재 사용자 정보 추출"""
    token = credentials.credentials
    
    # QA 전용 테스터 토큰 처리 (development 모드이거나 모의 환경이 명시적으로 켜졌을 때만 활성화)
    is_qa_allowed = os.getenv("ENV") == "development" or os.getenv("ALLOW_QA_MOCK") == "true"
    if token == "TEST_QA_TOKEN" and is_qa_allowed:
        from types import SimpleNamespace
        logger.info("QA Tester Token detected")
        return SimpleNamespace(
            id="00000000-0000-0000-0000-000000000000",
            email="qa-tester@checkjari.com",
            app_metadata={"provider": "email"},
            user_metadata={"provider_id": "00000000-0000-0000-0000-000000000000"}
        )

    try:
        # Supabase Auth로 토큰 검증
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            logger.warning("get_user returned None or User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자 인증에 실패했습니다."
            )
        return user_response.user
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )


# ============================================
# API 엔드포인트
# ============================================

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user)):
    """내 정보 조회"""
    # QA 전용 테스터 처리
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {
            "id": current_user.id,
            "email": current_user.email,
            "nickname": "QA테스터",
            "profile_image_url": None,
            "provider": "kakao",
            "agreed_to_terms": True,
            "agreed_to_privacy": True,
            "agreed_to_marketing": False,
            "created_at": datetime.now()
        }

    try:
        response = supabase.table("members").select("*").eq("id", current_user.id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"User profile fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자 정보를 찾을 수 없습니다."
        )


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    profile: UpdateProfileRequest,
    current_user = Depends(get_current_user)
):
    """내 정보 수정"""
    if profile.nickname and re.search(r'\s', profile.nickname):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="닉네임에 띄어쓰기를 포함할 수 없습니다."
        )

    try:
        update_data = profile.dict(exclude_unset=True)
        
        # QA 전용 테스터는 모의 성공 데이터 반환
        if current_user.id == "00000000-0000-0000-0000-000000000000":
            return {
                "id": current_user.id,
                "email": current_user.email,
                "nickname": profile.nickname or "QA테스터",
                "profile_image_url": None,
                "provider": "email",
                "agreed_to_terms": True,
                "agreed_to_privacy": True,
                "agreed_to_marketing": False,
                "created_at": datetime.now()
            }

        response = supabase.table("members").update(update_data).eq("id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 수정에 실패했습니다."
        )


@router.post("/me/agreements")
async def update_agreements(
    agreements: AgreementsRequest,
    current_user = Depends(get_current_user)
):
    """약관 동의 및 닉네임 업데이트"""
    
    # 🔒 필수 약관 미동의 시 DB 저장 원천 차단
    if not agreements.agreed_to_terms or not agreements.agreed_to_privacy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="서비스 이용약관 및 개인정보 수집·이용에 동의하셔야 합니다."
        )
    
    try:
        # 사용자 메타데이터에서 provider 정보 추출
        app_metadata = current_user.app_metadata or {}
        user_metadata = current_user.user_metadata or {}
        
        provider = app_metadata.get('provider', 'email')
        provider_id = user_metadata.get('provider_id', str(current_user.id))
        
        # upsert 데이터 준비 (nickname=None이면 NULL로 저장 — Step 5에서 PATCH로 업데이트됨)
        data = {
            "id": current_user.id,
            "email": current_user.email,
            "provider": provider,
            "provider_id": provider_id,
            "agreed_to_terms": True,
            "agreed_to_privacy": True,
            "agreed_to_marketing": agreements.agreed_to_marketing,
            "updated_at": "now()"
        }
        if agreements.nickname is not None:
            data["nickname"] = agreements.nickname
        
        # QA 전용 테스터는 실제 DB 저장을 스킵하여 외래키 제약조건 위반 방지
        if current_user.id == "00000000-0000-0000-0000-000000000000":
            return {"message": "Agreements updated successfully (QA Mock)"}

        response = supabase.table("members").upsert(data).execute()
        
        if not response.data:
            logger.error("Response data is empty after upsert!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="약관 동의 업데이트에 실패했습니다."
            )
        
        return {"message": "Agreements updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agreements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="약관 동의 업데이트에 실패했습니다."
        )


@router.delete("/me")
async def delete_my_account(current_user = Depends(get_current_user)):
    """회원 탈퇴"""
    if current_user.id == "00000000-0000-0000-0000-000000000000":
        return {"message": "Account deleted successfully (QA Mock)"}
        
    try:
        # members 테이블에서 삭제 (CASCADE로 wishlists도 자동 삭제)
        supabase.table("members").delete().eq("id", current_user.id).execute()
        
        # Supabase Auth에서도 사용자 삭제
        supabase.auth.admin.delete_user(current_user.id)
        
        return {"message": "Account deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 탈퇴 처리에 실패했습니다."
        )
