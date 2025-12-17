import csv
from supabase_client import supabase
from collections import defaultdict

def analyze_callnos():
    print("데이터 조회 중...")
    
    books = []
    chunk_size = 1000
    start = 0
    while True:
        # vol 컬럼도 같이 조회
        response = supabase.table("childbook_items").select("id, title, pangyo_callno, vol").range(start, start + chunk_size - 1).execute()
        chunk = response.data
        if not chunk:
            break
        books.extend(chunk)
        if len(chunk) < chunk_size:
            break
        start += chunk_size
        
    total_books = len(books)
    print(f"총 도서 수: {total_books}권")
    
    # 중복 분석 (청구기호 + 권차)
    id_map = defaultdict(list)
    for b in books:
        callno = b.get("pangyo_callno") or ""
        vol = b.get("vol") or ""
        if not callno.strip():
            continue
            
        # 식별자: "청구기호" + " (Vol:권차)" (권차가 있을 때만)
        identifier = callno.strip()
        if vol.strip():
            identifier += f" (Vol:{vol.strip()})"
            
        id_map[identifier].append(b)
        
    duplicates = {k: v for k, v in id_map.items() if len(v) > 1}
    
    print(f"\n[중복 분석 결과]")
    print(f"고유 식별자 수: {len(id_map)}개")
    if not duplicates:
        print("✅ 중복된 도서가 없습니다! (성공)")
    else:
        print(f"⚠️ 여전히 중복된 식별자가 {len(duplicates)}개 있습니다.")
        for k, v in duplicates.items():
            print(f"  - {k}: {len(v)}권 중복")
            has_vol = "Vol:" in k
            if not has_vol:
                print("    (권차 정보 없음 - 사용자 확인 필요)")
            for b in v:
                print(f"    * ID {b['id']}: {b['title']}")

if __name__ == "__main__":
    analyze_callnos()
