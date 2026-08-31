import sys
import os
from contextlib import asynccontextmanager

# Add current directory (backend) to sys.path to ensure 'services', 'api', etc. are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.books import router as books_router
from api.sync import router as sync_router
from api.auth import router as auth_router
from api.wishlists import router as wishlists_router
from api.threads import router as threads_router
from api.reviews import router as reviews_router

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 백그라운드 태스크 실행 및 토큰 보장
    import asyncio
    from api.threads import ensure_threads_admin_token, weekly_threads_scheduler, telegram_feedback_listener
    
    ensure_threads_admin_token()
    scheduler_task = asyncio.create_task(weekly_threads_scheduler())
    listener_task = asyncio.create_task(telegram_feedback_listener())
    
    yield
    
    # Shutdown: 백그라운드 태스크 취소 및 리소스 정리
    scheduler_task.cancel()
    listener_task.cancel()
    try:
        await asyncio.gather(scheduler_task, listener_task, return_exceptions=True)
    except Exception as e:
        print(f"Error during background task cancellation: {e}")

app = FastAPI(
    title="Kids Library API",
    description="어린이 도서 추천 및 검색 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (보안 강화: 특정 도메인만 허용 및 엄격한 정규식 매칭)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://checkjari.com",
        "https://www.checkjari.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3003",
        "http://localhost:3004",
        "http://127.0.0.1:3004",
    ],
    # Starlette CORSMiddleware regex: Vercel Preview 및 상용 도메인 허용
    # 기존에는 "kids-library-*.vercel.app"(어느 팀이든 이 이름으로 프로젝트를 만들면 매치)와
    # "*-hannas-projects*.vercel.app"(이 팀 소속이면 프로젝트명 무관하게 매치)를 독립적으로
    # 허용해, 제3자가 "kids-library-xxx.vercel.app" 프로젝트를 만드는 것만으로도
    # allow_credentials=True 상태에서 자격증명 포함 CORS 요청이 통과할 수 있었습니다.
    # 이 프로젝트(kids-library)의 실제 팀(hannas-projects) 소속 프리뷰 URL만 매치하도록
    # 두 조건을 하나의 패턴으로 결합해 범위를 좁혔습니다.
    allow_origin_regex=r"^(https://kids-library-git-[a-z0-9-]+-hannas-projects-[a-z0-9]+\.vercel\.app|https://(www\.)?checkjari\.com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Validation (422) 에러 로그 출력을 위한 전역 핸들러
# 주의: 요청 본문 전체를 로그/응답에 그대로 남기면 회원가입/프로필 수정 같은 요청의
# 이메일·닉네임 등 개인정보가 Render 로그와 클라이언트 응답에 평문으로 노출됩니다.
# 어떤 필드가, 어떤 타입 에러로 실패했는지만 남기고 원본 값은 남기지 않습니다.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_summaries = [
        {"field": ".".join(str(p) for p in err.get("loc", [])), "type": err.get("type")}
        for err in exc.errors()
    ]
    print(f"⚠️ Request Validation Error: {request.method} {request.url.path} -> {error_summaries}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# 라우터 등록
app.include_router(books_router)
app.include_router(sync_router)
app.include_router(auth_router)
app.include_router(wishlists_router)
app.include_router(threads_router)
app.include_router(reviews_router)

@app.get("/")
def read_root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "Kids Library API",
        "version": "1.0.0",
        "docs": "/docs"
    }
