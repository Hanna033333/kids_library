import sys
import os

# Add current directory (backend) to sys.path to ensure 'services', 'api', etc. are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

@app.get("/check-ip")
async def check_ip():
    """
    서버의 외부 IP 확인 (Render 배포 시 IP 등록용)
    """
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=json") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"ip": data.get("ip"), "message": "이 IP를 도서관 API 센터에 등록하세요."}
                return {"error": "IP 확인 실패"}
    except Exception as e:
        return {"error": str(e)}
