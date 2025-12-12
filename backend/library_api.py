import os
import requests
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"

# .env 파일에서 직접 읽기 (dotenv 실패 대비)
env_vars = {}
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
                            env_vars[key] = value
                    except Exception:
                        continue
    except Exception:
        pass

# dotenv 시도 (실패해도 env_vars에 있음)
try:
    load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

# 환경 변수 설정 (env_vars에서)
for key, value in env_vars.items():
    if key not in os.environ:
        try:
            os.environ[key] = value
        except Exception:
            pass

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID") or env_vars.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET") or env_vars.get("NAVER_CLIENT_SECRET")
DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY") or env_vars.get("DATA4LIBRARY_KEY")
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY") or env_vars.get("ALADIN_TTB_KEY")

def search_isbn(title, author=None):
    """
    네이버 책검색 API 기반 ISBN 찾기
    제목과 저자 정보를 활용하여 더 정확한 검색 수행
    
    Args:
        title: 책 제목
        author: 저자 (선택사항)
    
    Returns:
        (isbn13, score): ISBN-13과 유사도 점수, 실패 시 (None, 0)
    """
    if not title:
        return None, 0
    
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    # 저자 정보가 있으면 검색 쿼리에 포함
    if author:
        query = f"{title} {author}".strip()
    else:
        query = title
    
    params = {"query": query, "display": 10}  # 더 많은 결과 확인

    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.RequestException as e:
        # 디버깅: API 호출 오류만 출력 (너무 많은 출력 방지)
        if "네이버 API 호출 오류" not in str(e):
            pass  # 조용히 실패 처리
        return None, 0
    except Exception as e:
        return None, 0

    items = data.get("items", [])
    if not items:
        return None, 0

    best_item = None
    best_score = 0

    for item in items:
        item_title = item.get("title", "").replace("<b>", "").replace("</b>", "").strip()
        item_author = item.get("author", "").replace("<b>", "").replace("</b>", "").strip()
        
        # 제목 유사도 계산
        title_score = fuzz.token_set_ratio(title, item_title)
        
        # 저자 정보가 있으면 저자 유사도도 고려
        author_score = 0
        if author and item_author:
            author_score = fuzz.token_set_ratio(author, item_author)
            # 제목 70%, 저자 30% 가중치
            combined_score = title_score * 0.7 + author_score * 0.3
        else:
            combined_score = title_score
        
        if combined_score > best_score:
            best_score = combined_score
            best_item = item

    if not best_item:
        return None, 0

    # ISBN-13 우선 사용, 없으면 ISBN 사용
    isbn13 = best_item.get("isbn13", "")
    isbn = best_item.get("isbn", "")
    
    # ISBN-13이 있으면 사용, 없으면 ISBN 사용
    final_isbn = isbn13 if isbn13 else isbn
    
    # ISBN 형식 정리 (공백 제거, 숫자만 추출)
    if final_isbn:
        final_isbn = ''.join(filter(str.isdigit, final_isbn))
        # ISBN-13은 13자리, ISBN-10은 10자리
        if len(final_isbn) == 10 or len(final_isbn) == 13:
            return final_isbn, int(best_score)
    
    return None, 0

def search_isbn_aladin(title, author=None):
    """
    알라딘 Open API 기반 ISBN 찾기
    제목과 저자 정보를 활용하여 더 정확한 검색 수행
    
    Args:
        title: 책 제목
        author: 저자 (선택사항)
    
    Returns:
        (isbn13, score): ISBN-13과 유사도 점수, 실패 시 (None, 0)
    """
    if not title:
        return None, 0
    
    if not ALADIN_TTB_KEY:
        return None, 0
    
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    
    # 저자 정보가 있으면 QueryType을 Title로 하고 Author 파라미터 추가
    # 없으면 Keyword로 검색
    if author:
        params = {
            "TTBKey": ALADIN_TTB_KEY,
            "Query": title,
            "QueryType": "Title",
            "Author": author,
            "Output": "js",
            "Version": "20131101",
            "MaxResults": 10
        }
    else:
        params = {
            "TTBKey": ALADIN_TTB_KEY,
            "Query": title,
            "QueryType": "Keyword",
            "Output": "js",
            "Version": "20131101",
            "MaxResults": 10
        }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.RequestException:
        return None, 0
    except Exception:
        return None, 0
    
    items = data.get("item", [])
    if not items:
        return None, 0
    
    best_item = None
    best_score = 0
    
    for item in items:
        item_title = item.get("title", "").strip()
        item_author = item.get("author", "").strip()
        
        # 제목 유사도 계산
        title_score = fuzz.token_set_ratio(title, item_title)
        
        # 저자 정보가 있으면 저자 유사도도 고려
        author_score = 0
        if author and item_author:
            author_score = fuzz.token_set_ratio(author, item_author)
            # 제목 70%, 저자 30% 가중치
            combined_score = title_score * 0.7 + author_score * 0.3
        else:
            combined_score = title_score
        
        if combined_score > best_score:
            best_score = combined_score
            best_item = item
    
    if not best_item:
        return None, 0
    
    # ISBN-13 우선 사용, 없으면 ISBN 사용
    isbn13 = best_item.get("isbn13", "")
    isbn = best_item.get("isbn", "")
    
    # ISBN-13이 있으면 사용, 없으면 ISBN 사용
    final_isbn = isbn13 if isbn13 else isbn
    
    # ISBN 형식 정리 (공백 제거, 숫자만 추출)
    if final_isbn:
        final_isbn = ''.join(filter(str.isdigit, str(final_isbn)))
        # ISBN-13은 13자리, ISBN-10은 10자리
        if len(final_isbn) == 10 or len(final_isbn) == 13:
            return final_isbn, int(best_score)
    
    return None, 0

def search_isbn_combined(title, author=None):
    """
    네이버 API와 알라딘 API를 모두 활용한 ISBN 검색
    알라딘 API를 먼저 시도하고, 실패하거나 유사도가 낮으면 네이버 API 시도
    
    Args:
        title: 책 제목
        author: 저자 (선택사항)
    
    Returns:
        (isbn13, score, source): ISBN-13, 유사도 점수, API 소스('aladin' 또는 'naver'), 실패 시 (None, 0, None)
    """
    if not title:
        return None, 0, None
    
    # 알라딘 API 먼저 시도
    aladin_isbn, aladin_score = search_isbn_aladin(title, author)
    
    # 네이버 API 시도
    naver_isbn, naver_score = search_isbn(title, author)
    
    # 두 결과 중 더 높은 점수를 가진 것 선택
    if aladin_isbn and naver_isbn:
        if aladin_score >= naver_score:
            return aladin_isbn, aladin_score, 'aladin'
        else:
            return naver_isbn, naver_score, 'naver'
    elif aladin_isbn:
        return aladin_isbn, aladin_score, 'aladin'
    elif naver_isbn:
        return naver_isbn, naver_score, 'naver'
    else:
        return None, 0, None

def fetch_callno(isbn):
    """
    ISBN 기반 책 소장 여부 확인 (청구기호는 못 가져옴)
    """
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "isbn13": isbn,
        "format": "json"
    }

    res = requests.get(url, params=params)
    data = res.json()

    has_book = data.get("response", {}).get("hasBook", "N") == "Y"
    return None, has_book   # 청구기호는 itemSrch로만 조회됨
