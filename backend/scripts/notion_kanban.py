"""
책자리 Notion 비공개 칸반보드 생성 및 docs/roadmap.md 동기화 스크립트

사용법:
  1. 최초 DB 생성 (지정된 비공개 페이지 하위에 칸반 데이터베이스 생성):
     ./backend/venv/bin/python backend/scripts/notion_kanban.py init --page-id <PAGE_ID>

  2. Notion -> docs/roadmap.md 동기화:
     ./backend/venv/bin/python backend/scripts/notion_kanban.py sync

  3. 카드 추가:
     ./backend/venv/bin/python backend/scripts/notion_kanban.py add \
       --title "카카오톡 공유 OG 카드 고도화" \
       --status "Next" --area "마케팅/SEO" --priority "P1 (높음)" \
       --hypothesis "큐레이션 공유 미리보기 개선으로 공유율 상승" \
       --kpi "큐레이션 공유율 2% 이상"

  4. 카드 상태/배포일 업데이트:
     ./backend/venv/bin/python backend/scripts/notion_kanban.py update \
       --title "카카오톡 공유" --status "배포/검증중" --deployed-at "2026-11-26"
"""

import os
import sys
import argparse
import datetime
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_KANBAN_DB_ID = os.getenv("NOTION_KANBAN_DB_ID")
NOTION_VERSION = "2022-06-28"
ROADMAP_MD_PATH = os.path.join(REPO_ROOT, "docs", "roadmap.md")

STATUS_ORDER = ["🐛 버그", "🚧 진행", "🔍 QA", "📝 기획", "💡 아이디어", "✅ 완료", "⏸️ 보류"]


def _headers():
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY가 backend/.env에 설정되어 있지 않습니다.")
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def format_uuid(raw_id: str) -> str:
    clean = raw_id.replace("-", "").strip()
    if len(clean) == 32:
        return f"{clean[:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:]}"
    return raw_id.strip()


def create_kanban_database(parent_page_id: str) -> str:
    """지정된 비공개 Notion 페이지 하위에 책자리 프로젝트 칸반 DB를 생성합니다."""
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": format_uuid(parent_page_id)},
        "title": [{"type": "text", "text": {"content": "책자리 디벨롭 & 실험 보드"}}],
        "is_inline": True,
        "properties": {
            "제목": {"title": {}},
            "상태": {
                "select": {
                    "options": [
                        {"name": "🐛 버그", "color": "red"},
                        {"name": "💡 아이디어", "color": "gray"},
                        {"name": "📝 기획", "color": "blue"},
                        {"name": "🚧 진행", "color": "yellow"},
                        {"name": "🔍 QA", "color": "orange"},
                        {"name": "✅ 완료", "color": "green"},
                        {"name": "⏸️ 보류", "color": "brown"},
                    ]
                }
            },
            "영역": {
                "select": {
                    "options": [
                        {"name": "제품", "color": "blue"},
                        {"name": "마케팅/SEO", "color": "orange"},
                        {"name": "데이터/인프라", "color": "green"},
                        {"name": "QA/운영", "color": "pink"},
                    ]
                }
            },
            "우선순위": {
                "select": {
                    "options": [
                        {"name": "P0 (긴급)", "color": "red"},
                        {"name": "P1 (높음)", "color": "orange"},
                        {"name": "P2 (보통)", "color": "gray"},
                    ]
                }
            },
            "가설": {"rich_text": {}},
            "타겟 KPI": {"rich_text": {}},
            "배포일": {"date": {}},
            "결과판정": {
                "select": {
                    "options": [
                        {"name": "대기", "color": "gray"},
                        {"name": "성공", "color": "green"},
                        {"name": "부분성공", "color": "yellow"},
                        {"name": "실패/롤백", "color": "red"},
                    ]
                }
            },
            "결과메모": {"rich_text": {}},
        },
    }

    res = requests.post(url, headers=_headers(), json=payload, timeout=15)
    if res.status_code != 200:
        raise RuntimeError(f"Notion DB 생성 실패 ({res.status_code}): {res.text}")

    db_id = res.json()["id"]
    print(f"✅ Notion 칸반 DB 생성 완료! DB ID: {db_id}")
    return db_id


def add_kanban_card(
    db_id: str,
    title: str,
    status: str = "💡 아이디어",
    area: str = "제품",
    priority: str = "P1 (높음)",
    hypothesis: str = "",
    kpi: str = "",
    deployed_at: str = "",
    verdict: str = "대기",
    result_note: str = "",
) -> dict:
    """칸반 DB에 새 카드를 추가합니다."""
    url = "https://api.notion.com/v1/pages"
    props = {
        "제목": {"title": [{"text": {"content": title}}]},
        "상태": {"select": {"name": status}},
        "영역": {"select": {"name": area}},
        "우선순위": {"select": {"name": priority}},
        "결과판정": {"select": {"name": verdict}},
    }
    if hypothesis:
        props["가설"] = {"rich_text": [{"text": {"content": hypothesis}}]}
    if kpi:
        props["타겟 KPI"] = {"rich_text": [{"text": {"content": kpi}}]}
    if deployed_at:
        props["배포일"] = {"date": {"start": deployed_at}}
    if result_note:
        props["결과메모"] = {"rich_text": [{"text": {"content": result_note}}]}

    res = requests.post(
        url,
        headers=_headers(),
        json={"parent": {"database_id": format_uuid(db_id)}, "properties": props},
        timeout=15,
    )
    if res.status_code != 200:
        raise RuntimeError(f"Notion 카드 추가 실패 ({res.status_code}): {res.text}")
    return res.json()


def _get_text(prop: dict) -> str:
    if not prop:
        return ""
    ptype = prop.get("type")
    if ptype == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", [])).strip()
    if ptype == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", [])).strip()
    if ptype == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    if ptype == "date":
        dt = prop.get("date")
        return dt.get("start", "") if dt else ""
    return ""


def fetch_kanban_cards(db_id: str) -> list:
    """칸반 DB의 전체 카드를 조회해 정제된 dict 리스트로 반환합니다."""
    url = f"https://api.notion.com/v1/databases/{format_uuid(db_id)}/query"
    cards = []
    has_more = True
    next_cursor = None

    while has_more:
        body = {"page_size": 100}
        if next_cursor:
            body["start_cursor"] = next_cursor
        res = requests.post(url, headers=_headers(), json=body, timeout=15)
        if res.status_code != 200:
            raise RuntimeError(f"Notion DB 조회 실패 ({res.status_code}): {res.text}")
        data = res.json()
        for page in data.get("results", []):
            p = page.get("properties", {})
            cards.append({
                "id": page["id"],
                "url": page.get("url", ""),
                "title": _get_text(p.get("제목")),
                "status": _get_text(p.get("상태")) or "💡 아이디어",
                "area": _get_text(p.get("영역")) or "-",
                "priority": _get_text(p.get("우선순위")) or "P2 (보통)",
                "hypothesis": _get_text(p.get("가설")),
                "kpi": _get_text(p.get("타겟 KPI")),
                "deployed_at": _get_text(p.get("배포일")),
                "verdict": _get_text(p.get("결과판정")) or "대기",
                "result_note": _get_text(p.get("결과메모")),
            })
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    priority_rank = {"P0 (긴급)": 0, "P1 (높음)": 1, "P2 (보통)": 2}
    cards.sort(key=lambda c: (priority_rank.get(c["priority"], 9), c["title"]))
    return cards


def update_kanban_card(
    db_id: str,
    title_keyword: str,
    status: str = None,
    deployed_at: str = None,
    verdict: str = None,
    result_note: str = None,
) -> dict:
    """제목 키워드로 카드를 찾아 상태/배포일/결과를 업데이트합니다."""
    cards = fetch_kanban_cards(db_id)
    matched = [c for c in cards if title_keyword.lower() in c["title"].lower()]
    if not matched:
        raise ValueError(f"'{title_keyword}'에 해당하는 카드를 찾을 수 없습니다.")

    target = matched[0]
    props = {}
    if status:
        props["상태"] = {"select": {"name": status}}
    if deployed_at:
        props["배포일"] = {"date": {"start": deployed_at}}
    if verdict:
        props["결과판정"] = {"select": {"name": verdict}}
    if result_note:
        props["결과메모"] = {"rich_text": [{"text": {"content": result_note}}]}

    url = f"https://api.notion.com/v1/pages/{target['id']}"
    res = requests.patch(url, headers=_headers(), json={"properties": props}, timeout=15)
    if res.status_code != 200:
        raise RuntimeError(f"Notion 카드 수정 실패 ({res.status_code}): {res.text}")
    print(f"✅ 카드 업데이트 완료: [{target['title']}] -> {props}")
    return res.json()


def sync_to_roadmap_md(db_id: str, output_path: str = ROADMAP_MD_PATH):
    """Notion 칸반 보드의 최신 상태를 docs/roadmap.md로 동기화합니다."""
    cards = fetch_kanban_cards(db_id)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    grouped = {s: [] for s in STATUS_ORDER}
    for c in cards:
        grouped.setdefault(c["status"], []).append(c)

    lines = [
        "# 책자리 디벨롭 로드맵 & 실험 보드",
        "",
        f"> **마지막 Notion 동기화**: `{now_str}`  ",
        "> **단일 원본(SSOT)**: 비공개 Notion 칸반보드 (`책자리 디벨롭 & 실험 보드`)  ",
        "> **동기화 명령**: `./backend/venv/bin/python backend/scripts/notion_kanban.py sync`",
        "",
        "---",
        "",
    ]

    section_meta = {
        "🐛 버그": ("🐛 버그 (긴급/이슈)", "수정이 필요한 버그 및 장애 이슈"),
        "🚧 진행": ("🚧 진행 (이번 주 집중)", "현재 개발 및 콘텐츠 작업 중인 과제"),
        "🔍 QA": ("🔍 QA (프리뷰 검수중)", "`dev` 프리뷰 배포 후 모바일/기능 검수 중인 과제"),
        "📝 기획": ("📝 기획 (스펙/가설 확정)", "가설·KPI·화면 스펙(`docs/pages/*.md`)을 정리 중인 과제"),
        "💡 아이디어": ("💡 아이디어 (후보)", "떠오른 기능·마케팅 후보 및 장기 과제"),
        "✅ 완료": ("✅ 완료 (검증 끝)", "배포 및 지표 결과 판정까지 완료된 과제"),
        "⏸️ 보류": ("⏸️ 보류", "우선순위 조정으로 잠시 보류된 과제"),
    }

    for status in STATUS_ORDER:
        items = grouped.get(status, [])
        heading, desc = section_meta.get(status, (status, ""))
        lines.append(f"## {heading} ({len(items)})")
        if desc:
            lines.append(f"_{desc}_")
        lines.append("")

        if not items:
            lines.append("- _(항목 없음)_")
            lines.append("")
            continue

        lines.append("| 우선순위 | 영역 | 과제명 | 가설 | 타겟 KPI | 배포일 | 판정 |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for c in items:
            hyp = c["hypothesis"].replace("|", "\\|").replace("\n", " ") or "-"
            kpi = c["kpi"].replace("|", "\\|").replace("\n", " ") or "-"
            dep = c["deployed_at"] or "-"
            verdict = c["verdict"] or "-"
            if c["result_note"]:
                verdict = f"{verdict} ({c['result_note'].replace('|', '/')})"
            lines.append(
                f"| {c['priority']} | {c['area']} | **{c['title']}** | {hyp} | {kpi} | {dep} | {verdict} |"
            )
        lines.append("")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ docs/roadmap.md 동기화 완료! (총 {len(cards)}개 카드)")


def seed_initial_cards(db_id: str):
    """project_plan.md 및 마케팅 전략 기반 초기 핵심 카드를 등록합니다."""
    initial_cards = [
        {
            "title": "프로젝트 관리 자동화 (Notion 칸반 + AWS 주간 텔레그램 리포트)",
            "status": "In Progress",
            "area": "데이터/인프라",
            "priority": "P0 (긴급)",
            "hypothesis": "가설-배포-지표 추적을 자동화해 데이터 기반 디벨롭 사이클 확립",
            "kpi": "매주 월요일 09시 주간 리포트 자동 수신 & 배포별 전후 비교 가능",
        },
        {
            "title": "주변 도서관 책 검색 SEO 타이틀/메타 최적화",
            "status": "Next",
            "area": "마케팅/SEO",
            "priority": "P1 (높음)",
            "hypothesis": "타이틀/설명에 '주변 도서관 대출 + 연령별 큐레이션' 명시 시 검색 클릭률 상승",
            "kpi": "네이버 서치어드바이저 CTR 5% -> 10% 이상",
        },
        {
            "title": "큐레이션/내 책장 카카오톡 공유 OG 카드 고도화",
            "status": "Next",
            "area": "제품",
            "priority": "P1 (높음)",
            "hypothesis": "공유 시 책 표지+큐레이션 타이틀 OG 카드가 노출되면 자발적 공유 유입 증가",
            "kpi": "큐레이션 공유율 2% 이상, 공유 링크 월 유입 10건+",
        },
        {
            "title": "전국 공공도서관 지원 확대 및 소장 데이터 자동 갱신",
            "status": "Backlog",
            "area": "데이터/인프라",
            "priority": "P2 (보통)",
            "hypothesis": "유저 요청 지역 도서관 추가 시 재방문율 및 내 책장 찜 전환 상승",
            "kpi": "선호 도서관 설정률 및 7일 재방문율 35% 이상",
        },
        {
            "title": "부모 리뷰·공감 뱃지 & 내지 미리보기 배포",
            "status": "배포/검증중",
            "area": "제품",
            "priority": "P1 (높음)",
            "hypothesis": "내지 미리보기와 부모 공감 뱃지가 책 선택 확신을 높여 전환율 개선",
            "kpi": "도서 상세 체류시간 및 구매/대출 클릭 전환율 3% 이상",
            "deployed_at": "2026-11-26",
            "verdict": "대기",
        },
    ]

    for card in initial_cards:
        add_kanban_card(db_id, **card)
        print(f"  + 카드 등록: [{card['status']}] {card['title']}")


def main():
    parser = argparse.ArgumentParser(description="책자리 Notion 칸반 관리 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="비공개 Notion 페이지에 칸반 DB 최초 생성")
    p_init.add_argument("--page-id", required=True, help="Notion 부모 페이지 ID")
    p_init.add_argument("--seed", action="store_true", help="초기 카드 자동 등록")

    sub.add_parser("sync", help="Notion 칸반 -> docs/roadmap.md 동기화")

    p_add = sub.add_parser("add", help="칸반에 새 카드 추가")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--status", default="💡 아이디어")
    p_add.add_argument("--area", default="제품")
    p_add.add_argument("--priority", default="P1 (높음)")
    p_add.add_argument("--hypothesis", default="")
    p_add.add_argument("--kpi", default="")
    p_add.add_argument("--deployed-at", default="")

    p_upd = sub.add_parser("update", help="기존 카드 상태/배포일/판정 수정")
    p_upd.add_argument("--title", required=True, help="제목 검색 키워드")
    p_upd.add_argument("--status")
    p_upd.add_argument("--deployed-at")
    p_upd.add_argument("--verdict")
    p_upd.add_argument("--result-note")

    args = parser.parse_args()

    if args.cmd == "init":
        db_id = create_kanban_database(args.page_id)
        if args.seed:
            seed_initial_cards(db_id)
        sync_to_roadmap_md(db_id)
        print(f"\n👉 backend/.env에 아래 줄을 추가하세요:\nNOTION_KANBAN_DB_ID={db_id}")
    else:
        if not NOTION_KANBAN_DB_ID:
            raise ValueError("NOTION_KANBAN_DB_ID가 backend/.env에 없습니다. 먼저 init을 실행하세요.")
        if args.cmd == "sync":
            sync_to_roadmap_md(NOTION_KANBAN_DB_ID)
        elif args.cmd == "add":
            add_kanban_card(
                NOTION_KANBAN_DB_ID,
                title=args.title,
                status=args.status,
                area=args.area,
                priority=args.priority,
                hypothesis=args.hypothesis,
                kpi=args.kpi,
                deployed_at=args.deployed_at,
            )
            sync_to_roadmap_md(NOTION_KANBAN_DB_ID)
        elif args.cmd == "update":
            update_kanban_card(
                NOTION_KANBAN_DB_ID,
                title_keyword=args.title,
                status=args.status,
                deployed_at=args.deployed_at,
                verdict=args.verdict,
                result_note=args.result_note,
            )
            sync_to_roadmap_md(NOTION_KANBAN_DB_ID)


if __name__ == "__main__":
    main()
