"""판교 도서관 코드 찾기"""
import requests
from core.config import DATA4LIBRARY_KEY

print("🔍 판교 도서관 코드 검색...\n")

url = "http://data4library.kr/api/libSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "region": "경기",
    "format": "json",
    "pageNo": 1,
    "pageSize": 100
}

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status: {r.status_code}\n")
    
    if r.status_code == 200:
        import json
        data = json.loads(r.text)
        
        if "response" in data and "libs" in data["response"]:
            libs = data["response"]["libs"]
            
            # 판교 관련 도서관 찾기
            pangyo_libs = []
            for lib_data in libs:
                lib = lib_data.get("lib", {})
                lib_name = lib.get("libName", "")
                if "판교" in lib_name or "성남" in lib_name:
                    pangyo_libs.append({
                        "name": lib_name,
                        "code": lib.get("libCode", ""),
                        "address": lib.get("address", "")
                    })
            
            if pangyo_libs:
                print("✅ 판교/성남 지역 도서관:")
                for lib in pangyo_libs:
                    print(f"  📚 {lib['name']}")
                    print(f"     코드: {lib['code']}")
                    print(f"     주소: {lib['address']}")
                    print()
            else:
                print("⚠️  판교 도서관을 찾을 수 없습니다.")
                print(f"\n전체 응답 (처음 1000자):\n{r.text[:1000]}")
        else:
            print(f"응답 구조 확인:\n{r.text[:500]}")
            
except Exception as e:
    print(f"❌ Error: {e}")

