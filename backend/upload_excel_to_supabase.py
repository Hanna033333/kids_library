import pandas as pd
from supabase_client import supabase
import os
from pathlib import Path
from typing import List, Dict

def upload_excel_to_childbook_items(excel_path: str, sheet_name: str = None):
    """
    엑셀 파일을 읽어서 childbook_items 테이블에 업로드
    
    Args:
        excel_path: 엑셀 파일 경로
        sheet_name: 시트 이름 (None이면 첫 번째 시트)
    """
    print("=" * 60)
    print("엑셀 파일을 Supabase에 업로드")
    print("=" * 60)
    print()
    
    # 엑셀 파일 읽기
    print(f"엑셀 파일 읽기: {excel_path}")
    try:
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_path)
        
        print(f"총 {len(df)}개의 행 발견")
        print(f"컬럼: {list(df.columns)}")
        print()
        
        # 기존 데이터 수 확인
        try:
            existing = supabase.table("childbook_items").select("*", count="exact").execute()
            count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
            print(f"현재 childbook_items에 저장된 도서 수: {count_before}권")
        except Exception as e:
            print(f"기존 데이터 확인 중 오류: {e}")
            count_before = 0
        
        print()
        print("데이터 업로드 시작...")
        print("-" * 60)
        
        success_count = 0
        error_count = 0
        
        # 각 행을 Supabase에 업로드
        for idx, row in df.iterrows():
            try:
                # 엑셀 컬럼명을 테이블 컬럼명에 매핑
                # 엑셀 파일의 실제 컬럼명에 맞게 수정 필요
                book_data = {}
                
                # 기본 필드 매핑 (엑셀 컬럼명에 맞게 수정 필요)
                if '제목' in df.columns or 'title' in df.columns or '책이름' in df.columns:
                    col_name = '제목' if '제목' in df.columns else ('title' if 'title' in df.columns else '책이름')
                    book_data['title'] = str(row[col_name]) if pd.notna(row[col_name]) else None
                
                if '지은이' in df.columns or 'author' in df.columns or '작가' in df.columns:
                    col_name = '지은이' if '지은이' in df.columns else ('author' if 'author' in df.columns else '작가')
                    book_data['author'] = str(row[col_name]) if pd.notna(row[col_name]) else None
                
                if '출판사' in df.columns or 'publisher' in df.columns:
                    col_name = '출판사' if '출판사' in df.columns else 'publisher'
                    book_data['publisher'] = str(row[col_name]) if pd.notna(row[col_name]) else None
                
                if 'ISBN' in df.columns or 'isbn' in df.columns or 'ISBN13' in df.columns:
                    col_name = 'ISBN' if 'ISBN' in df.columns else ('isbn' if 'isbn' in df.columns else 'ISBN13')
                    isbn_value = row[col_name]
                    if pd.notna(isbn_value):
                        book_data['isbn'] = str(isbn_value).strip()
                
                # None 값 제거
                book_data = {k: v for k, v in book_data.items() if v is not None}
                
                # 최소한 제목은 있어야 함
                if not book_data.get('title'):
                    print(f"  {idx+1}행: 제목이 없어서 건너뜀")
                    error_count += 1
                    continue
                
                # Supabase에 업로드
                supabase.table("childbook_items").upsert(book_data).execute()
                success_count += 1
                
                if (idx + 1) % 100 == 0:
                    print(f"  {idx+1}행 처리 완료...")
                    
            except Exception as e:
                print(f"  {idx+1}행 오류: {e}")
                error_count += 1
                continue
        
        print("-" * 60)
        print(f"업로드 완료!")
        print(f"  성공: {success_count}건")
        print(f"  실패: {error_count}건")
        
        # 업로드 후 데이터 수 확인
        try:
            updated = supabase.table("childbook_items").select("*", count="exact").execute()
            count_after = updated.count if hasattr(updated, 'count') else len(updated.data) if updated.data else 0
            print(f"\n저장 후 childbook_items에 저장된 도서 수: {count_after}권")
            print(f"추가된 도서 수: {count_after - count_before}권")
        except Exception as e:
            print(f"\n저장 후 데이터 확인 중 오류: {e}")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 사용 예시
    # 엑셀 파일 경로를 지정하세요
    excel_file = input("엑셀 파일 경로를 입력하세요: ").strip().strip('"')
    
    if not excel_file:
        print("파일 경로가 입력되지 않았습니다.")
    elif not os.path.exists(excel_file):
        print(f"파일을 찾을 수 없습니다: {excel_file}")
    else:
        upload_excel_to_childbook_items(excel_file)








