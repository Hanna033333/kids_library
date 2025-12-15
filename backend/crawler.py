import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from bs4 import BeautifulSoup
import time

# Load environment (.env)
env_path = Path(__file__).parent / ".env"
try:
    load_dotenv(dotenv_path=env_path)
except Exception:
    # dotenv 실패 시 직접 파일 읽기
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key and value:
                                os.environ[key] = value
                        except Exception:
                            continue
        except Exception:
            pass

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"   # 판교도서관 코드 (※ 실제 코드인지 다시 확인 필요)

def is_child_book(class_no: str) -> bool:
    """
    아동 도서 분류번호 판별 (청구기호가 '아' 또는 '유'로 시작)
    """
    if not class_no:
        return False
    
    # 청구기호가 '아' 또는 '유'로 시작하는지 확인
    if class_no.startswith('아') or class_no.startswith('유'):
        return True
    
    return False


def get_series_number_from_website(isbn13: str, title: str = "", base_callno: str = "") -> str:
    """
    판교 도서관 웹사이트에서 권차 기호(총서 번호) 가져오기
    ISBN 또는 제목을 기반으로 검색하여 청구기호 테이블에서 권차 기호를 찾습니다.
    
    Args:
        isbn13: ISBN-13
        title: 책 제목
        base_callno: 기본 청구기호 (예: '유 808.9-ㅇ175ㅇ')
    
    Returns:
        권차 기호 문자열 (예: '204'), 없으면 빈 문자열
    """
    try:
        import re
        
        # 판교 도서관 검색 URL
        search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResultList.do"
        
        # 제목이 있으면 제목으로 검색, 없으면 ISBN으로 검색
        search_keyword = title if title else isbn13
        
        params = {
            "searchType": "SIMPLE",
            "searchCategory": "BOOK",
            "searchKey": "ALL",
            "searchKeyword": search_keyword,
            "searchLibrary": "",
            "searchPbLibrary": "ALL",
            "currentPageNo": "1",
            "searchRecordCount": "20"  # 더 많은 결과 확인
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Use POST method as GET might fail or return partial results
        res = requests.post(search_url, data=params, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 방법 1: 테이블에서 청구기호 찾기 (기존 로직 유지)
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # 청구기호 컬럼 찾기
                for i, cell_text in enumerate(cell_texts):
                    if '[판교]' in cell_text or '판교' in cell_text:
                        for j, text in enumerate(cell_texts):
                            if base_callno and base_callno in text:
                                if '-' in text:
                                    parts = text.split('-')
                                    if len(parts) >= 3:
                                        last_part = parts[-1].strip()
                                        if last_part.isdigit():
                                            return last_part
                            elif re.match(r'^[유아]\s+\d+[.\d]*-[가-힣\d]+-\d+', text):
                                match = re.search(r'-(\d+)$', text)
                                if match:
                                    return match.group(1)
        
        # 방법 2: 전체 텍스트에서 '청구기호:' 패턴 찾기 (New & Robust)
        # 예: "청구기호: 유 808.9-ㅂ966ㅂ-40"
        all_text = soup.get_text()
        
        # 1. Base Callno + Volume pattern
        if base_callno:
            # Remove spaces for flexible matching
            clean_base = base_callno.replace(" ", "")
            # Regex to find "청구기호: ... base_callno ... -digits"
            # We look for the base callno, then a hyphen and digits
            # The page text might have "청구기호: 유 808.9-ㅂ966ㅂ-40"
            pass
            
        # Find all text nodes containing "청구기호:"
        callno_nodes = soup.find_all(string=re.compile(r"청구기호:"))
        for node in callno_nodes:
            text = node.strip()
            # text like "청구기호: 유 808.9-ㅂ966ㅂ-40"
            if base_callno and base_callno in text:
                # Extract the part after base_callno
                # e.g. text="... 유 808.9-ㅂ966ㅂ-40 ..."
                # base="유 808.9-ㅂ966ㅂ"
                # remaining="-40"
                after = text.split(base_callno)[-1]
                match = re.search(r'^-(\d+)', after.strip())
                if match:
                    return match.group(1)
            
            # If plain match failed, try lax matching (ignore spaces)
            # or just look for the format
            if re.search(r'[유아]\s*\d+[.\d]*-[가-힣\d]+-\d+', text):
                 match = re.search(r'-(\d+)(?:\s|$)', text)
                 if match:
                     # Check if this call number belongs to our book (fuzzy check?)
                     # If we found "청구기호:" near our book title...
                     # For now, if searching by ISBN/Title and getting results, usually the result IS the book.
                     return match.group(1)

        return ""
    except Exception as e:
        print(f"Error extracting series number: {e}")
        return ""


def fetch_library_books_child(start_dt: str = "2020-01-01", end_dt: str = "2025-12-31"):
    """
    판교 도서관 아동 도서만 수집하는 함수.
    callNumbers 필드의 separate_shelf_name이 '아'/'유'이거나 
    shelf_loc_name에 '어린이'가 포함된 도서를 수집합니다.
    날짜 범위는 YYYY-MM-DD 형식.
    """
    url = "http://data4library.kr/api/itemSrch"
    page = 1
    page_size = 100  # 페이지 크기 (타임아웃 방지를 위해 작게 설정)
    books = []

    while True:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_CODE,
            "startDt": start_dt,
            "endDt": end_dt,
            "pageNo": page,
            "pageSize": page_size,
            "format": "json"
        }

        try:
            res = requests.get(url, params=params, timeout=120)  # 타임아웃 증가
            res.raise_for_status()  # HTTP 에러 체크
            
            # 응답 내용 확인
            if not res.text:
                print(f"{page} 페이지: 빈 응답")
                break
                
            try:
                data = res.json()
            except ValueError as json_err:
                print(f"{page} 페이지: JSON 파싱 오류 - {json_err}")
                print(f"응답 내용 (처음 500자): {res.text[:500]}")
                break
        except requests.exceptions.RequestException as e:
            print(f"요청 오류 발생: {e}")
            break
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            break

        docs = data.get("response", {}).get("docs", [])
        if not docs:
            break

        for d in docs:
            item = d.get("doc", {})
            class_no = item.get("class_no", "")
            
            # callNumbers 필드에서 아동 도서 확인 및 실제 청구기호 추출
            call_numbers = item.get("callNumbers", [])
            is_child = False
            actual_callno = None  # 실제 청구기호 (book_code)
            
            for call_info in call_numbers:
                call_number = call_info.get("callNumber", {})
                separate_shelf_name = call_number.get("separate_shelf_name", "")  # '유' 또는 '아'
                shelf_loc_name = call_number.get("shelf_loc_name", "")
                book_code = call_number.get("book_code", "")  # 'ㅇ175ㅇ'
                copy_code = call_number.get("copy_code", "")  # 복본 번호 (예: '204')
                
                # separate_shelf_name이 '아' 또는 '유'로 시작하거나
                # shelf_loc_name에 '어린이'가 포함되어 있으면 아동 도서
                if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
                   ('어린이' in shelf_loc_name):
                    is_child = True
                    # 전체 청구기호 구성: '유 808.9-ㅇ175ㅇ-204' 형식
                    parts = []
                    
                    # 1. separate_shelf_name (유/아)
                    if separate_shelf_name:
                        parts.append(separate_shelf_name)
                    
                    # 2. class_no (KDC 분류번호, 예: 808.9)
                    if class_no:
                        parts.append(class_no)
                    
                    # 3. book_code (예: ㅇ175ㅇ)
                    if book_code:
                        parts.append(book_code)
                    
                    # 4. 총서 번호 (copy_code가 없으면 웹사이트에서 가져오기)
                    series_number = copy_code
                    if not series_number:
                        # 웹사이트에서 총서 번호 가져오기 (느리므로 필요한 경우에만)
                        isbn13 = item.get("isbn13", "")
                        title = item.get("bookname", "")
                        if isbn13 or title:
                            series_number = get_series_number_from_website(isbn13, title)
                            # API 부하 방지를 위한 짧은 대기
                            time.sleep(0.3)
                    
                    if series_number:
                        parts.append(series_number)
                    
                    # 전체 청구기호 조합: '유 808.9-ㅇ175ㅇ-204' 형식
                    if len(parts) >= 3:
                        # separate_shelf_name + class_no + book_code + (series_number)
                        actual_callno = f"{parts[0]} {parts[1]}-{parts[2]}"
                        if len(parts) >= 4:
                            actual_callno += f"-{parts[3]}"
                    elif len(parts) == 2:
                        # separate_shelf_name + book_code (class_no 없는 경우)
                        actual_callno = f"{parts[0]} {parts[1]}"
                    elif len(parts) == 1:
                        # book_code만 있는 경우
                        actual_callno = parts[0]
                    
                    break
            
            # 아동 도서가 아니면 건너뛰기
            if not is_child:
                continue

            # 실제 청구기호가 없으면 건너뛰기 (데이터 불완전)
            if not actual_callno:
                continue

            books.append({
                "isbn13": item.get("isbn13", ""),
                "title": item.get("bookname", ""),
                "author": item.get("authors", ""),
                "callno": actual_callno,  # 실제 청구기호 저장 (book_code)
                "lib_code": PANGYO_CODE,
            })

        print(f"{page} 페이지 완료 / 현재까지 {len(books)}권 수집됨")
        page += 1

    return books
