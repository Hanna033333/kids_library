from supabase_client import supabase
import json

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    winter_books = json.load(f)

print(f"총 {len(winter_books)}권의 겨울방학 추천 도서")
print()

matched_books = []
unmatched_books = []

for book in winter_books:
    title = book['서명']
    author = book['저자']
    publisher = book['발행자']
    callno = book['청구기호']
    
    print(f"매칭 시도: {title} - {author}")
    
    # 1차 매칭: 제목으로 검색
    try:
        response = supabase.table('childbook_items')\
            .select('id, title, author, publisher, pangyo_callno')\
            .ilike('title', f'%{title}%')\
            .execute()
        
        if response.data and len(response.data) > 0:
            # 여러 결과가 있으면 저자나 출판사로 필터링
            candidates = response.data
            
            # 저자명으로 필터링 (저자명에서 첫 번째 이름 추출)
            author_name = author.split()[0] if author else ''
            
            best_match = None
            for candidate in candidates:
                # 제목이 정확히 일치하거나 저자가 포함되어 있으면 선택
                if candidate['title'] == title or (author_name and author_name in (candidate.get('author') or '')):
                    best_match = candidate
                    break
            
            if not best_match and len(candidates) > 0:
                best_match = candidates[0]
            
            if best_match:
                matched_books.append({
                    'book_id': best_match['id'],
                    'title': title,
                    'db_title': best_match['title'],
                    'author': author,
                    'db_author': best_match.get('author'),
                    'callno': callno,
                    'db_callno': best_match.get('pangyo_callno'),
                    'age_group': book['대상-연번']
                })
                print(f"  ✅ 매칭 성공: ID {best_match['id']} - {best_match['title']}")
            else:
                unmatched_books.append(book)
                print(f"  ❌ 매칭 실패: 후보 없음")
        else:
            # 2차 매칭: 청구기호로 검색 (유 접두사 제거)
            clean_callno = callno.replace('유', '') if callno.startswith('유') else callno
            
            response2 = supabase.table('childbook_items')\
                .select('id, title, author, publisher, pangyo_callno')\
                .ilike('pangyo_callno', f'%{clean_callno}%')\
                .execute()
            
            if response2.data and len(response2.data) > 0:
                match = response2.data[0]
                matched_books.append({
                    'book_id': match['id'],
                    'title': title,
                    'db_title': match['title'],
                    'author': author,
                    'db_author': match.get('author'),
                    'callno': callno,
                    'db_callno': match.get('pangyo_callno'),
                    'age_group': book['대상-연번']
                })
                print(f"  ✅ 청구기호로 매칭: ID {match['id']} - {match['title']}")
            else:
                unmatched_books.append(book)
                print(f"  ❌ 매칭 실패: 데이터베이스에 없음")
    
    except Exception as e:
        print(f"  ❌ 에러: {e}")
        unmatched_books.append(book)
    
    print()

print("\n" + "="*50)
print(f"✅ 매칭 성공: {len(matched_books)}권")
print(f"❌ 매칭 실패: {len(unmatched_books)}권")
print("="*50)

# 결과 저장
with open('winter_books_matched.json', 'w', encoding='utf-8') as f:
    json.dump({
        'matched': matched_books,
        'unmatched': unmatched_books,
        'summary': {
            'total': len(winter_books),
            'matched_count': len(matched_books),
            'unmatched_count': len(unmatched_books)
        }
    }, f, ensure_ascii=False, indent=2)

print("\n✅ winter_books_matched.json 파일로 저장 완료!")

# SQL 생성
if matched_books:
    book_ids = [str(b['book_id']) for b in matched_books]
    sql = f"""-- 겨울방학 2026 큐레이션 태그 추가
UPDATE childbook_items 
SET curation_tag = '겨울방학2026'
WHERE id IN ({', '.join(book_ids)});

-- 확인 쿼리
SELECT id, title, author, curation_tag 
FROM childbook_items 
WHERE curation_tag = '겨울방학2026'
ORDER BY id;
"""
    
    with open('add_winter_curation_tag.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print("\n✅ add_winter_curation_tag.sql 파일 생성 완료!")
    print(f"   총 {len(book_ids)}권의 책에 큐레이션 태그 추가 예정")

# 매칭 실패한 책 목록 출력
if unmatched_books:
    print("\n⚠️ 매칭 실패한 책 목록:")
    for book in unmatched_books:
        print(f"  - {book['서명']} ({book['저자']})")
