from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.books import router as books_router
from api.sync import router as sync_router

app = FastAPI(
    title="Kids Library API",
    description="어린이 도서 추천 및 검색 API",
    version="1.0.0"
)

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(books_router)
app.include_router(sync_router)


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
