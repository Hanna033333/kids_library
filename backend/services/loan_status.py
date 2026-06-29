"""도서 대출 정보 조회 서비스 (병렬 처리)"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY
from services.telegram_notifier import send_telegram_message


# 쿨다운 방지를 위한 마지막 경고 전송 시각
LAST_WARNING_SENT_AT: Optional[datetime] = None


# 인메모리 캐시 (30분 TTL)
LOAN_CACHE: Dict[str, tuple[Dict, datetime]] = {}
CACHE_TTL = timedelta(minutes=30)

# 도서관 코드 매핑 (판교도서관: 141231, 송파어린이도서관: 111117)
LIBRARY_CODE_MAP = {
    "판교도서관": "141231",
    "송파어린이도서관": "111117"
}

# 기본 도서관 코드
PANGYO_LIB_CODE = "141231"

# 전역 세마포어 (Lazy Init)
GLOBAL_SEMAPHORE: Optional[asyncio.Semaphore] = None

def get_semaphore() -> asyncio.Semaphore:
    """전역 세마포어 반환 (없으면 생성)"""
    global GLOBAL_SEMAPHORE
    if GLOBAL_SEMAPHORE is None:
        # 동시 요청 수를 5로 제한 (안정성 최우선)
        GLOBAL_SEMAPHORE = asyncio.Semaphore(5)
    return GLOBAL_SEMAPHORE



def get_cached_loan(lib_code: str, isbn: str) -> Optional[Dict]:
    """캐시에서 도서관별 대출 정보 조회"""
    cache_key = f"{lib_code}:{isbn}"
    if cache_key in LOAN_CACHE:
        data, timestamp = LOAN_CACHE[cache_key]
        if datetime.now() - timestamp < CACHE_TTL:
            return data
    return None


def set_cached_loan(lib_code: str, isbn: str, data: Dict):
    """캐시에 도서관별 대출 정보 저장"""
    cache_key = f"{lib_code}:{isbn}"
    LOAN_CACHE[cache_key] = (data, datetime.now())


async def fetch_loan_status_single(
    session: aiohttp.ClientSession, 
    isbn: str,
    lib_code: str = PANGYO_LIB_CODE
) -> Dict:
    """
    단일 책의 특정 도서관 대출 정보 조회 (비동기)
    
    Args:
        session: aiohttp 세션
        isbn: ISBN 번호
        lib_code: 도서관 기관 코드
        
    Returns:
        대출 정보 딕셔너리
    """
    # 캐시 확인
    cached = get_cached_loan(lib_code, isbn)
    if cached:
        return cached
    
    # bookExist API 호출 (실시간 대출 가능 여부)
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": lib_code,
        "isbn13": isbn,
        "format": "json"
    }
    
    try:
        async with session.get(url, params=params, timeout=30, allow_redirects=False) as response:
            # 302 리다이렉트 = 정보나루 API 점검/한도초과 상태
            if response.status in (301, 302, 303, 307, 308):
                result = {
                    "available": None,
                    "status": "확인중",
                    "updated_at": datetime.now().isoformat()
                }
                return result
            
            try:
                data = await response.json()
            except Exception:
                # JSON 파싱 실패 (HTML 응답 등)
                return {
                    "available": None,
                    "status": "확인중",
                    "updated_at": datetime.now().isoformat()
                }
            
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
            set_cached_loan(lib_code, isbn, result)
            return result
            
    except asyncio.TimeoutError:
        return {
            "available": None,
            "status": "확인중",
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "available": None,
            "status": "확인중",
            "error": str(e),
            "updated_at": datetime.now().isoformat()
        }


async def fetch_loan_status_batch(books: List[Dict], library_name: Optional[str] = None) -> Dict[int, Dict]:
    """
    여러 책의 특정 도서관 대출 정보를 병렬로 조회
    
    Args:
        books: 책 리스트 (각 책은 id, isbn 필드 필요)
        library_name: 조회 대상 도서관 명칭 (기본: 판교도서관)
        
    Returns:
        {book_id: loan_info} 형태의 딕셔너리
    """
    if not DATA4LIBRARY_KEY:
        # API 키가 없으면 빈 결과 반환
        return {}
    
    # 도서관 코드 확인
    lib_code = PANGYO_LIB_CODE
    if library_name and library_name in LIBRARY_CODE_MAP:
        lib_code = LIBRARY_CODE_MAP[library_name]
    
    # ISBN이 있는 책만 필터링
    books_with_isbn = [
        book for book in books 
        if book.get('isbn') and book.get('isbn').strip()
    ]
    
    if not books_with_isbn:
        return {}
    
    # 병렬 조회 (전역 세마포어로 동시 요청 제한)
    semaphore = get_semaphore()

    async def fetch_with_sem(session, isbn):
        async with semaphore:
            return await fetch_loan_status_single(session, isbn, lib_code)

    # 타임아웃 설정을 포함한 세션
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
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
                "status": "확인중",
                "error": str(result),
                "updated_at": datetime.now().isoformat()
            }
            
    # 2. ISBN이 없는 책이나 결과가 누락된 책 처리
    for book in books:
        if book['id'] not in loan_info:
            loan_info[book['id']] = {
                "available": None,
                "status": "미소장",
                "updated_at": datetime.now().isoformat()
            }
    
    # 3. 전체 도서 '확인중' (API 장애/차단) 감지 및 텔레그램 알림 발송
    if len(books_with_isbn) >= 5:
        all_failed = all(
            loan_info[book['id']].get("status") == "확인중"
            for book in books_with_isbn
        )
        if all_failed:
            global LAST_WARNING_SENT_AT
            now = datetime.now()
            # 1시간 쿨다운 체크
            if LAST_WARNING_SENT_AT is None or (now - LAST_WARNING_SENT_AT) > timedelta(hours=1):
                LAST_WARNING_SENT_AT = now
                warning_text = (
                    f"🚨 <b>[책자리 API 경고] 도서관 정보나루 연동 장애 감지</b>\n\n"
                    f"조회 대상 도서 전체가 '확인중' 상태로 반환되었습니다. IP 차단이나 정보나루 API 서버 장애 가능성이 높습니다.\n"
                    f"- 조회 도서 수: {len(books_with_isbn)}권\n"
                    f"- 감지 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} (KST)"
                )
                # 비차단(Non-blocking)을 위해 백그라운드 태스크로 전송
                asyncio.create_task(send_telegram_message(warning_text))
    
    return loan_info




