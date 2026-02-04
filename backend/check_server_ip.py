"""
서버 IP 확인 및 Data4Library API 테스트
"""
import asyncio
import aiohttp
import sys
sys.path.insert(0, '.')

from core.config import DATA4LIBRARY_KEY

async def check_server_ip():
    """서버 IP 확인 및 API 테스트"""
    
    print("=" * 60)
    print("🌐 서버 IP 및 API 연결 확인")
    print("=" * 60)
    print()
    
    async with aiohttp.ClientSession() as session:
        # 1. 현재 서버 IP 확인
        print("1️⃣ 현재 서버 IP 확인:")
        try:
            async with session.get("https://api.ipify.org?format=json", timeout=5) as resp:
                if resp.status == 200:
                    ip_data = await resp.json()
                    current_ip = ip_data.get("ip")
                    print(f"   ✅ 현재 IP: {current_ip}")
                else:
                    print(f"   ❌ IP 조회 실패: {resp.status}")
                    current_ip = None
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            current_ip = None
        
        print()
        
        # 2. Data4Library 등록 IP 확인
        print("2️⃣ Data4Library 등록 정보:")
        print(f"   API 키: {DATA4LIBRARY_KEY[:10]}...{DATA4LIBRARY_KEY[-5:]}")
        print(f"   등록 IP: 74.220.48.242 (스크린샷 기준)")
        print()
        
        # 3. IP 비교
        if current_ip:
            print("3️⃣ IP 비교:")
            if current_ip == "74.220.48.242":
                print(f"   ✅ 일치: 현재 IP와 등록 IP가 동일합니다!")
            else:
                print(f"   ⚠️  불일치:")
                print(f"      현재 IP: {current_ip}")
                print(f"      등록 IP: 74.220.48.242")
                print()
                print("   💡 이것이 API 한도 초과의 원인일 수 있습니다!")
                print("      → Data4Library에 새 IP 등록 필요")
        
        print()
        print("=" * 60)
        
        # 4. API 테스트
        print("4️⃣ Data4Library API 연결 테스트:")
        url = "http://data4library.kr/api/bookExist"
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": "141231",
            "isbn13": "9788931005158",
            "format": "json"
        }
        
        try:
            async with session.get(url, params=params, timeout=5) as resp:
                print(f"   응답 코드: {resp.status}")
                data = await resp.json()
                
                error = data.get("response", {}).get("error")
                if error:
                    print(f"   ❌ 에러: {error}")
                    if "IP" in error or "ip" in error.lower():
                        print("   💡 IP 관련 에러 → 등록된 IP 확인 필요!")
                else:
                    result = data.get("response", {}).get("result", {})
                    has_book = result.get("hasBook", "N")
                    print(f"   ✅ 정상 응답: hasBook={has_book}")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
        
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_server_ip())
