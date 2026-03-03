#!/usr/bin/env python3
"""
상용 환경 배포 후 검증 스크립트 (Production Verification)

QA 체크리스트 기반 자동 검증:
1. API 상태 확인 (Health Check)
2. 검색 API 동작 확인
3. 콘텐츠 정책 준수 (7권 이상 확보)
4. 대출 상태 API 연동 확인
5. 데이터 로직 검증
"""

import sys
import os
import asyncio
import aiohttp
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import supabase
from dotenv import load_dotenv

load_dotenv()

# 환경 설정
API_BASE_URL = os.getenv("NEXT_PUBLIC_API_URL", "https://api.checkjari.com")
PROD_FRONTEND_URL = "https://checkjari.com"

# 색상 출력
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


async def check_api_health():
    """1. API 상태 확인 (Health Check)"""
    print_header("1. API Health Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/", timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print_success(f"API 응답 정상: {resp.status}")
                    print_info(f"응답 데이터: {data}")
                    return True
                else:
                    print_error(f"API 응답 실패: {resp.status}")
                    return False
    except Exception as e:
        print_error(f"API 연결 실패: {str(e)}")
        return False


async def check_search_api():
    """2. 검색 API 동작 확인"""
    print_header("2. 검색 API 동작 확인")
    
    test_cases = [
        {"q": "곰", "expected_min": 1},
        {"age": "0-3", "expected_min": 1},
        {"category": "그림책", "expected_min": 1},
    ]
    
    all_passed = True
    
    try:
        async with aiohttp.ClientSession() as session:
            for test in test_cases:
                params = {**test}
                params.pop("expected_min")
                
                async with session.get(
                    f"{API_BASE_URL}/api/books/search",
                    params=params,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        total = data.get("total", 0)
                        if total >= test["expected_min"]:
                            print_success(f"검색 테스트 통과: {params} → {total}권")
                        else:
                            print_error(f"검색 결과 부족: {params} → {total}권 (최소 {test['expected_min']}권 필요)")
                            all_passed = False
                    else:
                        print_error(f"검색 API 실패: {params} → {resp.status}")
                        all_passed = False
                        
    except Exception as e:
        print_error(f"검색 API 테스트 실패: {str(e)}")
        all_passed = False
    
    return all_passed


def check_content_policy():
    """3. 콘텐츠 정책 준수 (7권 이상 확보)"""
    print_header("3. 콘텐츠 정책 준수 확인 (7권 이상)")
    
    # 운영 정책: 각 섹션별 최소 7권 확보
    checks = [
        {
            "name": "겨울방학 추천",
            "filter": {"curation_tag": "겨울방학"},
            "min_count": 7
        },
        {
            "name": "연령별 추천 (0-3세)",
            "filter": {"age": "0-3"},
            "min_count": 7
        },
        {
            "name": "연령별 추천 (4-7세)",
            "filter": {"age": "4-7"},
            "min_count": 7
        },
        {
            "name": "어린이도서연구회 추천",
            "filter": {"curation_tag": "어린이도서연구회"},
            "min_count": 7
        },
    ]
    
    all_passed = True
    
    for check in checks:
        try:
            query = supabase.table("childbook_items").select("id", count="exact")
            query = query.not_.is_("pangyo_callno", "null")
            query = query.neq("pangyo_callno", "없음")
            query = query.or_("is_hidden.is.null,is_hidden.eq.false")
            
            # 필터 적용
            for key, value in check["filter"].items():
                if key == "age":
                    # 연령 필터링 로직 (search.py와 동일)
                    if value == "0-3":
                        query = query.or_("age.ilike.%0세%,age.ilike.%1세%,age.ilike.%2세%,age.ilike.%3세%,age.ilike.%0-3%")
                    elif value == "4-7":
                        query = query.or_("age.ilike.%4세%,age.ilike.%5세%,age.ilike.%6세%,age.ilike.%7세%,age.ilike.%4-7%")
                    else:
                        query = query.ilike("age", f"%{value}%")
                else:
                    query = query.ilike(key, f"%{value}%")
            
            result = query.execute()
            count = result.count if hasattr(result, 'count') else len(result.data)
            
            if count >= check["min_count"]:
                print_success(f"{check['name']}: {count}권 확보 (최소 {check['min_count']}권)")
            else:
                print_error(f"{check['name']}: {count}권 (최소 {check['min_count']}권 필요)")
                all_passed = False
                
        except Exception as e:
            print_error(f"{check['name']} 확인 실패: {str(e)}")
            all_passed = False
    
    return all_passed


async def check_loan_status_api():
    """4. 대출 상태 API 연동 확인"""
    print_header("4. 대출 상태 API 연동 확인")
    
    # 테스트용 책 ID 가져오기 (ISBN이 있는 책)
    try:
        data = supabase.table("childbook_items").select("id, isbn").not_.is_("isbn", "null").limit(3).execute()
        
        if not data.data:
            print_warning("테스트할 책이 없습니다 (ISBN 필요)")
            return False
        
        book_ids = [book["id"] for book in data.data]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}/api/books/loan-status",
                json=book_ids,
                timeout=15
            ) as resp:
                if resp.status == 200:
                    loan_data = await resp.json()
                    print_success(f"대출 상태 API 응답 정상: {len(loan_data)}건")
                    
                    # 응답 형식 확인
                    for book_id, status in loan_data.items():
                        if "status" in status:
                            print_info(f"  책 ID {book_id}: {status['status']}")
                        else:
                            print_warning(f"  책 ID {book_id}: 응답 형식 오류")
                    
                    return True
                else:
                    print_error(f"대출 상태 API 실패: {resp.status}")
                    text = await resp.text()
                    print_error(f"응답: {text[:200]}")
                    return False
                    
    except Exception as e:
        print_error(f"대출 상태 API 테스트 실패: {str(e)}")
        return False


def check_data_logic():
    """5. 데이터 로직 검증"""
    print_header("5. 데이터 로직 검증")
    
    checks_passed = True
    
    # 5-1. 청구기호 없는 책이 노출되지 않는지 확인
    try:
        query = supabase.table("childbook_items").select("id", count="exact")
        query = query.or_("pangyo_callno.is.null,pangyo_callno.eq.없음")
        query = query.or_("is_hidden.is.null,is_hidden.eq.false")
        
        result = query.execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        
        if count == 0:
            print_success("청구기호 없는 책 노출 방지: 정상")
        else:
            print_warning(f"청구기호 없는 책 {count}건이 노출될 수 있음")
            checks_passed = False
            
    except Exception as e:
        print_error(f"청구기호 검증 실패: {str(e)}")
        checks_passed = False
    
    # 5-2. 중복 ISBN 확인
    try:
        result = supabase.rpc("check_duplicate_isbns").execute()
        # RPC가 없을 수 있으므로 간단히 쿼리로 대체
        data = supabase.table("childbook_items").select("isbn").not_.is_("isbn", "null").execute()
        
        isbns = [book["isbn"] for book in data.data if book.get("isbn")]
        unique_isbns = set(isbns)
        
        if len(isbns) == len(unique_isbns):
            print_success(f"중복 ISBN 없음: {len(isbns)}건 확인")
        else:
            duplicates = len(isbns) - len(unique_isbns)
            print_warning(f"중복 ISBN {duplicates}건 발견")
            
    except Exception as e:
        print_error(f"중복 ISBN 검증 실패: {str(e)}")
    
    return checks_passed


async def main():
    """메인 검증 프로세스"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}상용 환경 QA 검증 시작{Colors.END}")
    print(f"{Colors.BOLD}대상 API: {API_BASE_URL}{Colors.END}")
    print(f"{Colors.BOLD}시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    results = {}
    
    # 1. API Health Check
    results["health"] = await check_api_health()
    
    # 2. 검색 API
    results["search"] = await check_search_api()
    
    # 3. 콘텐츠 정책
    results["content"] = check_content_policy()
    
    # 4. 대출 상태 API
    results["loan_status"] = await check_loan_status_api()
    
    # 5. 데이터 로직
    results["data_logic"] = check_data_logic()
    
    # 결과 요약
    print_header("검증 결과 요약")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: PASS")
        else:
            print_error(f"{check}: FAIL")
    
    print(f"\n{Colors.BOLD}총 {passed}/{total} 항목 통과{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ 모든 검증 통과! 상용 환경 정상{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ 일부 검증 실패. 상용 환경 점검 필요{Colors.END}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
