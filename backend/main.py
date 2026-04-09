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
    ],
    allow_origin_regex=r"https://.*kids-library.*\.vercel\.app",  # Vercel Preview 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(books_router)
app.include_router(sync_router)
app.include_router(auth_router)
app.include_router(wishlists_router)


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


