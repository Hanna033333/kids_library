import sys
import os

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

app = FastAPI(
    title="Kids Library API",
    description="어린이 도서 추천 및 검색 API",
    version="1.0.0"
)

# CORS 설정 (보안 강화: 특정 도메인만 허용)
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
    allow_origin_regex=r"https://.*kids-library.*\.vercel\.app",  # Vercel Preview 허용
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


@app.on_event("startup")
async def startup_event():
    import asyncio
    from api.threads import weekly_threads_scheduler, telegram_feedback_listener
    asyncio.create_task(weekly_threads_scheduler())
    asyncio.create_task(telegram_feedback_listener())

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


