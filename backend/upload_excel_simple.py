"""
엑셀 파일을 읽어서 childbook_items 테이블에 업로드하는 간단한 스크립트

사용법:
    python upload_excel_simple.py <엑셀파일경로> [시트이름]

예시:
    python upload_excel_simple.py data.xlsx
    python upload_excel_simple.py data.xlsx "Sheet1"
"""
import pandas as pd
from supabase_client import supabase
import sys
import os

def upload_excel(excel_path: str, sheet_name: str = None):
    """엑셀 파일을 읽어서 childbook_items에 업로드"""
    
    print("=" * 60)
    print("엑셀 → Supabase 업로드")
    print("=" * 60)
    print(f"파일: {excel_path}")
    if sheet_name:
        print(f"시트: {sheet_name}")
    print()
    
    # 엑셀 읽기
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(f"✅ 엑셀 파일 읽기 성공")
        print(f"   총 {len(df)}행")
        print(f"   컬럼: {', '.join(df.columns.tolist())}")
        print()
    except Exception as e:
        print(f"❌ 엑셀 파일 읽기 실패: {e}")
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
    
    # 컬럼명 매핑 (엑셀 파일의 실제 컬럼명에 맞게 수정 필요)
    title_cols = ['제목', 'title', '책이름', '책 제목', '도서명']
    author_cols = ['지은이', 'author', '작가', '저자', '저작자']
    publisher_cols = ['출판사', 'publisher', '출판']
    isbn_cols = ['ISBN', 'isbn', 'ISBN13', 'isbn13']
    
    # 실제 컬럼명 찾기
    title_col = None
    author_col = None
    publisher_col = None
    isbn_col = None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if not title_col and any(t in col_lower for t in ['제목', 'title', '책이름', '도서명']):
            title_col = col
        if not author_col and any(a in col_lower for a in ['지은이', 'author', '작가', '저자']):
            author_col = col
        if not publisher_col and any(p in col_lower for p in ['출판사', 'publisher', '출판']):
            publisher_col = col
        if not isbn_col and any(i in col_lower for i in ['isbn']):
            isbn_col = col
    
    print(f"컬럼 매핑:")
    print(f"  제목: {title_col or '없음'}")
    print(f"  지은이: {author_col or '없음'}")
    print(f"  출판사: {publisher_col or '없음'}")
    print(f"  ISBN: {isbn_col or '없음'}")
    print()
    
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
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    excel_path = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    upload_excel(excel_path, sheet_name)








