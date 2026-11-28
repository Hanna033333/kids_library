"""전국 공공도서관 마스터 레지스트리 (메모리 캐싱 + 검색/거리 정렬)"""
import json
import math
from pathlib import Path
from typing import Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "libraries.json"

_LIBRARIES: List[Dict] = []
_BY_CODE: Dict[str, Dict] = {}
_BY_NAME: Dict[str, Dict] = {}
_LOADED = False


def _ensure_loaded() -> None:
    global _LIBRARIES, _BY_CODE, _BY_NAME, _LOADED
    if _LOADED:
        return

    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _LIBRARIES = json.load(f)
    else:
        _LIBRARIES = []

    _BY_CODE = {}
    _BY_NAME = {}
    for lib in _LIBRARIES:
        code = str(lib.get("code", "")).strip()
        name = str(lib.get("name", "")).strip()
        official = str(lib.get("official_name", "")).strip()
        if code:
            _BY_CODE[code] = lib
        if name:
            _BY_NAME[name] = lib
            _BY_NAME[name.lower()] = lib
        if official and official not in _BY_NAME:
            _BY_NAME[official] = lib
            _BY_NAME[official.lower()] = lib

    _LOADED = True


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def find_library(
    library_name: Optional[str] = None,
    lib_code: Optional[str] = None,
) -> Optional[Dict]:
    """lib_code 또는 library_name으로 전국 도서관 정보 조회"""
    _ensure_loaded()

    if lib_code:
        found = _BY_CODE.get(str(lib_code).strip())
        if found:
            return found

    if library_name:
        key = library_name.strip()
        found = _BY_NAME.get(key) or _BY_NAME.get(key.lower())
        if found:
            return found
        # 공백 제거 완전 일치 fallback
        normalized = key.replace(" ", "").lower()
        for lib in _LIBRARIES:
            if lib["name"].replace(" ", "").lower() == normalized:
                return lib
            if lib.get("official_name", "").replace(" ", "").lower() == normalized:
                return lib
        # 부분 일치 fallback
        for lib in _LIBRARIES:
            if normalized in lib["name"].replace(" ", "").lower():
                return lib

    return None


def get_verified_libraries() -> List[Dict]:
    """기존 DB 청구기호 검증이 완료된 대표 도서관 목록 반환"""
    _ensure_loaded()
    return [lib for lib in _LIBRARIES if lib.get("has_callno_db")]


def search_libraries(
    q: Optional[str] = None,
    region: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    limit: int = 30,
) -> Dict:
    """전국 공공도서관 검색 (이름/주소 키워드, 지역 필터, 위치 기반 가까운 순 정렬)"""
    _ensure_loaded()

    candidates = _LIBRARIES

    if region and region != "전체":
        candidates = [lib for lib in candidates if lib.get("region") == region]

    if q and q.strip():
        tokens = [t.lower() for t in q.strip().split() if t.strip()]
        filtered = []
        for lib in candidates:
            haystack = (
                f"{lib.get('name', '')} {lib.get('official_name', '')} "
                f"{lib.get('address', '')} {lib.get('region', '')}"
            ).lower()
            if all(tok in haystack for tok in tokens):
                filtered.append(lib)
        candidates = filtered

    results: List[Dict] = []
    if lat is not None and lng is not None:
        with_dist = []
        for lib in candidates:
            lib_lat = lib.get("lat")
            lib_lng = lib.get("lng")
            if lib_lat is not None and lib_lng is not None:
                dist = _haversine_km(lat, lng, lib_lat, lib_lng)
                item = {**lib, "distance_km": round(dist, 2)}
                with_dist.append((dist, item))
        with_dist.sort(key=lambda pair: pair[0])
        total = len(with_dist)
        results = [item for _, item in with_dist[:limit]]
    else:
        # 검색어 없을 때는 기존 검증 도서관을 상단에 우선 배치
        if not q or not q.strip():
            ordered = sorted(
                candidates,
                key=lambda x: (0 if x.get("has_callno_db") else 1, x.get("name", "")),
            )
        else:
            q_lower = q.strip().lower()
            ordered = sorted(
                candidates,
                key=lambda x: (
                    0 if q_lower in x.get("name", "").lower() else 1,
                    0 if x.get("has_callno_db") else 1,
                    x.get("name", ""),
                ),
            )
        total = len(ordered)
        results = ordered[:limit]

    return {
        "libraries": [
            {
                "code": lib["code"],
                "name": lib["name"],
                "address": lib.get("address", ""),
                "region": lib.get("region", ""),
                "homepage": lib.get("homepage", ""),
                "has_callno_db": bool(lib.get("has_callno_db", False)),
                **({"distance_km": lib["distance_km"]} if "distance_km" in lib else {}),
            }
            for lib in results
        ],
        "total": total,
    }

