#!/usr/bin/env python
"""
중복 청구기호 CSV에 Data4Library API 권차 정보 추가
"""
import requests
import csv
import time
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

def get_volume_info(isbn):
    """Data4Library API로 권차 정보 조회 (재시도 로직 포함)"""
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "isbn",
        "keyword": isbn,
        "format": "json",
        "startDt": "2000-01-01",
        "endDt": "2025-12-22"
    }
    
    # 3번 재시도
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            
            if docs:
                doc = docs[0].get("doc", {})
                vol = doc.get("vol", "").strip()
                return vol if vol else ""
            return ""
        except Exception as e:
            if attempt < 2:  # 마지막 시도가 아니면 재시도
                time.sleep(2)
                continue
            else:
                return ""  # 조용히 실패
    return ""

def add_volume_to_csv():
    """CSV 파일에 API 권차 정보 추가"""
    input_file = "duplicates_for_manual_check.csv"
    output_file = "duplicates_with_volume.csv"
    
    print("=" * 80)
    print("📚 Data4Library API 권차 정보 조회 시작")
    print("=" * 80)
    
    # CSV 읽기
    books = []
    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        books = list(reader)
    
    print(f"총 {len(books)}권의 책 조회 예정\n")
    
    # API 조회 및 권차 정보 추가
    found_count = 0
    for i, book in enumerate(books, 1):
        isbn = book["ISBN"].strip()
        title = book["제목"]
        
        print(f"[{i}/{len(books)}] {title[:30]:30} ({isbn})", end=" ")
        
        vol = get_volume_info(isbn)
        book["API_권차"] = vol
        
        if vol:
            print(f"✅ vol: '{vol}'")
            found_count += 1
        else:
            print("❌")
        
        # API 부하 방지 (1초 대기)
        if i < len(books):
            time.sleep(1)
    
    # 새 CSV 파일 작성
    print(f"\n📝 결과 파일 작성 중: {output_file}")
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["청구기호", "Library 청구기호", "제목", "ISBN", "API_권차", "권차(입력필요)", "DB_ID", "이미지URL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for book in books:
            writer.writerow({
                "청구기호": book["청구기호"],
                "Library 청구기호": book["Library 청구기호"],
                "제목": book["제목"],
                "ISBN": book["ISBN"],
                "API_권차": book["API_권차"],
                "권차(입력필요)": book["권차(입력필요)"],
                "DB_ID": book["DB_ID"],
                "이미지URL": book["이미지URL"]
            })
    
    print("\n" + "=" * 80)
    print(f"✅ 완료!")
    print(f"  - 총 조회: {len(books)}권")
    print(f"  - 권차 발견: {found_count}권")
    print(f"  - 결과 파일: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    add_volume_to_csv()
