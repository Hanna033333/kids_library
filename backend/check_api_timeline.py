"""
API 호출 기록 추적 - 여러 시간대에 테스트
"""
import asyncio
import aiohttp
import sys
from datetime import datetime
sys.path.insert(0, '.')

from core.config import DATA4LIBRARY_KEY

async def test_api_timeline():
    """API 호출을 여러 번 시도하여 언제부터 막혔는지 확인"""
    
    # 테스트용 ISBN (곰 사냥을 떠나자)
    test_isbn = "9788931005158"
    lib_code = "141231"
    
    print("=" * 60)
    print("🔍 API 호출 타임라인 테스트")
    print("=" * 60)
    print(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    url = "http://data4library.kr/api/bookExist"
    
    # 5번 연속 호출하여 패턴 확인
    for i in range(5):
        print(f"\n[테스트 {i+1}/5] {datetime.now().strftime('%H:%M:%S')}")
        
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": lib_code,
            "isbn13": test_isbn,
            "format": "json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    data = await response.json()
                    
                    # 에러 체크
                    error = data.get("response", {}).get("error")
                    if error:
                        print(f"❌ 에러: {error}")
                        if "500건" in error:
                            print("   ⚠️  일일 한도 초과 확인!")
                    else:
                        result = data.get("response", {}).get("result", {})
                        has_book = result.get("hasBook", "N")
                        print(f"✅ 정상 응답: hasBook={has_book}")
                        
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
        
        # 1초 대기
        if i < 4:
            await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("💡 분석:")
    print("   - 모든 호출이 '500건 초과' 에러 → 오늘 이미 한도 초과")
    print("   - 일부만 에러 → 방금 한도 초과")
    print("   - 모두 정상 → 한도 여유 있음")
    print("=" * 60)

asyncio.run(test_api_timeline())
