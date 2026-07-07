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
    ],
    # Starlette의 CORSMiddleware가 부분 일치(re.match)로 체크할 경우를 대비하여 명확히 ^과 $ 앵커를 사용하여 앞뒤 제한
    allow_origin_regex=r"^(https://kids-library-git-[a-z0-9-]+-hannas-projects-[a-z0-9]+\.vercel\.app|https://(www\.)?checkjari\.com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Validation (422) 에러 로그 출력을 위한 전역 핸들러 추가
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("⚠️ Request Validation Error Detected!")
    try:
        body = await request.body()
        print(f"👉 Request Body: {body.decode('utf-8')}")
    except Exception as e:
        print(f"❌ Failed to read request body: {e}")
    print(f"👉 Errors Details: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )

# 라우터 등록
app.include_router(books_router)
app.include_router(sync_router)
app.include_router(auth_router)
app.include_router(wishlists_router)
app.include_router(threads_router)

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
