"""
childbook_items 테이블의 모든 데이터 삭제 후 CSV 파일 재업로드
"""
import pandas as pd
from supabase_client import supabase
import os

def clear_table():
    """테이블의 모든 데이터 삭제"""
    print("=" * 60)
    print("테이블 데이터 삭제")
    print("=" * 60)
    print()
    
    try:
        # 전체 데이터 수 확인
        count_result = supabase.table("childbook_items").select("*", count="exact").execute()
        count_before = count_result.count if hasattr(count_result, 'count') else 0
        print(f"삭제 전 총 도서 수: {count_before}건")
        print()
        
        if count_before == 0:
            print("삭제할 데이터가 없습니다.")
            return
        
        print("데이터 삭제 중...")
        
        # 모든 데이터 조회 후 삭제
        page_size = 1000
        offset = 0
        deleted = 0
        
        while True:
            data = supabase.table("childbook_items").select("id").range(offset, offset + page_size - 1).execute()
            
            if not data.data or len(data.data) == 0:
                break
            
            # 배치로 삭제
            for item in data.data:
                try:
                    supabase.table("childbook_items").delete().eq("id", item['id']).execute()
                    deleted += 1
                except Exception as e:
                    print(f"  삭제 오류: {e}")
            
            offset += page_size
            
            if offset % 1000 == 0:
                print(f"  {deleted}건 삭제 중...")
            
            if len(data.data) < page_size:
                break
        
        print(f"✅ {deleted}건 삭제 완료")
        print()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


def upload_csv_complete(csv_path: str):
    """CSV 파일을 모든 필드 포함해서 업로드"""
    print("=" * 60)
    print("CSV 파일 업로드 (모든 필드 포함)")
    print("=" * 60)
    print(f"파일: {csv_path}")
    print()
    
    # CSV 읽기
    try:
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
            print("❌ CSV 파일 읽기 실패")
            return
        
        print(f"   총 {len(df)}행")
        print(f"   컬럼: {', '.join(df.columns.tolist())}")
        print()
        
    except Exception as e:
        print(f"❌ CSV 파일 읽기 실패: {e}")
        return
    
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
    
    # 각 행 처리
    for idx, row in df.iterrows():
        try:
            book_data = {}
            
            # 제목
            if title_col in df.columns:
                title_val = row[title_col]
                if pd.notna(title_val):
                    book_data['title'] = str(title_val).strip()
            
            # 지은이
            if author_col in df.columns:
                author_val = row[author_col]
                if pd.notna(author_val):
                    book_data['author'] = str(author_val).strip()
            
            # 출판사
            if publisher_col in df.columns:
                publisher_val = row[publisher_col]
                if pd.notna(publisher_val):
                    book_data['publisher'] = str(publisher_val).strip()
            
            # 쪽수 (page)
            if page_col in df.columns:
                page_val = row[page_col]
                if pd.notna(page_val):
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
                    price_str = str(price_val).strip()
                    price_clean = ''.join(filter(str.isdigit, price_str.replace(',', '')))
                    if price_clean:
                        try:
                            book_data['price'] = int(price_clean)
                        except:
                            pass
            
            # 주제어 (keywords)
            if keywords_col in df.columns:
                keywords_val = row[keywords_col]
                if pd.notna(keywords_val):
                    book_data['keywords'] = str(keywords_val).strip()
            
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
            if error <= 5:
                print(f"  {idx+1}행 오류: {e}")
            continue
    
    print("-" * 60)
    print(f"✅ 업로드 완료!")
    print(f"   성공: {success}건")
    print(f"   실패: {error}건")
    
    # 최종 데이터 수 확인
    try:
        updated = supabase.table("childbook_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else 0
        print(f"\n저장 후 총 도서 수: {count_after}권")
    except Exception as e:
        print(f"\n최종 데이터 확인 중 오류: {e}")


if __name__ == "__main__":
    csv_path = r"C:\Users\skplanet\Desktop\kids library\검색결과.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        exit(1)
    
    # 1. 테이블 비우기
    clear_table()
    
    # 2. CSV 재업로드
    upload_csv_complete(csv_path)







