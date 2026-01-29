from supabase_client import supabase
from datetime import datetime
import json
import sys

def diagnose_home_api():
    """홈 API의 데이터 조회 문제 진단"""
    
    results = {}
    
    # 현재 주차 계산 (프론트엔드와 동일한 로직)
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    week_number = int((now - start_of_year).total_seconds() / (7 * 24 * 60 * 60))
    age_offset = (week_number * 5) % 100
    research_offset = (week_number * 5) % 50
    
    results['time_info'] = {
        'current_time': str(now),
        'week_number': week_number,
        'age_offset': age_offset,
        'research_offset': research_offset
    }
    
    # 연령 그룹별 데이터 확인
    age_groups = {
        '0-3': ['0세부터', '3세부터'],
        '4-7': ['5세부터', '7세부터'],
        '8-12': ['9세부터', '11세부터'],
        '13+': ['13세부터', '16세부터']
    }
    
    results['age_groups'] = {}
    
    for group_name, age_values in age_groups.items():
        group_result = {
            'age_values': age_values,
            'total_count': 0,
            'books_in_range': 0,
            'has_data': False,
            'offset_exceeds_total': False,
            'sample_books': []
        }
        
        try:
            # 전체 개수 확인
            count_response = supabase.table('childbook_items')\
                .select('id', count='exact')\
                .in_('age', age_values)\
                .or_('is_hidden.is.null,is_hidden.eq.false')\
                .execute()
            group_result['total_count'] = count_response.count
            
            # offset 범위의 데이터 확인
            data_response = supabase.table('childbook_items')\
                .select('id, title, age, pangyo_callno')\
                .in_('age', age_values)\
                .or_('is_hidden.is.null,is_hidden.eq.false')\
                .order('id')\
                .range(age_offset, age_offset + 6)\
                .execute()
            
            books = data_response.data
            group_result['books_in_range'] = len(books)
            group_result['has_data'] = len(books) > 0
            group_result['offset_exceeds_total'] = age_offset >= count_response.count
            
            if books:
                group_result['sample_books'] = [
                    {
                        'id': book['id'],
                        'title': book['title'],
                        'age': book['age']
                    }
                    for book in books[:3]
                ]
                
        except Exception as e:
            group_result['error'] = str(e)
        
        results['age_groups'][group_name] = group_result
    
    # 어린이도서연구회 책 확인
    research_result = {
        'total_count': 0,
        'books_in_range': 0,
        'has_data': False,
        'offset_exceeds_total': False,
        'sample_books': []
    }
    
    try:
        count_response = supabase.table('childbook_items')\
            .select('id', count='exact')\
            .eq('curation_tag', '어린이도서연구회')\
            .or_('is_hidden.is.null,is_hidden.eq.false')\
            .execute()
        research_result['total_count'] = count_response.count
        
        data_response = supabase.table('childbook_items')\
            .select('id, title, curation_tag')\
            .eq('curation_tag', '어린이도서연구회')\
            .or_('is_hidden.is.null,is_hidden.eq.false')\
            .order('id')\
            .range(research_offset, research_offset + 6)\
            .execute()
        
        books = data_response.data
        research_result['books_in_range'] = len(books)
        research_result['has_data'] = len(books) > 0
        research_result['offset_exceeds_total'] = research_offset >= count_response.count
        
        if books:
            research_result['sample_books'] = [
                {
                    'id': book['id'],
                    'title': book['title']
                }
                for book in books[:3]
            ]
            
    except Exception as e:
        research_result['error'] = str(e)
    
    results['research_council'] = research_result
    
    # 송파도서관 데이터 확인
    songpa_result = {
        'total_count': 0,
        'has_data': False,
        'sample_data': []
    }
    
    try:
        count_response = supabase.table('book_library_info')\
            .select('book_id', count='exact')\
            .ilike('library_name', '%송파%')\
            .execute()
        songpa_result['total_count'] = count_response.count
        
        response = supabase.table('book_library_info')\
            .select('book_id, library_name, callno')\
            .ilike('library_name', '%송파%')\
            .limit(5)\
            .execute()
        
        songpa_data = response.data
        songpa_result['has_data'] = len(songpa_data) > 0
        
        if songpa_data:
            songpa_result['sample_data'] = [
                {
                    'book_id': item['book_id'],
                    'library_name': item['library_name'],
                    'callno': item['callno']
                }
                for item in songpa_data
            ]
            
    except Exception as e:
        songpa_result['error'] = str(e)
    
    results['songpa_library'] = songpa_result
    
    # JSON 출력 (UTF-8로 stdout에 직접)
    json_str = json.dumps(results, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(json_str.encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

if __name__ == "__main__":
    diagnose_home_api()
