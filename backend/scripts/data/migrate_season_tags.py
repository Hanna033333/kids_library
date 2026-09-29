import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')

supabase_url = os.getenv('SUPABASE_URL')
# 반드시 Service Role Key를 사용하여 RLS를 우회합니다.
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# 1. 계절별 도서 맵핑 정의
SPRING_IDS = [9124, 9121, 9120, 8440, 8939, 9115, 9118, 9293, 8575, 9642]
SUMMER_IDS = [9970, 8134, 9565, 9505, 9506, 9508, 10230, 8785, 8432, 9968]
AUTUMN_IDS = [9772, 7600, 8429, 8519, 8481, 8359, 8430, 9967, 9765, 9102]
WINTER_IDS = [8370, 8379, 9950, 8376, 10467, 8715, 10807, 9205, 9298, 9299, 9600]

def update_book_tag(book_id: int, new_first_tag: str):
    res = supabase.table('childbook_items').select('id, title, curation_tag').eq('id', book_id).execute()
    if not res.data:
        print(f"Book {book_id} not found")
        return
    book = res.data[0]
    raw_tag = book.get('curation_tag') or ''
    tags = [t.strip().lstrip('#') for t in raw_tag.split(',') if t.strip()]
    
    # 기존 '계절' 및 4계절 태그 제거
    cleaned_tags = [t for t in tags if t not in ['계절', '봄', '여름', '가을', '겨울']]
    
    # 새 태그를 맨 앞에 삽입
    final_tags = [new_first_tag] + cleaned_tags
    final_tag_str = ','.join(final_tags)
    
    supabase.table('childbook_items').update({'curation_tag': final_tag_str}).eq('id', book_id).execute()
    print(f"Updated [{book['id']}] {book['title']}: {raw_tag} -> {final_tag_str}")

def main():
    print("=== 1. 봄 도서 태그 업데이트 ===")
    for bid in SPRING_IDS:
        update_book_tag(bid, '봄')
        
    print("\n=== 2. 여름 도서 태그 업데이트 ===")
    for bid in SUMMER_IDS:
        update_book_tag(bid, '여름')
        
    print("\n=== 3. 가을 도서 태그 업데이트 ===")
    for bid in AUTUMN_IDS:
        update_book_tag(bid, '가을')
        
    print("\n=== 4. 겨울 도서 태그 업데이트 ===")
    for bid in WINTER_IDS:
        update_book_tag(bid, '겨울')

    # 5. 기타 '계절' 태그가 남아있는 도서 정제
    print("\n=== 5. 기타 잔여 '계절' 태그 정제 ===")
    res = supabase.table('childbook_items').select('id, title, curation_tag, description').ilike('curation_tag', '%계절%').execute()
    for b in res.data:
        raw_tag = b.get('curation_tag') or ''
        tags = [t.strip().lstrip('#') for t in raw_tag.split(',') if t.strip()]
        if '계절' in tags:
            # 제목이나 설명에 따라 분류하거나 제거
            title = b['title'] or ''
            desc = b.get('description') or ''
            text = title + ' ' + desc
            
            if '여름' in text or '수박' in text:
                rep = '여름'
            elif '겨울' in text or '눈' in text or '산타' in text:
                rep = '겨울'
            elif '가을' in text or '단풍' in text or '도토리' in text:
                rep = '가을'
            elif '봄' in text or '꽃' in text or '새싹' in text:
                rep = '봄'
            else:
                rep = '자연관찰'
                
            new_tags = [rep if t == '계절' else t for t in tags]
            # 중복 제거
            seen = set()
            dedup = []
            for t in new_tags:
                if t not in seen:
                    seen.add(t)
                    dedup.append(t)
            new_tag_str = ','.join(dedup)
            supabase.table('childbook_items').update({'curation_tag': new_tag_str}).eq('id', b['id']).execute()
            print(f"Cleaned remaining [{b['id']}] {b['title']}: {raw_tag} -> {new_tag_str}")

if __name__ == '__main__':
    main()
