"""도서 대출 정보 조회 서비스 (병렬 처리)"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY


# 인메모리 캐시 (30분 TTL)
LOAN_CACHE: Dict[str, tuple[Dict, datetime]] = {}
CACHE_TTL = timedelta(minutes=30)

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"


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
    
    # bookExist API 호출 (실시간 대출 가능 여부)
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": isbn,
        "format": "json"
    }
    
    try:
        async with session.get(url, params=params, timeout=3) as response:
            data = await response.json()
            
            # 응답 파싱
            result_data = data.get("response", {}).get("result", {})
            has_book = result_data.get("hasBook", "N")
            loan_available = result_data.get("loanAvailable", "N")
            
            if has_book == "Y":
                result = {
                    "available": loan_available == "Y",
                    "status": "대출가능" if loan_available == "Y" else "대출중",
                    "updated_at": datetime.now().isoformat()
                }
            else:
                result = {
                    "available": None,
                    "status": "미소장",
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
    
    # 병렬 조회 (세마포어로 동시 요청 제한 - 속도 향상)
    semaphore = asyncio.Semaphore(20)  # 동시 요청 20개로 증량

    async def fetch_with_sem(session, isbn):
        async with semaphore:
            return await fetch_loan_status_single(session, isbn)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_with_sem(session, book['isbn'])
            for book in books_with_isbn
        ]
        
        # 모든 요청 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
    # 결과 매핑
    loan_info = {}
    
    # 1. ISBN이 있는 책들의 결과 매핑
    for book, result in zip(books_with_isbn, results):
        if not isinstance(result, Exception):
            loan_info[book['id']] = result
        else:
            loan_info[book['id']] = {
                "available": None,
                "status": "확인불가",
                "error": str(result),
                "updated_at": datetime.now().isoformat()
            }
            
    # 2. ISBN이 없는 책이나 결과가 누락된 책 처리
    for book in books:
        if book['id'] not in loan_info:
            loan_info[book['id']] = {
                "available": None,
                "status": "정보없음", # ISBN 없음 등
                "updated_at": datetime.now().isoformat()
            }
    
    return loan_info


