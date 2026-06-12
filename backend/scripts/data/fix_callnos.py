from supabase_client import supabase

def fix_incorrect_callnos():
    """잘못된 청구기호 수정"""
    
    corrections = {
        '여름이 온다': '유 808.9-ㅂ966ㅂ-297',
        '팍스': '아 843.6-ㅍ26ㅍ-1',
        '불안': '유 808.9-ㅍ99-1',
        '기울어': '유 813.8-ㅇ929ㄱ',
        '행복한 우리 가족': '유 813.8-ㅎ313ㅎ=2',
        '이봉창': '아 813.8-ㅇ527ㄹ-21',
        '질문의 그림책': '유 813.8-ㅇ842ㅈ',
        '하이킹': '유 808.9-ㅇ175ㅂ-12',
        '덥석!': '유 808.9-ㅎ343한-1'
    }
    
    print("🔧 청구기호 수정 중...\n")
    
    updated = 0
    for title, correct_callno in corrections.items():
        try:
            # 제목으로 책 찾기
            res = supabase.table("childbook_items") \
                .select("id, pangyo_callno, web_scraped_callno") \
                .eq("title", title) \
                .execute()
            
            if res.data:
                book = res.data[0]
                book_id = book['id']
                
                print(f"📚 {title}")
                print(f"   현재: {book['pangyo_callno']}")
                print(f"   수정: {correct_callno}")
                
                # pangyo_callno와 web_scraped_callno 모두 업데이트
                supabase.table("childbook_items").update({
                    "pangyo_callno": correct_callno,
                    "web_scraped_callno": correct_callno
                }).eq("id", book_id).execute()
                
                updated += 1
                print(f"   ✅ 업데이트 완료\n")
            else:
                print(f"⚠️  '{title}' 책을 찾을 수 없습니다.\n")
                
        except Exception as e:
            print(f"❌ 오류 ({title}): {e}\n")
    
    print(f"\n✅ 총 {updated}권 수정 완료!")

if __name__ == "__main__":
    fix_incorrect_callnos()
