"""전국 공공도서관 마스터 데이터 수집 스크립트 (정보나루 libSrch API)

실행:
    ./backend/venv/bin/python backend/scripts/fetch_national_libraries.py
결과:
    backend/data/libraries.json
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from core.config import DATA4LIBRARY_KEY
from services.loan_status import LIBRARY_CODE_MAP

OUTPUT_PATH = BACKEND_DIR / "data" / "libraries.json"

REGION_ALIAS = {
    "서울특별시": "서울",
    "서울시": "서울",
    "서울": "서울",
    "경기도": "경기",
    "경기": "경기",
    "인천광역시": "인천",
    "인천시": "인천",
    "인천": "인천",
    "부산광역시": "부산",
    "부산시": "부산",
    "부산": "부산",
    "대구광역시": "대구",
    "대구시": "대구",
    "대구": "대구",
    "대전광역시": "대전",
    "대전시": "대전",
    "대전": "대전",
    "광주광역시": "광주",
    "광주시": "광주",
    "광주": "광주",
    "울산광역시": "울산",
    "울산시": "울산",
    "울산": "울산",
    "세종특별자치시": "세종",
    "세종시": "세종",
    "세종": "세종",
    "강원특별자치도": "강원",
    "강원도": "강원",
    "강원": "강원",
    "충청북도": "충북",
    "충북": "충북",
    "충청남도": "충남",
    "충남": "충남",
    "전북특별자치도": "전북",
    "전라북도": "전북",
    "전북": "전북",
    "전라남도": "전남",
    "전남": "전남",
    "경상북도": "경북",
    "경북": "경북",
    "경상남도": "경남",
    "경남": "경남",
    "제주특별자치도": "제주",
    "제주도": "제주",
    "제주": "제주",
}


def extract_region(address: str) -> str:
    if not address:
        return "기타"
    first = address.strip().split()[0]
    for prefix, short in REGION_ALIAS.items():
        if first.startswith(prefix):
            return short
    return first[:2] if len(first) >= 2 else "기타"


def to_float(val) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        f = float(val)
        return f if f != 0.0 else None
    except (ValueError, TypeError):
        return None


def fetch_all_libraries() -> List[Dict]:
    if not DATA4LIBRARY_KEY:
        raise RuntimeError("DATA4LIBRARY_KEY 환경 변수가 설정되어 있지 않습니다.")

    legacy_code_to_name = {code: name for name, code in LIBRARY_CODE_MAP.items()}
    libraries_by_code: Dict[str, Dict] = {}

    page_no = 1
    page_size = 100
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CheckjariBot/1.0)"})

    while True:
        url = "http://data4library.kr/api/libSrch"
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "pageNo": page_no,
            "pageSize": page_size,
            "format": "json",
        }
        print(f"📡 Fetching libSrch page {page_no} (pageSize={page_size})...")
        data = None
        for attempt in range(1, 4):
            try:
                resp = session.get(url, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                print(f"   ⚠️ 시도 {attempt}/3 실패: {e}")
                if attempt == 3:
                    raise
        response_body = data.get("response", {})
        num_found = int(response_body.get("numFound", 0))
        libs = response_body.get("libs", [])

        if not libs:
            break

        for item in libs:
            lib = item.get("lib", {})
            code = str(lib.get("libCode", "")).strip()
            name = str(lib.get("libName", "")).strip()
            if not code or not name:
                continue

            address = str(lib.get("address", "") or "").strip()
            is_verified = code in legacy_code_to_name
            # 기존 13개 검증 도서관은 DB book_library_info.library_name과 100% 호환되도록 기존 이름 우선 보존
            canonical_name = legacy_code_to_name[code] if is_verified else name

            libraries_by_code[code] = {
                "code": code,
                "name": canonical_name,
                "official_name": name,
                "address": address,
                "region": extract_region(address),
                "lat": to_float(lib.get("latitude")),
                "lng": to_float(lib.get("longitude")),
                "homepage": str(lib.get("homepage", "") or "").strip(),
                "tel": str(lib.get("tel", "") or "").strip(),
                "closed": str(lib.get("closed", "") or "").strip(),
                "operating_time": str(lib.get("operatingTime", "") or "").strip(),
                "has_callno_db": is_verified,
            }

        print(f"   → 누적 {len(libraries_by_code)}개 / 전체 {num_found}개")
        if page_no * page_size >= num_found:
            break
        page_no += 1

    # 기존 13개 도서관 중 혹시 API 결과에 누락된 항목이 있으면 안전하게 보강
    for legacy_name, code in LIBRARY_CODE_MAP.items():
        if code not in libraries_by_code:
            libraries_by_code[code] = {
                "code": code,
                "name": legacy_name,
                "official_name": legacy_name,
                "address": "",
                "region": "기타",
                "lat": None,
                "lng": None,
                "homepage": "",
                "tel": "",
                "closed": "",
                "operating_time": "",
                "has_callno_db": True,
            }

    result = sorted(libraries_by_code.values(), key=lambda x: x["name"])
    return result


def main():
    libraries = fetch_all_libraries()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(libraries, f, ensure_ascii=False, indent=2)

    verified_count = sum(1 for lib in libraries if lib["has_callno_db"])
    with_coords = sum(1 for lib in libraries if lib["lat"] and lib["lng"])
    print(f"\n✅ 저장 완료: {OUTPUT_PATH}")
    print(f"   - 총 공공도서관 수: {len(libraries)}개")
    print(f"   - 기존 DB 검증 도서관: {verified_count}개")
    print(f"   - 위치(위경도) 보유 도서관: {with_coords}개")


if __name__ == "__main__":
    main()
