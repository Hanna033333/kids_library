from supabase_client import supabase

# 현재 사용 중인 age 값 조회
print("📊 현재 데이터베이스의 age 값 종류:")
print()

try:
    # DISTINCT age 값 조회
    result = supabase.table('childbook_items')\
        .select('age')\
        .execute()
    
    # 고유한 age 값 추출
    ages = set()
    for book in result.data:
        if book['age']:
            ages.add(book['age'])
    
    # 정렬하여 출력
    sorted_ages = sorted(ages)
    
    print(f"총 {len(sorted_ages)}개의 age 값:")
    for i, age in enumerate(sorted_ages, 1):
        print(f"  {i}. '{age}'")
    
    print()
    print("📝 각 age 값별 책 개수:")
    
    # 각 age별 개수 확인
    age_counts = {}
    for book in result.data:
        age = book['age'] if book['age'] else 'NULL'
        age_counts[age] = age_counts.get(age, 0) + 1
    
    for age in sorted(age_counts.keys()):
        print(f"  {age}: {age_counts[age]}권")
    
except Exception as e:
    print(f"❌ 에러: {e}")
