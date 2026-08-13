"""도서 리뷰 & 공감 뱃지 API 라우터"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from collections import Counter
import logging
from core.database import supabase

router = APIRouter(prefix="/api/books", tags=["reviews"])
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 범용 10종 부모 공감 뱃지 정의 (상수)
# ──────────────────────────────────────────────
BADGE_LIST = [
    "🎨 그림체가 좋아요",
    "😆 깔깔 웃으며 무한 반복 요청해요",
    "📖 글밥이 적당해요",
    "🧠 호기심이 부쩍 늘었어요",
    "⭐ 우리 아이 최애 책이에요",
    "💬 아이와 대화거리가 풍부해져요",
    "💡 새로운 상상력을 자극해요",
    "📚 꼭 읽어볼 만해요",
    "☀️ 아이 혼자서도 잘 펼쳐봐요",
    "👏 아이 집중력이 엄청 높아져요",
]


# ──────────────────────────────────────────────
# Pydantic 모델
# ──────────────────────────────────────────────
class ReviewCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20, description="작성자 닉네임")
    child_age: Optional[str] = Field(None, max_length=10, description="자녀 연령 (예: 3세)")
    rating: float = Field(..., ge=1.0, le=5.0, description="평점 (1.0~5.0)")
    selected_badges: List[str] = Field(default=[], description="선택한 뱃지 목록")
    content: Optional[str] = Field(None, max_length=500, description="한줄평 본문")


class ReviewResponse(BaseModel):
    id: str
    book_id: int
    nickname: str
    child_age: Optional[str]
    rating: float
    selected_badges: List[str]
    content: Optional[str]
    created_at: str


class ReviewsAggregation(BaseModel):
    avg_rating: Optional[float]
    review_count: int
    badge_counts: dict  # { "🎨 그림체가 좋아요": 42, ... }
    reviews: List[dict]


# ──────────────────────────────────────────────
# GET /api/books/{book_id}/reviews
# ──────────────────────────────────────────────
@router.get("/{book_id}/reviews")
def get_book_reviews(book_id: int):
    """
    도서별 리뷰 목록, 평균 평점, 뱃지 득표수 집계 반환
    """
    try:
        result = (
            supabase.table("book_reviews")
            .select("*")
            .eq("book_id", book_id)
            .order("created_at", desc=True)
            .execute()
        )
        reviews = result.data or []

        # 평균 평점 계산
        ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

        # 뱃지 득표수 집계
        badge_counter = Counter()
        for r in reviews:
            badges = r.get("selected_badges") or []
            for badge in badges:
                badge_counter[badge] += 1

        # 정렬된 뱃지 집계 (득표수 내림차순)
        badge_counts = dict(badge_counter.most_common())

        return {
            "avg_rating": avg_rating,
            "review_count": len(reviews),
            "badge_counts": badge_counts,
            "reviews": reviews,
        }

    except Exception as e:
        logger.error(f"리뷰 조회 실패 (book_id={book_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="리뷰를 불러오는 데 실패했습니다."
        )


# ──────────────────────────────────────────────
# POST /api/books/{book_id}/reviews
# ──────────────────────────────────────────────
@router.post("/{book_id}/reviews", status_code=status.HTTP_201_CREATED)
def create_book_review(book_id: int, review: ReviewCreate):
    """
    도서에 부모 한줄평/뱃지 평가 등록
    """
    # 뱃지 유효성 검증
    for badge in review.selected_badges:
        if badge not in BADGE_LIST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 뱃지입니다: {badge}"
            )

    try:
        data = {
            "book_id": book_id,
            "nickname": review.nickname.strip(),
            "child_age": review.child_age.strip() if review.child_age else None,
            "rating": review.rating,
            "selected_badges": review.selected_badges,
            "content": review.content.strip() if review.content else None,
            "is_ai_generated": False,
        }

        result = supabase.table("book_reviews").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="리뷰 등록에 실패했습니다."
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"리뷰 등록 실패 (book_id={book_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="리뷰 등록 중 오류가 발생했습니다."
        )


# ──────────────────────────────────────────────
# GET /api/books/badges
# ──────────────────────────────────────────────
@router.get("/badges/list")
def get_badge_list():
    """범용 10종 부모 공감 뱃지 목록 반환"""
    return {"badges": BADGE_LIST}
