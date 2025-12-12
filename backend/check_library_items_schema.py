from supabase_client import supabase

print("library_items 테이블 스키마 확인 중...")
print()

try:
    # 기존 데이터 조회해서 컬럼명 확인
    data = supabase.table("library_items").select("*").limit(1).execute()
    
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
        print("테이블에 데이터가 없습니다. 빈 테이블일 수 있습니다.")
        # 빈 테이블이어도 스키마 정보를 얻기 위해 다른 방법 시도
        try:
            # 모든 컬럼 선택 시도
            all_data = supabase.table("library_items").select("*").execute()
            if all_data.data:
                print("\n테이블에 데이터가 있습니다:")
                print(f"총 {len(all_data.data)}개 행")
        except Exception as e2:
            print(f"테이블 접근 오류: {e2}")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()









