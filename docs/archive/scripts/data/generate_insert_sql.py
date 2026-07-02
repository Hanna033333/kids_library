import json

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# 연령 매핑
age_mapping = {
    '유아': '유아',
    '초등1~2학년': '7세부터',
    '초등3~4학년': '9세부터', 
    '초등5~6학년': '11세부터'
}

def get_age_from_target(target):
    """대상-연번에서 연령 추출"""
    if '유아' in target:
        return '유아'
    elif '초등1~2' in target:
        return '7세부터'
    elif '초등3~4' in target:
        return '9세부터'
    elif '초등5~6' in target:
        return '11세부터'
    return '유아'

def escape_sql_string(s):
    """SQL 문자열 이스케이프"""
    if not s:
        return ''
    return s.replace("'", "''")

# SQL 생성
sql_lines = []
sql_lines.append("-- 2025년 겨울방학 권장도서 40권 추가")
sql_lines.append("-- 생성일: 2026-01-19")
sql_lines.append("")

for i, book in enumerate(books, 1):
    title = escape_sql_string(book['서명'])
    author = escape_sql_string(book['저자'])
    publisher = escape_sql_string(book['발행자'])
    callno = escape_sql_string(book['청구기호'])
    age = get_age_from_target(book['대상-연번'])
    
    sql = f"""INSERT INTO childbook_items (
  title, 
  author, 
  publisher, 
  pangyo_callno, 
  age, 
  curation_tag,
  category
) VALUES (
  '{title}',
  '{author}',
  '{publisher}',
  '{callno}',
  '{age}',
  '겨울방학2026',
  '동화'
);"""
    
    sql_lines.append(f"-- {i}. {book['서명']} ({book['대상-연번']})")
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

with open('insert_winter_books.sql', 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"✅ insert_winter_books.sql 파일 생성 완료!")
print(f"   총 {len(books)}권의 책 INSERT 쿼리 생성")
print()
print("📝 SQL 파일 내용:")
print(f"   - INSERT 문: {len(books)}개")
print(f"   - 확인 쿼리: 3개")
print()
print("🔧 다음 단계:")
print("   1. insert_winter_books.sql 파일 확인")
print("   2. Supabase에서 SQL 실행")
print("   3. 확인 쿼리로 검증")
