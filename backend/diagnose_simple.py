from supabase_client import supabase
from datetime import datetime

def diagnose_home_api():
    """홈 API의 데이터 조회 문제 진단"""
    
    # 현재 주차 계산 (프론트엔드와 동일한 로직)
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    week_number = int((now - start_of_year).total_seconds() / (7 * 24 * 60 * 60))
    age_offset = (week_number * 5) % 100
    research_offset = (week_number * 5) % 50
    
    print("=== TIME INFO ===")
    print(f"Week: {week_number} | Age offset: {age_offset} | Research offset: {research_offset}")
    print()
    
    # 연령 그룹별 데이터 확인
    age_groups = {
        '0-3': ['0세부터', '3세부터'],
        '4-7': ['5세부터', '7세부터'],
        '8-12': ['9세부터', '11세부터'],
        '13+': ['13세부터', '16세부터']
    }
    
    print("=== AGE GROUPS ===")
    for group_name, age_values in age_groups.items():
        # 전체 개수 확인
        count_response = supabase.table('childbook_items')\
            .select('id', count='exact')\
            .in_('age', age_values)\
            .or_('is_hidden.is.null,is_hidden.eq.false')\
            .execute()
        total_count = count_response.count
        
        # offset 범위의 데이터 확인
        data_response = supabase.table('childbook_items')\
            .select('id, title, age')\
            .in_('age', age_values)\
            .or_('is_hidden.is.null,is_hidden.eq.false')\
            .order('id')\
            .range(age_offset, age_offset + 6)\
            .execute()
        
        books = data_response.data
        books_in_range = len(books)
        
        print(f"{group_name}: total={total_count}, in_range={books_in_range}, has_data={books_in_range > 0}")
        if books:
            for book in books[:2]:
                print(f"  - ID {book['id']}: {book['title']}")
    
    print()
    print("=== RESEARCH COUNCIL ===")
    count_response = supabase.table('childbook_items')\
        .select('id', count='exact')\
        .eq('curation_tag', '어린이도서연구회')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .execute()
    total_count = count_response.count
    
    data_response = supabase.table('childbook_items')\
        .select('id, title')\
        .eq('curation_tag', '어린이도서연구회')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('id')\
        .range(research_offset, research_offset + 6)\
        .execute()
    
    books = data_response.data
    books_in_range = len(books)
    
    print(f"total={total_count}, in_range={books_in_range}, has_data={books_in_range > 0}")
    if books:
        for book in books[:2]:
            print(f"  - ID {book['id']}: {book['title']}")
    
    print()
    print("=== SONGPA LIBRARY ===")
    count_response = supabase.table('book_library_info')\
        .select('book_id', count='exact')\
        .ilike('library_name', '%송파%')\
        .execute()
    print(f"total={count_response.count}")

if __name__ == "__main__":
    diagnose_home_api()
