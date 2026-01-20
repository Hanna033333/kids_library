from supabase_client import supabase

# SQL 파일 읽기
with open('insert_winter_books.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

print("🚀 겨울방학 도서 40권 데이터베이스 추가 시작...")
print()

# SQL을 개별 INSERT 문으로 분리
sql_statements = []
current_statement = []

for line in sql_content.split('\n'):
    line = line.strip()
    
    # 주석이나 빈 줄 건너뛰기
    if not line or line.startswith('--'):
        continue
    
    current_statement.append(line)
    
    # INSERT 문 완료 (세미콜론으로 끝남)
    if line.endswith(');'):
        sql_statements.append(' '.join(current_statement))
        current_statement = []

print(f"총 {len(sql_statements)}개의 INSERT 문 실행 예정")
print()

# 각 INSERT 문 실행
success_count = 0
error_count = 0
errors = []

for i, sql in enumerate(sql_statements, 1):
    try:
        # Supabase에서 SQL 실행
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        success_count += 1
        print(f"✅ {i}/{len(sql_statements)} 완료")
    except Exception as e:
        error_count += 1
        errors.append((i, str(e)))
        print(f"❌ {i}/{len(sql_statements)} 실패: {e}")

print()
print("="*50)
print(f"✅ 성공: {success_count}개")
print(f"❌ 실패: {error_count}개")
print("="*50)

if errors:
    print("\n⚠️ 에러 목록:")
    for idx, err in errors:
        print(f"  {idx}. {err}")

# 확인 쿼리 실행
if success_count > 0:
    print("\n📊 데이터 확인 중...")
    
    try:
        # 총 개수 확인
        result = supabase.table('childbook_items')\
            .select('id', count='exact')\
            .eq('curation_tag', '겨울방학2026')\
            .execute()
        
        print(f"\n✅ 겨울방학2026 태그 책: {result.count}권")
        
        # 연령대별 확인
        result2 = supabase.table('childbook_items')\
            .select('age')\
            .eq('curation_tag', '겨울방학2026')\
            .execute()
        
        age_counts = {}
        for book in result2.data:
            age = book['age']
            age_counts[age] = age_counts.get(age, 0) + 1
        
        print("\n연령대별 분포:")
        for age, count in sorted(age_counts.items()):
            print(f"  {age}: {count}권")
        
    except Exception as e:
        print(f"❌ 확인 쿼리 실패: {e}")

print("\n✅ 작업 완료!")
