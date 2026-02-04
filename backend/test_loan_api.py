"""
대출 가능 여부 API 직접 테스트
"""
import asyncio
import aiohttp
import sys
sys.path.insert(0, '.')

from core.config import DATA4LIBRARY_KEY
from supabase_client import supabase

PANGYO_LIB_CODE = "141231"

async def test_loan_api():
    """실제 책 데이터로 API 테스트"""
    
    # 1. API 키 확인
    print("=" * 60)
    print("🔑 API 키 확인")
    print("=" * 60)
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY가 설정되지 않았습니다!")
        print("   .env 파일을 확인하세요.")
        return
    
    print(f"✅ API 키 존재: {DATA4LIBRARY_KEY[:10]}...{DATA4LIBRARY_KEY[-5:]}")
    print(f"   길이: {len(DATA4LIBRARY_KEY)}")
    print()
    
    # 2. 테스트할 책 가져오기 (실제 DB에서)
    print("=" * 60)
    print("📚 테스트 도서 조회")
    print("=" * 60)
    
    result = supabase.table('childbook_items').select(
        'id, title, isbn, pangyo_callno'
    ).not_.is_('pangyo_callno', 'null').limit(3).execute()
    
    if not result.data:
        print("❌ 테스트할 책이 없습니다.")
        return
    
    books = result.data
    print(f"✅ {len(books)}권의 책을 테스트합니다.\n")
    
    # 3. 각 책에 대해 API 호출
    for i, book in enumerate(books, 1):
        print(f"\n{'='*60}")
        print(f"📖 테스트 {i}/{len(books)}: {book['title']}")
        print(f"{'='*60}")
        print(f"ISBN: {book['isbn']}")
        print(f"청구기호: {book['pangyo_callno']}")
        print()
        
        # API 호출
        url = "http://data4library.kr/api/bookExist"
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_LIB_CODE,
            "isbn13": book['isbn'],
            "format": "json"
        }
        
        print(f"🌐 API 요청:")
        print(f"   URL: {url}")
        print(f"   libCode: {PANGYO_LIB_CODE}")
        print(f"   isbn13: {book['isbn']}")
        print()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    print(f"📡 응답 상태: {response.status}")
                    
                    if response.status != 200:
                        print(f"❌ HTTP 오류: {response.status}")
                        text = await response.text()
                        print(f"   응답 내용: {text[:200]}")
                        continue
                    
                    data = await response.json()
                    print(f"✅ JSON 응답 수신")
                    print()
                    
                    # 응답 구조 출력
                    print("📋 전체 응답 구조:")
                    import json
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print()
                    
                    # 파싱
                    result_data = data.get("response", {}).get("result", {})
                    has_book = result_data.get("hasBook", "N")
                    loan_available = result_data.get("loanAvailable", "N")
                    
                    print("🔍 파싱 결과:")
                    print(f"   hasBook: {has_book}")
                    print(f"   loanAvailable: {loan_available}")
                    print()
                    
                    # 최종 판정
                    if has_book == "Y":
                        status = "대출가능" if loan_available == "Y" else "대출중"
                        print(f"✅ 최종 상태: {status}")
                    else:
                        print(f"⚠️  최종 상태: 미소장")
                        print(f"   (예상: 소장 - 청구기호 있음)")
                        print(f"   ⚠️  API와 DB 불일치 감지!")
                    
        except asyncio.TimeoutError:
            print("❌ 타임아웃 (5초 초과)")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_loan_api())
