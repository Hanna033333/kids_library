"""도서 리뷰 & 공감 뱃지 API 라우터"""
import re
import time
import threading
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from collections import Counter, defaultdict
import logging
from core.database import supabase
from api.auth import get_current_user

router = APIRouter(prefix="/api/books", tags=["reviews"])
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 금지어 목록 (어린이 서비스 특화)
# ──────────────────────────────────────────────
_BANNED_WORDS = [
    # 욕설/비속어
    "씨발", "시발", "ㅅㅂ", "개새끼", "개새", "ㄱㅅㄲ", "지랄", "ㅈㄹ",
    "병신", "ㅂㅅ", "미친놈", "미친년", "미친새끼", "새끼", "년놈", "꺼져",
    "닥쳐", "죽어", "뒤져", "찐따", "장애인새끼",
    # 성적 표현
    "섹스", "야동", "포르노", "성관계", "변태", "강간", "성추행",
    # 광고/홍보 (URL, 전화번호 패턴은 정규식으로 별도 처리)
    "카카오톡", "텔레그램", "라인 아이디", "오픈채팅",
]

# 광고성 패턴 (정규식)
_SPAM_PATTERNS = [
    r"https?://",           # URL
    r"www\.",               # www 링크
    r"\d{2,4}-\d{3,4}-\d{4}",  # 전화번호
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # 이메일
    r"카카오톡\s*아이디",
    r"오픈\s*채팅",
]


def _check_banned_content(text: str):
    """금지어 및 광고성 패턴 검사 — 위반 시 HTTPException 발생"""
    if not text:
        return
    lower = text.lower()

    for word in _BANNED_WORDS:
        if word in lower:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="작성할 수 없는 내용이 포함되어 있습니다."
            )

    for pattern in _SPAM_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="링크나 연락처는 포함할 수 없습니다."
            )


# ──────────────────────────────────────────────
# 범용 10종 부모 공감 뱃지 정의 (상수)
# ──────────────────────────────────────────────
BADGE_LIST = [
    # 도서 특징 (프론트 badge_constants.ts 와 1:1 동기화)
    "🎨 그림체가 예뻐요",
    "📖 글밥이 적당해요",
    "💡 문장이 아름다워요",
    "💬 바른 습관을 도와줘요",
    "📚 교훈과 위안을 줘요",
    # 아이 반응
    "⭐ 아이 최애 책이에요",
    "😆 깔깔 웃고 좋아해요",
    "👏 몰입해서 집중해요",
    "☀️ 혼자서도 잘 봐요",
    "🧠 질문을 많이 해요",
    # ── 하위 호환: 이전 버전에서 저장된 뱃지 텍스트도 허용 ──
    "🎨 그림체가 좋아요",
    "😆 깔깔 웃으며 무한 반복 요청해요",
    "🧠 호기심이 부쩍 늘었어요",
    "⭐ 우리 아이 최애 책이에요",
    "💬 아이와 대화거리가 풍부해져요",
    "💡 새로운 상상력을 자극해요",
    "📚 꼭 읽어볼 만해요",
    "☀️ 아이 혼자서도 잘 펼쳐봐요",
    "👏 아이 집중력이 엄청 높아져요",
]

# ──────────────────────────────────────────────
# 간단한 인메모리 레이트리밋 (IP 기준)
# book_reviews INSERT를 anon 키로 직접 막아둔 대신(RLS), 백엔드 엔드포인트에도
# 최소한의 스팸 방지 장치를 둡니다. 프로세스 재시작 시 초기화되는 단순 구현이며,
# 다중 워커/인스턴스 환경에서는 워커별로 독립 카운트됩니다 — 완전한 방어가 아니라
# 명백한 어뷰징(수 초 간격 연타 등)을 걸러내기 위한 최소 장치입니다.
# ──────────────────────────────────────────────
_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_HISTORY: Dict[str, List[float]] = defaultdict(list)
_RATE_LIMIT_MIN_INTERVAL_SEC = 3          # 동일 IP 연속 요청 최소 간격
_RATE_LIMIT_MAX_PER_HOUR = 20             # 동일 IP 시간당 최대 리뷰 등록 수


def _check_rate_limit(client_ip: str):
    now = time.time()
    with _RATE_LIMIT_LOCK:
        history = _RATE_LIMIT_HISTORY[client_ip]
        # 1시간 이전 기록 정리
        history[:] = [t for t in history if now - t < 3600]

        if history and (now - history[-1]) < _RATE_LIMIT_MIN_INTERVAL_SEC:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="요청이 너무 빠릅니다. 잠시 후 다시 시도해 주세요.",
            )
        if len(history) >= _RATE_LIMIT_MAX_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="리뷰 등록 횟수 제한을 초과했습니다. 잠시 후 다시 시도해 주세요.",
            )
        history.append(now)


# ──────────────────────────────────────────────
# Pydantic 모델
# ──────────────────────────────────────────────
class ReviewCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20, description="작성자 닉네임")
    child_age: Optional[str] = Field(None, max_length=10, description="자녀 연령 (예: 3세)")
    rating: float = Field(..., ge=1.0, le=5.0, description="평점 (1.0~5.0)")
    selected_badges: List[str] = Field(default=[], description="선택한 뱃지 목록")
    content: Optional[str] = Field(None, min_length=10, max_length=500, description="한줄평 본문 (최소 10자)")


class ReviewUpdate(BaseModel):
    child_age: Optional[str] = Field(None, max_length=10)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    selected_badges: Optional[List[str]] = Field(None)
    content: Optional[str] = Field(None, min_length=10, max_length=500)


class ReviewResponse(BaseModel):
    id: str
    book_id: int
    nickname: str
    child_age: Optional[str]
    rating: float
    selected_badges: List[str]
    content: Optional[str]
    created_at: str
    is_ai_generated: bool = False


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
        raw_reviews = result.data or []

        formatted_reviews = []
        for r in raw_reviews:
            formatted_reviews.append({
                "id": str(r.get("id", "")),
                "book_id": r.get("book_id", book_id),
                "nickname": r.get("nickname") or "익명 부모님",
                "child_age": r.get("child_age") or None,
                "rating": float(r.get("rating", 5.0)),
                "selected_badges": r.get("selected_badges") or [],
                "content": r.get("content") or r.get("comment") or "",
                "created_at": str(r.get("created_at", "")),
                # AI가 생성한 예시 리뷰인지 여부. 실제 부모 후기와 구분해 프론트에서
                # "AI 생성 예시" 배지로 표시합니다.
                "is_ai_generated": bool(r.get("is_ai_generated", False)),
                "user_id": str(r["user_id"]) if r.get("user_id") else None,
            })

        # 리뷰가 아직 없는 경우 빈 목록 반환 (프론트엔드에서 깔끔한 Empty State UI 지원)
        if not formatted_reviews:
            return {
                "avg_rating": 0.0,
                "review_count": 0,
                "badge_counts": {},
                "reviews": [],
            }

        # 평균 평점 계산
        ratings = [r["rating"] for r in formatted_reviews if r.get("rating") is not None]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 5.0

        # 뱃지 득표수 집계
        badge_counter = Counter()
        for r in formatted_reviews:
            badges = r.get("selected_badges") or []
            for badge in badges:
                badge_counter[badge] += 1

        badge_counts = dict(badge_counter.most_common())

        return {
            "avg_rating": avg_rating,
            "review_count": len(formatted_reviews),
            "badge_counts": badge_counts,
            "reviews": formatted_reviews,
        }

    except Exception as e:
        logger.error(f"리뷰 조회 실패 (book_id={book_id}): {e}")
        # 조회 실패 시에도 프론트가 깨지지 않도록 빈 목록으로 응답하되, 반드시 에러 레벨로 로깅합니다.
        return {
            "avg_rating": 0.0,
            "review_count": 0,
            "badge_counts": {},
            "reviews": [],
        }


# ──────────────────────────────────────────────
# POST /api/books/{book_id}/reviews
# ──────────────────────────────────────────────
@router.post("/{book_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=ReviewResponse)
def create_book_review(book_id: int, review: ReviewCreate, request: Request, current_user=Depends(get_current_user)):
    """
    도서에 부모 리뷰/뱃지 평가 등록 (로그인 필수)
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    if re.search(r'\s', review.nickname):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="닉네임에 띄어쓰기를 포함할 수 없습니다."
        )

    # 금지어 및 광고성 패턴 검사
    _check_banned_content(review.nickname)
    if review.content:
        _check_banned_content(review.content)

    # 한줄평 최소 길이 검증 (작성 시 10자 이상)
    if review.content is not None and len(review.content.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한줄평은 최소 10자 이상 작성해 주세요."
        )

    # 뱃지 유효성 검증
    for badge in review.selected_badges:
        if badge not in BADGE_LIST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 뱃지입니다: {badge}"
            )

    # 존재하지 않는 book_id로 리뷰가 쌓이는 것을 방지
    book_exists = (
        supabase.table("childbook_items").select("id").eq("id", book_id).limit(1).execute()
    )
    if not book_exists.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 도서입니다."
        )

    # 동일 유저 중복 리뷰 방지
    duplicate_check = (
        supabase.table("book_reviews")
        .select("id")
        .eq("book_id", book_id)
        .eq("user_id", str(current_user.id))
        .limit(1)
        .execute()
    )
    if duplicate_check.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 이 책에 리뷰를 작성하셨습니다. 기존 리뷰를 수정해 주세요."
        )

    try:
        # 우선 신규 컬럼 명으로 insert 시도, 기존 스키마일 경우 comment 컬럼으로 인서트
        try:
            data = {
                "book_id": book_id,
                "user_id": str(current_user.id),
                "nickname": review.nickname.strip(),
                "child_age": review.child_age.strip() if review.child_age else None,
                "rating": review.rating,
                "selected_badges": review.selected_badges,
                "content": review.content.strip() if review.content else None,
                "is_ai_generated": False,
            }
            result = supabase.table("book_reviews").insert(data).execute()
        except Exception:
            data_legacy = {
                "book_id": book_id,
                "rating": int(review.rating),
                "comment": review.content.strip() if review.content else f"{review.nickname}님의 평점",
            }
            result = supabase.table("book_reviews").insert(data_legacy).execute()

        if not result.data:
            raise RuntimeError("Insert returned no data")

        saved = result.data[0]
        return {
            "id": str(saved.get("id", "")),
            "book_id": book_id,
            "nickname": review.nickname.strip(),
            "child_age": review.child_age.strip() if review.child_age else None,
            "rating": review.rating,
            "selected_badges": review.selected_badges,
            "content": review.content.strip() if review.content else None,
            "created_at": str(saved.get("created_at", "방금 전")),
            "is_ai_generated": False,
        }

    except HTTPException:
        raise
    except Exception as e:
        # 저장에 실패했는데 성공한 것처럼 응답하면 사용자는 "등록 완료"로 착각하지만
        # 실제로는 DB에 아무것도 남지 않습니다. 반드시 실패를 알립니다.
        logger.error(f"리뷰 등록 실패 (book_id={book_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="리뷰 등록에 실패했습니다. 잠시 후 다시 시도해 주세요."
        )


# ──────────────────────────────────────────────
# PATCH /api/books/{book_id}/reviews/{review_id}
# ──────────────────────────────────────────────
@router.patch("/{book_id}/reviews/{review_id}", status_code=status.HTTP_200_OK)
def update_book_review(book_id: int, review_id: str, review: ReviewUpdate, current_user=Depends(get_current_user)):
    """
    본인 리뷰 수정 (로그인 필수, 본인 작성 리뷰만 가능)
    """
    # 리뷰 존재 및 본인 확인
    existing = supabase.table("book_reviews").select("id, user_id").eq("id", review_id).eq("book_id", book_id).execute()
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리뷰를 찾을 수 없습니다.")
    if existing.data[0].get("user_id") != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인이 작성한 리뷰만 수정할 수 있습니다.")

    update_data = {}
    if review.child_age is not None:
        update_data["child_age"] = review.child_age.strip()
    if review.rating is not None:
        update_data["rating"] = review.rating
    if review.selected_badges is not None:
        for badge in review.selected_badges:
            if badge not in BADGE_LIST:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"유효하지 않은 뱃지입니다: {badge}")
        update_data["selected_badges"] = review.selected_badges
    if review.content is not None:
        if len(review.content.strip()) < 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="한줄평은 최소 10자 이상 작성해 주세요.")
        _check_banned_content(review.content)
        update_data["content"] = review.content.strip()

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

    try:
        result = supabase.table("book_reviews").update(update_data).eq("id", review_id).execute()
        return {"success": True, "data": result.data[0] if result.data else {}}
    except Exception as e:
        logger.error(f"리뷰 수정 실패 (review_id={review_id}): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="리뷰 수정에 실패했습니다.")


# ──────────────────────────────────────────────
# DELETE /api/books/{book_id}/reviews/{review_id}
# ──────────────────────────────────────────────
@router.delete("/{book_id}/reviews/{review_id}", status_code=status.HTTP_200_OK)
def delete_book_review(book_id: int, review_id: str, current_user=Depends(get_current_user)):
    """
    본인 리뷰 삭제 (로그인 필수, 본인 작성 리뷰만 가능)
    """
    # 리뷰 존재 및 본인 확인
    existing = supabase.table("book_reviews").select("id, user_id").eq("id", review_id).eq("book_id", book_id).execute()
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리뷰를 찾을 수 없습니다.")
    if existing.data[0].get("user_id") != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인이 작성한 리뷰만 삭제할 수 있습니다.")

    try:
        supabase.table("book_reviews").delete().eq("id", review_id).execute()
        return {"success": True}
    except Exception as e:
        logger.error(f"리뷰 삭제 실패 (review_id={review_id}): {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="리뷰 삭제에 실패했습니다.")


# ──────────────────────────────────────────────
# GET /api/books/my-reviews  (로그인 유저가 별점 남긴 책 목록)
# ──────────────────────────────────────────────
@router.get("/my-reviews")
def get_my_reviews(current_user=Depends(get_current_user)):
    """
    내가 별점을 남긴 책 목록 반환 (로그인 필수)
    동일 책에 여러 리뷰가 있으면 가장 최근 리뷰 1개만 포함.
    """
    try:
        # 1. 현재 유저의 리뷰 조회 (최신순)
        reviews_result = (
            supabase.table("book_reviews")
            .select("id, book_id, rating, content, selected_badges, created_at")
            .eq("user_id", str(current_user.id))
            .order("created_at", desc=True)
            .execute()
        )
        reviews = reviews_result.data or []
        if not reviews:
            return {"rated_books": []}

        # 2. 중복 book_id 제거 (최신 리뷰만 유지)
        seen_book_ids: set = set()
        deduped = []
        for r in reviews:
            bid = r.get("book_id")
            if bid not in seen_book_ids:
                seen_book_ids.add(bid)
                deduped.append(r)

        book_ids = [r["book_id"] for r in deduped]

        # 3. 책 정보 일괄 조회
        books_result = (
            supabase.table("childbook_items")
            .select("id, title, author, publisher, isbn, image_url, age, category, curation_tag, description, national_loan_count")
            .in_("id", book_ids)
            .execute()
        )
        books_map = {b["id"]: b for b in (books_result.data or [])}

        # 4. 리뷰 + 책 정보 병합
        rated_books = []
        for r in deduped:
            bid = r["book_id"]
            book = books_map.get(bid, {})
            rated_books.append({
                "review_id": str(r.get("id", "")),
                "book_id": bid,
                "rating": float(r.get("rating", 0)),
                "created_at": str(r.get("created_at", "")),
                # 책 메타데이터 (Book 타입 호환)
                "id": bid,
                "title": book.get("title") or "제목 없음",
                "author": book.get("author"),
                "publisher": book.get("publisher"),
                "isbn": book.get("isbn"),
                "image_url": book.get("image_url"),
                "age": book.get("age"),
                "category": book.get("category"),
                "curation_tag": book.get("curation_tag"),
                "description": book.get("description"),
                "national_loan_count": book.get("national_loan_count"),
                "pangyo_callno": None,
                "vol": None,
            })

        return {"rated_books": rated_books}

    except Exception as e:
        logger.error(f"내 리뷰 조회 실패 (user_id={current_user.id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="리뷰 목록을 불러오는 데 실패했습니다."
        )


# ──────────────────────────────────────────────
# GET /api/books/badges
# ──────────────────────────────────────────────
@router.get("/badges/list")
def get_badge_list():
    """범용 10종 부모 공감 뱃지 목록 반환"""
    return {"badges": BADGE_LIST}
