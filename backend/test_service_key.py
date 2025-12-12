from supabase import create_client
import os

# 서비스 키 직접 설정
url = "https://gglaltjiamrzgitvlvlc.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnbGFsdGppYW1yemdpdHZsdmxjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDY5NjA0MCwiZXhwIjoyMDgwMjcyMDQwfQ.YtXk1GmvBYvwvmJd-2Z94z-8aa_bXXB-3bdks87HIlk"

supabase = create_client(url, service_key)

# 테스트: library_items 테이블에 데이터 삽입 테스트
test_data = {
    "isbn13": "9781234567890",
    "title": "테스트 도서",
    "author": "테스트 저자",
    "callno": "아123-456",
    "lib_code": "141231"
}

try:
    result = supabase.table("library_items").insert(test_data).execute()
    print("✅ 서비스 키로 데이터 삽입 성공!")
    print(f"삽입된 데이터: {result.data}")
    
    # 테스트 데이터 삭제
    supabase.table("library_items").delete().eq("isbn13", "9781234567890").execute()
    print("✅ 테스트 데이터 삭제 완료")
except Exception as e:
    print(f"❌ 오류 발생: {e}")






