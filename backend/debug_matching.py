import asyncio
import aiohttp
import re
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

def normalize_title(title: str) -> str:
    """제목 정규화 (공백, 문장부호 제거, 소문자 변환)"""
    if not title:
        return ""
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"[^a-zA-Z0-9가-힣]", "", title)
    return title.lower()

async def debug_matching():
    callno = "유 808.9-ㅂ966ㅂ"
    target_title = "헨리에타의 첫 겨울"
    target_isbn = "9788949110295"
    
    print(f"Debugging CallNo: {callno}")
    print(f"Target Title: {target_title} -> Norm: {normalize_title(target_title)}")
    print(f"Target ISBN: {target_isbn}")
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "callNumber",
        "keyword": callno.strip(),
        "startDt": "2000-01-01",
        "endDt": "2025-12-31",
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            docs = data.get("response", {}).get("docs", [])
            
            print(f"\nAPI Results: {len(docs)}")
            
            for i, doc_wrapper in enumerate(docs):
                doc = doc_wrapper.get("doc", {})
                title = doc.get("bookname", "")
                isbn = doc.get("isbn13", "")
                vol = doc.get("vol", "")
                
                norm_title = normalize_title(title)
                
                print(f"[{i+1}] {title} (ISBN: {isbn})")
                print(f"    Norm: {norm_title}")
                print(f"    Vol: {vol}")
                
                if normalize_title(target_title) == norm_title:
                    print("    ✅ Title Exact Match!")
                elif normalize_title(target_title) in norm_title:
                    print("    ✅ Title Target in API!")
                elif norm_title in normalize_title(target_title):
                    print("    ✅ Title API in Target!")
                    
                if target_isbn in isbn:
                    print("    ✅ ISBN Match!")

if __name__ == "__main__":
    asyncio.run(debug_matching())
