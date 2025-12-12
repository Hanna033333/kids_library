import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict

def fetch_childbook_recommendations(page: int = 1) -> List[Dict]:
    """
    어린이 도서 연구회 추천 도서 리스트 크롤링
    
    Args:
        page: 페이지 번호 (기본값: 1)
    
    Returns:
        추천 도서 리스트
    """
    url = "https://www.childbook.org/book/recommend_list.html"
    
    params = {
        "p": page  # 페이지 파라미터
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=30)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        soup = BeautifulSoup(res.text, 'html.parser')
        books = []
        
        # 모든 li 태그에서 책 정보 추출
        book_items = soup.find_all('li')
        
        for item in book_items:
            try:
                # 책 정보가 있는 li인지 확인 (긴 텍스트가 있는 경우)
                text = item.get_text(strip=True)
                if len(text) < 50:  # 너무 짧으면 건너뛰기
                    continue
                
                # 책 제목 (st1 클래스의 b 태그)
                title_elem = item.find('p', class_='st1')
                if not title_elem:
                    continue
                    
                title = title_elem.find('b')
                if not title:
                    continue
                title = title.get_text(strip=True)
                
                # 지은이 (st2 mt20 클래스)
                author_elem = item.find('p', class_='st2')
                author = ""
                if author_elem:
                    author = author_elem.get_text(strip=True)
                
                # 출판사/연도/쪽수 (st2 클래스, 두 번째)
                pub_info = ""
                st2_elems = item.find_all('p', class_='st2')
                if len(st2_elems) > 1:
                    pub_info = st2_elems[1].get_text(strip=True)
                
                # 출판사, 연도, 쪽수 파싱
                publisher = ""
                year = ""
                pages = ""
                if pub_info:
                    parts = pub_info.split('|')
                    if len(parts) >= 1:
                        publisher = parts[0].strip()
                    if len(parts) >= 2:
                        year = parts[1].strip()
                    if len(parts) >= 3:
                        pages = parts[2].strip()
                
                # 연령/갈래/가격 (st2 클래스 중 연령 정보가 있는 것)
                age = ""
                category = ""
                price = ""
                
                # 모든 st2 p 태그 확인
                for p_elem in st2_elems:
                    p_text = p_elem.get_text(strip=True)
                    # 연령 정보가 포함된 경우 (세부터, 전연령, 교사 등)
                    if '세부터' in p_text or '전연령' in p_text or '교사' in p_text:
                        parts = p_text.split('|')
                        if len(parts) >= 1:
                            age = parts[0].strip()
                        if len(parts) >= 2:
                            category = parts[1].strip()
                        if len(parts) >= 3:
                            price = parts[2].strip()
                        break
                
                # 내용 (st2 클래스의 div)
                description = ""
                desc_elem = item.find('div', class_='st2')
                if desc_elem:
                    # '내용' 텍스트 다음 부분만 추출
                    desc_text = desc_elem.get_text(strip=True)
                    if '내용' in desc_text:
                        desc_text = desc_text.split('내용', 1)[-1].strip()
                    description = desc_text
                
                # 책 번호 (b_no 파라미터)
                book_no = ""
                link = item.find('a')
                if link and link.get('href'):
                    href = link.get('href')
                    match = re.search(r'b_no=(\d+)', href)
                    if match:
                        book_no = match.group(1)
                
                books.append({
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "year": year,
                    "pages": pages,
                    "age": age,
                    "category": category,
                    "price": price,
                    "description": description,
                    "book_no": book_no,
                    "source": "childbook_org"
                })
            except Exception as e:
                print(f"책 정보 파싱 오류: {e}")
                continue
        
        return books
        
    except Exception as e:
        print(f"요청 오류 발생: {e}")
        return []


def fetch_all_childbook_recommendations() -> List[Dict]:
    """
    모든 페이지의 추천 도서 수집
    """
    all_books = []
    page = 1
    
    while True:
        print(f"{page} 페이지 크롤링 중...")
        books = fetch_childbook_recommendations(page)
        
        if not books:
            print(f"{page} 페이지에 데이터가 없습니다. 종료합니다.")
            break
            
        all_books.extend(books)
        print(f"{page} 페이지 완료 / 현재까지 {len(all_books)}권 수집됨")
        
        # 다음 페이지 확인 (마지막 페이지까지)
        # 실제로는 페이지네이션 정보를 확인해야 함
        page += 1
        
        # 안전장치: 너무 많은 페이지 방지
        if page > 200:
            print("최대 페이지 수에 도달했습니다.")
            break
            
        time.sleep(1)  # 서버 부하 방지
    
    return all_books
