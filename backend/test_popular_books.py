"""
Data4Library 인기대출도서 API 테스트

목적: 홈페이지 "많이 찾는 책" 섹션을 위한 API 테스트
- 인기대출도서 조회
"""

import requests
from core.config import DATA4LIBRARY_KEY

if not DATA4LIBRARY_KEY:
    print("❌ DATA4LIBRARY_KEY가 설정되지 않았습니다")
    exit(1)

print(f"✅ API 키 로드 성공")

def get_popular_books():
    """
    Data4Library 인기대출도서 조회
    """
    # 최근 1개월 데이터
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    url = "http://data4library.kr/api/loanItemSrch"
    params = {
        'authKey': DATA4LIBRARY_KEY,
        'startDt': start_date.strftime('%Y-%m-%d'),
        'endDt': end_date.strftime('%Y-%m-%d'),
        'age': '8',  # 8세 (아동)
        'pageNo': '1',
        'pageSize': '20',
        'format': 'json'
    }
    
    print(f"📡 API 호출 중...")
    print(f"기간: {params['startDt']} ~ {params['endDt']}")
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 응답 구조 확인
        print("✅ API 응답 성공!")
        print(f"응답 키: {data.keys()}")
        print()
        
        # 도서 목록 추출
        if 'response' in data:
            books = data['response'].get('docs', [])
            print(f"📚 인기 도서 {len(books)}권 조회됨")
            print()
            
            # 상위 5권 출력
            print("=" * 80)
            print("상위 5권 인기 도서")
            print("=" * 80)
            
            for i, book in enumerate(books[:5], 1):
                print(f"\n{i}. {book.get('doc', {}).get('bookname', 'N/A')}")
                print(f"   저자: {book.get('doc', {}).get('authors', 'N/A')}")
                print(f"   출판사: {book.get('doc', {}).get('publisher', 'N/A')}")
                print(f"   ISBN: {book.get('doc', {}).get('isbn13', 'N/A')}")
                print(f"   대출 건수: {book.get('doc', {}).get('loanCnt', 'N/A')}")
            
            print()
            print("=" * 80)
            
            return books
        else:
            print("❌ 응답에 'response' 키가 없습니다")
            print(f"전체 응답: {data}")
            return []
            
    except requests.exceptions.Timeout:
        print("❌ API 타임아웃 (10초 초과)")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ API 호출 실패: {e}")
        return []
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []


def match_with_our_db(api_books):
    """
    API 결과를 우리 DB와 매칭
    """
    from supabase import create_client
    import os
    
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase 환경변수가 설정되지 않았습니다")
        return [], []
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("\n" + "=" * 80)
    print("우리 DB와 매칭 시도")
    print("=" * 80)
    
    matched = []
    not_matched = []
    
    for i, book in enumerate(api_books[:20], 1):  # 상위 20권 테스트
        doc = book.get('doc', {})
        isbn = doc.get('isbn13', '')
        title = doc.get('bookname', '')
        
        if not isbn:
            print(f"\n{i}. ⚠️  ISBN 없음: {title}")
            not_matched.append(title)
            continue
        
        # ISBN으로 우리 DB 검색
        try:
            result = supabase.table('childbook_items')\
                .select('id, title, author, pangyo_callno, is_hidden')\
                .eq('isbn', isbn)\
                .execute()
            
            if result.data and len(result.data) > 0:
                our_book = result.data[0]
                is_hidden = our_book.get('is_hidden', False)
                
                if is_hidden:
                    print(f"\n{i}. ⚠️  매칭되었으나 숨김 처리됨: {title}")
                    not_matched.append(title)
                else:
                    print(f"\n{i}. ✅ 매칭 성공: {title}")
                    print(f"   우리 DB ID: {our_book['id']}")
                    print(f"   청구기호: {our_book.get('pangyo_callno', 'N/A')}")
                    matched.append({
                        'api': doc,
                        'our_db': our_book
                    })
            else:
                print(f"\n{i}. ❌ 매칭 실패: {title}")
                print(f"   ISBN: {isbn}")
                not_matched.append(title)
        except Exception as e:
            print(f"\n{i}. ❌ DB 조회 오류: {title}")
            print(f"   오류: {e}")
            not_matched.append(title)
    
    print()
    print("=" * 80)
    print(f"매칭 결과: {len(matched)}권 성공, {len(not_matched)}권 실패")
    print("=" * 80)
    
    return matched, not_matched



if __name__ == '__main__':
    print("🔍 Data4Library 인기대출도서 API 테스트")
    print()
    
    # 1. API 호출
    popular_books = get_popular_books()
    
    if not popular_books:
        print("\n❌ API 호출 실패")
        exit(1)
    
    # 2. DB 매칭
    matched, not_matched = match_with_our_db(popular_books)
    
    # 3. 결과 요약
    print("\n" + "=" * 80)
    print("📊 최종 결과")
    print("=" * 80)
    print(f"API 조회: {len(popular_books)}권")
    print(f"✅ 매칭 성공: {len(matched)}권")
    print(f"❌ 매칭 실패: {len(not_matched)}권")
    print(f"매칭률: {len(matched) / len(popular_books) * 100:.1f}%")
    
    if len(matched) >= 5:
        print("\n✅ 홈페이지 '많이 찾는 책' 섹션 구현 가능!")
        print(f"   → 최소 5권 이상 매칭됨 ({len(matched)}권)")
        print("\n💡 제안하는 구조:")
        print("   홈 > 인기 도서 5권 표시")
        print("   더보기 → 인기 도서 전체 리스트 (매칭된 책만)")
        print("   책 클릭 → 책 상세 페이지")
    else:
        print("\n⚠️  매칭된 책이 부족합니다")
        print(f"   → 5권 필요, {len(matched)}권만 매칭됨")
        print("\n💡 해결 방법:")
        print("   1. 연령 범위 확대 (age 파라미터 조정)")
        print("   2. 기간 확대 (30일 → 60일)")
        print("   3. 대체 섹션 사용 ('새로 들어온 책' 등)")
