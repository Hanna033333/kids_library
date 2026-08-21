"""도서 대출 정보 조회 서비스 (병렬 처리)"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from core.config import DATA4LIBRARY_KEY
from services.telegram_notifier import send_telegram_message

logger = logging.getLogger(__name__)

# 쿨다운 방지를 위한 마지막 경고 전송 시각
LAST_WARNING_SENT_AT: Optional[datetime] = None
WARNING_LOCK: Optional[asyncio.Lock] = None

def get_warning_lock() -> asyncio.Lock:
    global WARNING_LOCK
    if WARNING_LOCK is None:
        WARNING_LOCK = asyncio.Lock()
    return WARNING_LOCK


# 인메모리 캐시 (30분 TTL)
LOAN_CACHE: Dict[str, tuple[Dict, datetime]] = {}
CACHE_TTL = timedelta(minutes=30)
LAST_GC_RUN_AT: datetime = datetime.now()

# 도서관 코드 매핑 (전국 대표 7개 도서관 - ㄱㄴㄷ 순)
LIBRARY_CODE_MAP = {
    "광주광역시립무등도서관": "124003",
    "서울특별시교육청서울시립어린이도서관": "111017",
    "송파어린이도서관": "111117",
    "수지도서관": "141079",
    "울산도서관": "131080",
    "판교도서관": "141231",
    "한밭도서관": "125003"
}

# 기본 도서관 코드
PANGYO_LIB_CODE = "141231"

# 전역 세마포어 (Lazy Init)
GLOBAL_SEMAPHORE: Optional[asyncio.Semaphore] = None

def get_semaphore() -> asyncio.Semaphore:
    """전역 세마포어 반환 (없으면 생성)"""
    global GLOBAL_SEMAPHORE
    if GLOBAL_SEMAPHORE is None:
        # 1페이지(24권) 분량을 1라운드에 동시 병렬 처리할 수 있도록 25로 설정
        GLOBAL_SEMAPHORE = asyncio.Semaphore(25)
    return GLOBAL_SEMAPHORE


def clean_expired_cache():
    """만료된 (30분 초과) 대출 캐시 항목을 메모리에서 제거합니다. (가비지 컬렉션)"""
    global LAST_GC_RUN_AT
    now = datetime.now()
    # GC 실행은 5분에 한 번씩만 수행하여 오버헤드 최소화
    if now - LAST_GC_RUN_AT < timedelta(minutes=5):
        return
        
    LAST_GC_RUN_AT = now
    expired_keys = [
        key for key, (_, timestamp) in LOAN_CACHE.items()
        if now - timestamp >= CACHE_TTL
    ]
    
    for key in expired_keys:
        LOAN_CACHE.pop(key, None)
        
    if expired_keys:
        logger.info(f"🧹 Cleaned {len(expired_keys)} expired items from LOAN_CACHE")


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
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=False) as response:
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
    # 주기적인 캐시 GC 실행
    clean_expired_cache()
    
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
    timeout = aiohttp.ClientTimeout(total=20)
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
            async def maybe_send_warning():
                global LAST_WARNING_SENT_AT
                async with get_warning_lock():
                    now = datetime.now()
                    if LAST_WARNING_SENT_AT is None or (now - LAST_WARNING_SENT_AT) > timedelta(hours=1):
                        LAST_WARNING_SENT_AT = now
                        warning_text = (
                            f"🚨 <b>[책자리 API 경고] 도서관 정보나루 연동 장애 감지</b>\n\n"
                            f"조회 대상 도서 전체가 '확인중' 상태로 반환되었습니다. IP 차단이나 정보나루 API 서버 장애 가능성이 높습니다.\n"
                            f"- 조회 도서 수: {len(books_with_isbn)}권\n"
                            f"- 감지 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} (KST)"
                        )
                        await send_telegram_message(warning_text)
            asyncio.create_task(maybe_send_warning())
    
    return loan_info
