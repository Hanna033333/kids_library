import json
import re

# JSON 파일 읽기
with open('winter_books_callno_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📊 크롤링 결과 분석")
print(f"총 {data['total']}권 / 성공 {data['success']}권 / 실패 {data['fail']}권")
print()

def clean_callno(raw_callno):
    """청구기호에서 불필요한 정보 제거"""
    if not raw_callno:
        return None
    
    # "저자 : ... 발행자: ... 발행연도: ..." 패턴에서 청구기호만 추출
    # 마지막 부분이 청구기호
    parts = raw_callno.split('발행연도:')
    if len(parts) >= 2:
        # 발행연도 이후의 텍스트에서 청구기호 추출
        after_year = parts[-1].strip()
        # 연도 제거 (4자리 숫자)
        callno = re.sub(r'^\d{4}\s+', '', after_year)
        return callno.strip()
    
    return raw_callno.strip()

# 청구기호 정제
cleaned_results = []
for result in data['results']:
    if result['status'] == 'success' and result['callno']:
        cleaned_callno = clean_callno(result['callno'])
        cleaned_results.append({
            'title': result['title'],
            'callno': cleaned_callno
        })
        print(f"✅ {result['title']}")
        print(f"   원본: {result['callno'][:50]}...")
        print(f"   정제: {cleaned_callno}")
        print()

print(f"\n정제 완료: {len(cleaned_results)}권")

# UPDATE SQL 생성
if cleaned_results:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 청구기호 업데이트")
    sql_lines.append(f"-- 크롤링 결과: {len(cleaned_results)}/{data['total']}권 성공")
    sql_lines.append("-- 생성일: 2026-01-19")
    sql_lines.append("")
    
    for result in cleaned_results:
        title_escaped = result['title'].replace("'", "''")
        callno_escaped = result['callno'].replace("'", "''")
        
        sql = f"""UPDATE childbook_items 
SET pangyo_callno = '{callno_escaped}'
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
        sql_lines.append(f"-- {result['title']}: {result['callno']}")
        sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag = '겨울방학2026'")
    sql_lines.append("  AND pangyo_callno IS NOT NULL")
    sql_lines.append("ORDER BY title;")
    
    with open('update_winter_callno_clean.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"\n✅ update_winter_callno_clean.sql 파일 생성 완료!")
    print(f"   {len(cleaned_results)}개 UPDATE 문 포함")
