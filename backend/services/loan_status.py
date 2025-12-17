"""도서 대출 정보 조회 서비스 (병렬 처리)"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from core.config import DATA4LIBRARY_KEY


# 인메모리 캐시 (1분 TTL)
LOAN_CACHE: Dict[str, tuple[Dict, datetime]] = {}
CACHE_TTL = timedelta(minutes=1)

# 판교 도서관 코드
PANGYO_LIB_CODE = "MA0003"


def get_cached_loan(isbn: str) -> Optional[Dict]:
    """캐시에서 대출 정보 조회"""
    if isbn in LOAN_CACHE:
        data, timestamp = LOAN_CACHE[isbn]
        if datetime.now() - timestamp < CACHE_TTL:
            return data
    return None


def set_cached_loan(isbn: str, data: Dict):
    """캐시에 대출 정보 저장"""
    LOAN_CACHE[isbn] = (data, datetime.now())


async def fetch_loan_status_single(
    session: aiohttp.ClientSession, 
    isbn: str
) -> Dict:
    """
    단일 책의 대출 정보 조회 (비동기)
    
    Args:
        session: aiohttp 세션
        isbn: ISBN 번호
        
    Returns:
        대출 정보 딕셔너리
    """
    # 캐시 확인
    cached = get_cached_loan(isbn)
    if cached:
        return cached
    
    # API 호출
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "isbn13": isbn,
        "format": "xml"
    }
    
    try:
        async with session.get(url, params=params, timeout=3) as response:
            text = await response.text()
            
            # XML 파싱
            root = ET.fromstring(text)
            
            # 대출 가능 여부 확인
            loan_available = root.find(".//loanAvailable")
            
            if loan_available is not None and loan_available.text:
                result = {
                    "available": loan_available.text == "Y",
                    "status": "대출가능" if loan_available.text == "Y" else "대출중",
                    "updated_at": datetime.now().isoformat()
                }
            else:
                result = {
                    "available": None,
                    "status": "정보없음",
                    "updated_at": datetime.now().isoformat()
                }
            
            # 캐시 저장
            set_cached_loan(isbn, result)
            return result
            
    except asyncio.TimeoutError:
        return {
            "available": None,
            "status": "시간초과",
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "available": None,
            "status": "확인불가",
            "error": str(e),
            "updated_at": datetime.now().isoformat()
        }


async def fetch_loan_status_batch(books: List[Dict]) -> Dict[int, Dict]:
    """
    여러 책의 대출 정보를 병렬로 조회
    
    Args:
        books: 책 리스트 (각 책은 id, isbn 필드 필요)
        
    Returns:
        {book_id: loan_info} 형태의 딕셔너리
    """
    if not DATA4LIBRARY_KEY:
        # API 키가 없으면 빈 결과 반환
        return {}
    
    # ISBN이 있는 책만 필터링
    books_with_isbn = [
        book for book in books 
        if book.get('isbn') and book.get('isbn').strip()
    ]
    
    if not books_with_isbn:
        return {}
    
    # 병렬 조회
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_loan_status_single(session, book['isbn'])
            for book in books_with_isbn
        ]
        
        # 모든 요청 동시 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 매핑
        loan_info = {}
        for book, result in zip(books_with_isbn, results):
            if not isinstance(result, Exception):
                loan_info[book['id']] = result
        
        return loan_info

