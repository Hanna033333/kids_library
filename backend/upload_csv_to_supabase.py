"""
CSV 파일을 읽어서 childbook_items 테이블에 업로드하는 스크립트

사용법:
    python upload_csv_to_supabase.py <CSV파일경로>
"""
import pandas as pd
from supabase_client import supabase
import sys
import os

def upload_csv(csv_path: str):
    """CSV 파일을 읽어서 childbook_items에 업로드"""
    
    print("=" * 60)
    print("CSV → Supabase 업로드")
    print("=" * 60)
    print(f"파일: {csv_path}")
    print()
    
    # CSV 읽기
    try:
        # 인코딩 자동 감지 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✅ CSV 파일 읽기 성공 (인코딩: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("❌ CSV 파일 읽기 실패: 인코딩을 확인할 수 없습니다.")
            return
        
        print(f"   총 {len(df)}행")
        print(f"   컬럼: {', '.join(df.columns.tolist())}")
        print()
        
        # 첫 몇 행 미리보기
        print("첫 3행 미리보기:")
        print(df.head(3).to_string())
        print()
        
    except Exception as e:
        print(f"❌ CSV 파일 읽기 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 기존 데이터 수 확인
    try:
        existing = supabase.table("childbook_items").select("*", count="exact").execute()
        count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
        print(f"현재 저장된 도서 수: {count_before}권")
    except:
        count_before = 0
    
    print()
    print("업로드 시작...")
    print("-" * 60)
    
    success = 0
    error = 0
    
    # 컬럼명 매핑
    title_col = '책이름'
    author_col = '지은이'
    publisher_col = '출판사'
    page_col = '쪽수'
    age_col = '연령'
    category_col = '갈래'
    price_col = '가격'
    keywords_col = '주제어'
    isbn_col = None
    
    # 실제 컬럼명 확인
    for col in df.columns:
        col_str = str(col).strip()
        col_lower = col_str.lower()
        if 'isbn' in col_lower:
            isbn_col = col
    
    print(f"컬럼 매핑:")
    print(f"  제목 (title): {title_col}")
    print(f"  지은이 (author): {author_col}")
    print(f"  출판사 (publisher): {publisher_col}")
    print(f"  쪽수 (page): {page_col}")
    print(f"  연령 (age): {age_col}")
    print(f"  갈래 (category): {category_col}")
    print(f"  가격 (price): {price_col}")
    print(f"  주제어 (keywords): {keywords_col}")
    print(f"  ISBN: {isbn_col or '없음'}")
    print()
    
    if not title_col:
        print("⚠️ 경고: 제목 컬럼을 찾을 수 없습니다. 업로드를 계속할까요? (y/n)")
        # 자동으로 진행하되 경고만 표시
    
    # 각 행 처리
    for idx, row in df.iterrows():
        try:
            book_data = {}
            
            if title_col:
                title_val = row[title_col]
                if pd.notna(title_val):
                    book_data['title'] = str(title_val).strip()
            
            if author_col:
                author_val = row[author_col]
                if pd.notna(author_val):
                    book_data['author'] = str(author_val).strip()
            
            if publisher_col:
                publisher_val = row[publisher_col]
                if pd.notna(publisher_val):
                    book_data['publisher'] = str(publisher_val).strip()
            
            # 쪽수 (page)
            if page_col in df.columns:
                page_val = row[page_col]
                if pd.notna(page_val):
                    # "216쪽" 같은 형식에서 숫자만 추출
                    page_str = str(page_val).strip()
                    page_clean = ''.join(filter(str.isdigit, page_str))
                    if page_clean:
                        try:
                            book_data['page'] = int(page_clean)
                        except:
                            book_data['page'] = page_str
            
            # 연령 (age)
            if age_col in df.columns:
                age_val = row[age_col]
                if pd.notna(age_val):
                    book_data['age'] = str(age_val).strip()
            
            # 갈래 (category)
            if category_col in df.columns:
                category_val = row[category_col]
                if pd.notna(category_val):
                    book_data['category'] = str(category_val).strip()
            
            # 가격 (price)
            if price_col in df.columns:
                price_val = row[price_col]
                if pd.notna(price_val):
                    # "9,800원" 같은 형식에서 숫자만 추출
                    price_str = str(price_val).strip()
                    # 쉼표와 "원" 제거 후 숫자만 추출
                    price_clean = ''.join(filter(str.isdigit, price_str.replace(',', '')))
                    if price_clean:
                        try:
                            book_data['price'] = int(price_clean)
                        except:
                            pass  # 변환 실패 시 건너뜀
            
            # 주제어 (keywords)
            if keywords_col in df.columns:
                keywords_val = row[keywords_col]
                if pd.notna(keywords_val):
                    book_data['keywords'] = str(keywords_val).strip()
            
            if isbn_col:
                isbn_val = row[isbn_col]
                if pd.notna(isbn_val):
                    # ISBN에서 숫자만 추출
                    isbn_str = str(isbn_val).strip()
                    isbn_clean = ''.join(filter(str.isdigit, isbn_str))
                    if isbn_clean:
                        book_data['isbn'] = isbn_clean
            
            # 제목은 필수
            if not book_data.get('title'):
                error += 1
                if error <= 5:  # 처음 5개만 출력
                    print(f"  {idx+1}행: 제목이 없어서 건너뜀")
                continue
            
            # 업로드
            supabase.table("childbook_items").upsert(book_data).execute()
            success += 1
            
            if (idx + 1) % 50 == 0:
                print(f"  {idx+1}/{len(df)} 처리 중...")
                
        except Exception as e:
            error += 1
            if error <= 5:  # 처음 5개 오류만 출력
                print(f"  {idx+1}행 오류: {e}")
            continue
    
    print("-" * 60)
    print(f"✅ 완료!")
    print(f"   성공: {success}건")
    print(f"   실패: {error}건")
    
    # 최종 데이터 수 확인
    try:
        updated = supabase.table("childbook_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else len(updated.data) if updated.data else 0
        print(f"\n저장 후 총 도서 수: {count_after}권 (+{count_after - count_before})")
    except Exception as e:
        print(f"\n최종 데이터 확인 중 오류: {e}")


if __name__ == "__main__":
    csv_path = r"C:\Users\skplanet\Desktop\kids library\검색결과.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        sys.exit(1)
    
    upload_csv(csv_path)

