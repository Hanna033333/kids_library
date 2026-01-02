"""childbook_items 테이블 덤프 스크립트"""
import json
from datetime import datetime
from supabase_client import supabase


def dump_childbook_items():
    """childbook_items 테이블의 모든 데이터를 JSON 파일로 덤프"""
    print("childbook_items 테이블 덤프 시작...")

    
    # 전체 데이터 가져오기 (페이지네이션 처리)
    all_items = []
    page_size = 1000
    offset = 0
    
    while True:
        print(f"데이터 가져오는 중... (offset: {offset})")
        
        response = supabase.table("childbook_items") \
            .select("*") \
            .range(offset, offset + page_size - 1) \
            .execute()
        
        items = response.data
        
        if not items:
            break
            
        all_items.extend(items)
        print(f"  - {len(items)}개 항목 가져옴 (총 {len(all_items)}개)")
        
        if len(items) < page_size:
            break
            
        offset += page_size
    
    # 파일명에 타임스탬프 추가
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"childbook_items_dump_{timestamp}.json"
    
    # JSON 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n덤프 완료!")
    print(f"파일명: {filename}")
    print(f"총 {len(all_items)}개 항목 저장됨")
    
    # 통계 정보 출력
    print("\n=== 통계 정보 ===")
    
    # 컬럼 정보
    if all_items:
        columns = list(all_items[0].keys())
        print(f"컬럼 수: {len(columns)}")
        print(f"컬럼 목록: {', '.join(columns)}")
    
    # callno 있는 항목
    items_with_callno = sum(1 for item in all_items if item.get('callno'))
    print(f"callno 있는 항목: {items_with_callno}개")
    
    # web_scraped_callno 있는 항목
    items_with_web_callno = sum(1 for item in all_items if item.get('web_scraped_callno'))
    print(f"web_scraped_callno 있는 항목: {items_with_web_callno}개")
    
    # vol 있는 항목
    items_with_vol = sum(1 for item in all_items if item.get('vol'))
    print(f"vol 있는 항목: {items_with_vol}개")
    
    # curation_tag 있는 항목
    items_with_curation = sum(1 for item in all_items if item.get('curation_tag'))
    print(f"curation_tag 있는 항목: {items_with_curation}개")
    
    return filename

if __name__ == "__main__":
    dump_childbook_items()
