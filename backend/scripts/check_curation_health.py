#!/usr/bin/env python3
"""
큐레이션 도서 수 일괄 검증 스크립트
- taxonomy.ts의 모든 태그
- weekly_schedule.json의 현재 주차 및 향후 4주 태그
실행: python3 backend/scripts/check_curation_health.py
"""
import urllib.request, urllib.parse, json, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ── 환경변수 로드 ────────────────────────────────────────────────────────────
def load_env():
    for candidate in [
        Path(__file__).resolve().parents[1] / ".env",
        Path(__file__).resolve().parents[2] / "backend" / ".env",
    ]:
        if candidate.exists():
            env = {}
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            return env
    raise FileNotFoundError("backend/.env 파일을 찾을 수 없습니다.")

env = load_env()
SUPABASE_URL = env.get('SUPABASE_URL', '')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_KEY', env.get('SUPABASE_KEY', ''))
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

MIN_HOME = 7   # 홈 화면 CurationSection 표시 기준 (weekly_schedule 태그에 적용)
MIN_PAGE = 1   # 도서 목록 페이지 표시 기준 (taxonomy 태그에 적용, 0권이면 SEO 빈 페이지)

# ── DB 태그 카운트 ────────────────────────────────────────────────────────────
# 홈 캐러셀(getBooksByTag/getCaldecottBooks/getResearchCouncilBooks)은 pangyo_callno를
# 전혀 필터링하지 않는다. 반면 목록/SEO 페이지(getBooksFromSupabase, 백엔드 search_books_service)는
# pangyo_callno IS NOT NULL을 강제한다. 두 화면의 실제 노출 권수가 다르므로 카운트 함수도
# raw(홈 기준) / callno-filtered(목록·SEO 기준)로 분리한다. 하나로 합치면 "홈 섹션 숨김" 같은
# 라벨이 실제 동작과 어긋나는 오경보/오판을 유발한다.

def _count(params: list) -> int:
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/childbook_items?{qs}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return len(json.loads(r.read()))
    except Exception as e:
        return -1  # 조회 실패

def count_books_by_tag_raw(tag: str) -> int:
    """getBooksByTag 동일 패턴 (이미지 있고 숨김 아니면 카운트, 청구기호 무관) — 홈 캐러셀 기준"""
    or_filter = f'curation_tag.eq."{tag}",curation_tag.like."{tag},%",curation_tag.eq."#{tag}",curation_tag.like."#{tag},%"'
    return _count([
        ("select", "id"),
        ("or", f"({or_filter})"),
        ("is_hidden", "not.eq.true"),
        ("image_url", "not.is.null"),
        ("limit", "100"),
    ])

def count_books_by_tag(tag: str) -> int:
    """getBooksFromSupabase / search_books_service 동일 패턴 (청구기호 있는 것만) — 목록/SEO 페이지 기준"""
    or_filter = f'curation_tag.eq."{tag}",curation_tag.like."{tag},%",curation_tag.eq."#{tag}",curation_tag.like."#{tag},%"'
    return _count([
        ("select", "id"),
        ("or", f"({or_filter})"),
        ("is_hidden", "not.eq.true"),
        ("image_url", "not.is.null"),
        ("pangyo_callno", "not.is.null"),
        ("pangyo_callno", "not.eq.없음"),
        ("limit", "100"),
    ])

def count_books_ilike_raw(tag: str) -> int:
    """getCaldecottBooks / getResearchCouncilBooks 패턴 (ilike, 청구기호 무관) — 홈 캐러셀 기준"""
    return _count([
        ("select", "id"),
        ("curation_tag", f"ilike.%{tag}%"),
        ("is_hidden", "not.eq.true"),
        ("image_url", "not.is.null"),
        ("limit", "100"),
    ])

def count_books_ilike(tag: str) -> int:
    """목록/SEO 페이지 기준 ilike 매칭 (청구기호 필수)"""
    return _count([
        ("select", "id"),
        ("curation_tag", f"ilike.%{tag}%"),
        ("is_hidden", "not.eq.true"),
        ("image_url", "not.is.null"),
        ("pangyo_callno", "not.is.null"),
        ("pangyo_callno", "not.eq.없음"),
        ("limit", "100"),
    ])

# ── taxonomy.ts 파싱 ──────────────────────────────────────────────────────────
def load_taxonomy_tags() -> list[dict]:
    """frontend/lib/constants/taxonomy.ts에서 tag/slug 파싱"""
    ts_file = Path(__file__).resolve().parents[2] / "frontend" / "lib" / "constants" / "taxonomy.ts"
    if not ts_file.exists():
        print(f"  ⚠️  taxonomy.ts 없음: {ts_file}")
        return []

    tags = []
    import re
    text = ts_file.read_text()
    # { id: N, ..., tag: "TAG", slug: "SLUG" } 패턴 파싱
    pattern = re.compile(r'\{[^}]*?tag:\s*["\']([^"\']+)["\'][^}]*?slug:\s*["\']([^"\']+)["\'][^}]*?\}', re.DOTALL)
    for m in pattern.finditer(text):
        tags.append({'tag': m.group(1), 'slug': m.group(2)})
    return tags

# ── weekly_schedule.json 파싱 ─────────────────────────────────────────────────
def load_weekly_schedule() -> list[dict]:
    for candidate in [
        Path(__file__).resolve().parents[2] / "frontend" / "shared" / "weekly_schedule.json",
        Path(__file__).resolve().parents[1] / "weekly_schedule.json",
    ]:
        if candidate.exists():
            return json.loads(candidate.read_text())
    return []

def get_upcoming_tags(schedule: list[dict], weeks: int = 6) -> list[dict]:
    """오늘 기준 KST 향후 N주 태그 수집"""
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).date()
    result = []
    seen = set()
    for item in schedule:
        start = datetime.strptime(item['start'], '%Y-%m-%d').date()
        end = datetime.strptime(item['end'], '%Y-%m-%d').date()
        if end < today:
            continue
        if start > today + timedelta(weeks=weeks):
            continue
        for c in item.get('curations', []):
            tag = c.get('tag', '')
            if tag and tag not in seen:
                seen.add(tag)
                result.append({'tag': tag, 'period': f"{item['start']}~{item['end']}", 'title': c.get('title', '')})
    return result

# ── 특수 큐레이션 ─────────────────────────────────────────────────────────────
SPECIAL = [
    {'tag': 'caldecott',    'label': '칼데콧 수상작',        'mode': 'ilike'},
    {'tag': '어린이도서연구회', 'label': '어린이도서연구회',    'mode': 'ilike'},
    {'tag': '여름방학2026',  'label': '여름방학2026',         'mode': 'ilike'},
]

# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 62)
    print("📚 큐레이션 도서 수 건강 검진 (Curation Health Check)")
    print("=" * 62)

    all_ok = True
    errors = []

    # SPECIAL 태그는 ilike 모드로 Section 3에서 검사하므로 Section 1 제외
    special_tags = {s['tag'] for s in SPECIAL}

    # 1. taxonomy 전체 태그 (기준: 1권 이상 — 0권이면 SEO 유입 시 빈 페이지)
    print("\n[1] VALID_TAXONOMY 전체 태그  ← 기준: 1권 이상 (0권 = SEO 빈 페이지 위험)")
    taxonomy_tags = load_taxonomy_tags()
    if not taxonomy_tags:
        print("  ⚠️  taxonomy 파싱 실패 — 수동 확인 필요")
    for t in taxonomy_tags:
        if t['tag'] in special_tags:
            continue  # Section 3에서 ilike로 별도 검사
        cnt = count_books_by_tag(t['tag'])          # 목록/SEO 페이지 실제 노출 권수
        raw_cnt = count_books_by_tag_raw(t['tag'])   # 홈 캐러셀 태그 매칭 권수 (참고용)
        ok = cnt >= MIN_PAGE
        warn = 0 < raw_cnt < MIN_HOME  # 홈 로테이션 배정 시 자격 미달 여부 (참고용)
        if not ok:
            all_ok = False
            errors.append(f"taxonomy '{t['tag']}' ({t['slug']}): 0권 — SEO 빈 페이지!")
        icon = "✅" if ok else "❌"
        warn_str = f" ⚠️ ({raw_cnt}권, 홈 로테이션 배정 불가)" if warn else ""
        gap_str = f" (홈 캐러셀은 {raw_cnt}권 — 청구기호 미확보 {raw_cnt - cnt}권 목록/SEO 미노출)" if cnt < raw_cnt else ""
        bar = f"{cnt:>3}권"
        print(f"  {icon} {bar}  {t['tag']:<15} /collections/curation/{t['slug']}{warn_str}{gap_str}")

    # 2. 향후 6주 weekly_schedule 태그 (기준: 7권 이상 — 미달 시 홈 섹션 숨김)
    # 홈 캐러셀(getBooksByTag)은 pangyo_callno를 필터링하지 않으므로 raw 카운트로 판정한다.
    print("\n[2] weekly_schedule 향후 6주 태그  ← 기준: 7권 이상 (미달 = 홈 섹션 자동 숨김)")
    schedule = load_weekly_schedule()
    upcoming = get_upcoming_tags(schedule, weeks=6)
    if not upcoming:
        print("  ⚠️  weekly_schedule 파싱 실패 또는 향후 일정 없음")
    for t in upcoming:
        raw_cnt = count_books_by_tag_raw(t['tag'])
        page_cnt = count_books_by_tag(t['tag'])
        ok = raw_cnt >= MIN_HOME
        if not ok:
            all_ok = False
            errors.append(f"schedule '{t['tag']}' ({t['period']}): {raw_cnt}권 — 홈 섹션 숨김!")
        icon = "✅" if ok else "❌"
        gap_str = f" (목록/SEO 페이지는 {page_cnt}권만 노출 — 청구기호 미확보 {raw_cnt - page_cnt}권)" if page_cnt < raw_cnt else ""
        print(f"  {icon} {raw_cnt:>3}권  {t['tag']:<15} [{t['period']}] {t['title']}{gap_str}")

    # 3. 특수 고정 큐레이션 (기준: 7권 이상)
    # Section 2와 동일하게 홈 캐러셀(getCaldecottBooks/getResearchCouncilBooks) 기준 raw 카운트로 판정한다.
    print("\n[3] 고정 큐레이션  ← 기준: 7권 이상")
    for s in SPECIAL:
        if s['mode'] == 'ilike':
            raw_cnt = count_books_ilike_raw(s['tag'])
            page_cnt = count_books_ilike(s['tag'])
        else:
            raw_cnt = count_books_by_tag_raw(s['tag'])
            page_cnt = count_books_by_tag(s['tag'])
        cnt = raw_cnt
        ok = cnt >= MIN_HOME
        if not ok:
            all_ok = False
            errors.append(f"special '{s['tag']}': {cnt}권")
        icon = "✅" if ok else "❌"
        gap_str = f" (목록/SEO 페이지는 {page_cnt}권만 노출 — 청구기호 미확보 {raw_cnt - page_cnt}권)" if page_cnt < raw_cnt else ""
        print(f"  {icon} {cnt:>3}권  {s['label']}{gap_str}")

    # 최종 판정
    print("\n" + "=" * 62)
    if all_ok:
        print("🎉 전체 이상 없음 — 배포 진행 가능!")
    else:
        print("🚨 문제 항목 발견:")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)  # CI 연동 시 오류 코드 반환

if __name__ == "__main__":
    main()
