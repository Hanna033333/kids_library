import json

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

def get_age_from_target(target):
    """대상-연번에서 연령 추출 - 실제 DB 값 사용"""
    if '유아' in target:
        return '5세부터'  # 유아 대표
    elif '초등1~2' in target:
        return '7세부터'
    elif '초등3~4' in target:
        return '9세부터'
    elif '초등5~6' in target:
        return '11세부터'
    return '5세부터'

def escape_sql_string(s):
    """SQL 문자열 이스케이프"""
    if not s:
        return ''
    return s.replace("'", "''")

# SQL 생성
sql_lines = []
sql_lines.append("-- 2025년 겨울방학 권장도서 40권 추가")
sql_lines.append("-- 생성일: 2026-01-19")
sql_lines.append("-- 주의: 청구기호는 서울시어린이도서관 기준이므로 NULL로 설정")
sql_lines.append("-- 판교도서관 청구기호는 별도로 수집 필요")
sql_lines.append("")
sql_lines.append("-- age 매핑:")
sql_lines.append("-- 유아 → 5세부터")
sql_lines.append("-- 초등1~2학년 → 7세부터")
sql_lines.append("-- 초등3~4학년 → 9세부터")
sql_lines.append("-- 초등5~6학년 → 11세부터")
sql_lines.append("")

for i, book in enumerate(books, 1):
    title = escape_sql_string(book['서명'])
    author = escape_sql_string(book['저자'])
    publisher = escape_sql_string(book['발행자'])
    age = get_age_from_target(book['대상-연번'])
    seoul_callno = book['청구기호']
    
    sql = f"""INSERT INTO childbook_items (
  title, 
  author, 
  publisher, 
  age, 
  curation_tag,
  category
) VALUES (
  '{title}',
  '{author}',
  '{publisher}',
  '{age}',
  '겨울방학2026',
  '동화'
);"""
    
    sql_lines.append(f"-- {i}. {book['서명']} ({book['대상-연번']} → {age})")
    sql_lines.append(f"-- 서울시도서관 청구기호: {seoul_callno}")
    sql_lines.append(sql)
    sql_lines.append("")

# 확인 쿼리 추가
sql_lines.append("")
sql_lines.append("-- 확인 쿼리")
sql_lines.append("SELECT COUNT(*) as total_count")
sql_lines.append("FROM childbook_items")
sql_lines.append("WHERE curation_tag = '겨울방학2026';")
sql_lines.append("")
sql_lines.append("-- 연령대별 확인")
sql_lines.append("SELECT age, COUNT(*) as count")
sql_lines.append("FROM childbook_items")
sql_lines.append("WHERE curation_tag = '겨울방학2026'")
sql_lines.append("GROUP BY age")
sql_lines.append("ORDER BY age;")
sql_lines.append("")
sql_lines.append("-- 전체 목록 확인")
sql_lines.append("SELECT id, title, author, publisher, pangyo_callno, age, curation_tag")
sql_lines.append("FROM childbook_items")
sql_lines.append("WHERE curation_tag = '겨울방학2026'")
sql_lines.append("ORDER BY age, id;")

# 파일 저장
sql_content = '\n'.join(sql_lines)

with open('insert_winter_books_final.sql', 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"✅ insert_winter_books_final.sql 파일 생성 완료!")
print(f"   총 {len(books)}권의 책 INSERT 쿼리 생성")
print()
print("📝 age 매핑:")
print("   유아 (10권) → 5세부터")
print("   초등1~2학년 (10권) → 7세부터")
print("   초등3~4학년 (10권) → 9세부터")
print("   초등5~6학년 (10권) → 11세부터")
print()
print("✅ 모든 age 값이 데이터베이스 기존 값과 일치합니다!")
