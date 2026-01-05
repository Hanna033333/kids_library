import csv
from datetime import datetime
from supabase_client import supabase
import re

def is_similar_callno(original, scraped):
    """
    청구기호가 유사한지 판단
    1. 권차 정보 추가: 808.9-ㅂ966ㅂ → 808.9-ㅂ966ㅂ-259
    2. 복본 번호: 813.8-ㄷ97 → 813.8-ㄷ97-16=2
    3. 시리즈 번호: 082-ㅇ546 → 082-ㅇ546-4
    """
    if not original or not scraped:
        return False
    
    # 기본 청구기호 추출 (-, =, v. 앞부분)
    def get_base(callno):
        # 권차/복본/시리즈 번호 제거
        base = re.split(r'[-=](?=\d)|(?:v\.)', callno)[0]
        return base.strip()
    
    base_original = get_base(original)
    base_scraped = get_base(scraped)
    
    # 기본 부분이 같으면 유사한 것으로 판단
    return base_original == base_scraped

def update_callnos():
    """청구기호 업데이트"""
    print("📚 청구기호 업데이트 시작...\n")
    
    # 모든 책 조회
    res = supabase.table("childbook_items") \
        .select("id, title, author, pangyo_callno, web_scraped_callno") \
        .execute()
    
    books = res.data
    
    updated = 0
    skipped_different = []
    
    for book in books:
        book_id = book['id']
        original = book.get('pangyo_callno')
        scraped = book.get('web_scraped_callno')
        
        # NULL/NotFound 처리
        if not original or not scraped or scraped == 'NotFound':
            continue
        
        # 이미 같으면 스킵
        if original == scraped:
            continue
        
        # 유사한지 판단
        if is_similar_callno(original, scraped):
            # 업데이트
            supabase.table("childbook_items") \
                .update({"pangyo_callno": scraped}) \
                .eq("id", book_id) \
                .execute()
            updated += 1
            
            if updated % 50 == 0:
                print(f"   진행 중: {updated}권 업데이트...")
        else:
            # 완전히 다른 경우 - CSV로 저장
            skipped_different.append({
                'id': book_id,
                'title': book['title'],
                'author': book.get('author', ''),
                'original_callno': original,
                'scraped_callno': scraped
            })
    
    print(f"\n✅ 업데이트 완료: {updated}권")
    print(f"⚠️  완전히 다른 청구기호: {len(skipped_different)}권\n")
    
    # 완전히 다른 것들 CSV로 저장
    if skipped_different:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"different_callnos_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'author', 'original_callno', 'scraped_callno'])
            writer.writeheader()
            writer.writerows(skipped_different)
        
        print(f"📄 완전히 다른 청구기호 저장: {filename}")
        print(f"   확인 후 수동으로 처리해주세요.\n")
    
    return updated, len(skipped_different)

if __name__ == "__main__":
    update_callnos()
