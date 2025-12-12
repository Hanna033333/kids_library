from supabase_client import supabase

print("테이블 스키마 확인 중...")
print()

try:
    # 기존 데이터 조회해서 컬럼명 확인
    data = supabase.table("childbook_items").select("*").limit(1).execute()
    
    if data.data and len(data.data) > 0:
        print("현재 테이블의 컬럼명:")
        print("-" * 60)
        for key in data.data[0].keys():
            print(f"  - {key}")
        print("-" * 60)
        print()
        print("샘플 데이터:")
        print(data.data[0])
    else:
        print("테이블에 데이터가 없습니다.")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()









