import os, re
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not found in backend/.env")

supabase = create_client(url, key)

res = supabase.table("childbook_items").select("id, title, author, publisher, isbn").ilike("curation_tag", "%교과서%").order("id").execute()
books = res.data

def refine_title(title: str, book_id: int) -> str:
    t = title.strip()
    
    # 0. 개별 특수 케이스 처리
    custom_map = {
        11568: "뜨고 지고!",
        11597: "보리 국어사전",
        11598: "초등 저학년 만만한 국어 세트",
        11611: "세계 도시탐험 만화 역사상식 세트",
        11624: "상상력을 키우는 그림 이야기 글자 없는 그림책 세트",
        11657: "한석봉",
        11660: "장영실",
        11718: "하늘과 바람과 별과 詩",
    }
    if book_id in custom_map:
        return custom_map[book_id]
        
    # 세트 도서 슬래시 뒤 내용 정리 (예: .../속담상담소...)
    if "/" in t and (" 세트" in t or "세트" in t):
        t = t.split("/")[0].strip()
        
    # 1. ' - ' 분리 (부제목 및 교과서/수상작/선정도서 정보 제거)
    if " - " in t:
        t = t.split(" - ")[0].strip()
        
    # 2. ' : ' 분리 (콜론 뒤 부제/설명 제거)
    if " : " in t:
        parts = t.split(" : ")
        t = parts[0].strip()
        
    # 3. 괄호 안의 판형 제거 (양장, 반양장, 개정판, 2025년 최신판 등)
    t = re.sub(r"\s*\((?:양장|반양장|보드북|페이퍼백|개정판|무선|2025년 최신판|신판|전\d+권)\)", "", t)
    
    # 4. HTML entity 정리
    t = t.replace("&lt;", "〈").replace("&gt;", "〉").replace("&amp;", "&")
    
    return t.strip()

updated_count = 0
failed_count = 0

for b in books:
    orig = b["title"]
    bid = b["id"]
    cleaned = refine_title(orig, bid)
    
    if orig != cleaned:
        try:
            update_res = supabase.table("childbook_items").update({"title": cleaned}).eq("id", bid).execute()
            if update_res.data:
                updated_count += 1
                print(f"[SUCCESS {updated_count}] ID {bid}: '{orig}' -> '{cleaned}'")
            else:
                print(f"[WARN] ID {bid} update returned no data")
        except Exception as e:
            failed_count += 1
            print(f"[ERROR] Failed to update ID {bid}: {e}")

print(f"\nFinished! Total updated: {updated_count}, Failed: {failed_count}")
