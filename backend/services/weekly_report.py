"""
책자리 주간 성과 리포트 생성, 텔레그램 발송 및 Notion 주간 지표 트래커 자동 적재 서비스
- GA4: 마케팅 유입(신규/검색/SNS·블로그) vs 제품 전환·깊이(NSM/재방문/1인당 PV/상세진입률/전환)
- Supabase: 신규 가입, 신규 찜, 신규 부모 리뷰, 누적 회원, 해당 주 Threads 발행 이력
- Notion 칸반보드: 🚧 진행 / 🔍 QA + ✅ 완료(최근 14일 이내 배포 건)
- Notion 주간 지표 트래커: 매주 월요일 1행 자동 적재 (중복 주차 방지)
"""

import os
import csv
import json
import html
import datetime
import urllib.parse
from collections import Counter
from typing import Dict, Any, List, Optional, Tuple

import httpx
from supabase import create_client
from services.telegram_notifier import send_telegram_message

GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "518474196")
NOTION_VERSION = "2022-06-28"
NOTION_PAGE_URL = os.getenv(
    "NOTION_PROJECT_PAGE_URL",
    "https://www.notion.so/424939f003ba807da0c2f0a1db2149f9",
)

KST = datetime.timezone(datetime.timedelta(hours=9))


def _get_week_ranges(reference_date: Optional[datetime.date] = None) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """기준일(기본: 오늘 KST) 기준 '직전 주(월~일)'와 '전전 주(월~일)' 날짜 범위를 반환합니다."""
    today = reference_date or datetime.datetime.now(KST).date()
    this_monday = today - datetime.timedelta(days=today.weekday())
    last_monday = this_monday - datetime.timedelta(days=7)
    last_sunday = last_monday + datetime.timedelta(days=6)
    prev_monday = last_monday - datetime.timedelta(days=7)
    prev_sunday = prev_monday + datetime.timedelta(days=6)
    return (
        (last_monday.isoformat(), last_sunday.isoformat()),
        (prev_monday.isoformat(), prev_sunday.isoformat()),
    )


def _pct_change(curr: float, prev: float) -> str:
    if prev == 0:
        return "NEW" if curr > 0 else "0%"
    diff = ((curr - prev) / prev) * 100
    sign = "+" if diff > 0 else ""
    return f"{sign}{diff:.0f}%"


def _build_ga4_client():
    """GA4 클라이언트를 초기화합니다. 환경변수 JSON 또는 키 파일을 순서대로 탐색합니다."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.oauth2 import service_account

    creds_json = os.getenv("GA4_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(info)
        return BetaAnalyticsDataClient(credentials=creds)

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_root = os.path.dirname(backend_dir)
    candidate_paths = [
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        os.path.join(backend_dir, "ga4-key.json"),
        os.path.join(repo_root, "ga_service_account.json"),
    ]
    for path in candidate_paths:
        if path and os.path.isfile(path):
            creds = service_account.Credentials.from_service_account_file(path)
            return BetaAnalyticsDataClient(credentials=creds)

    raise FileNotFoundError("GA4 서비스 계정 키 파일(ga4-key.json / ga_service_account.json)을 찾을 수 없습니다.")


def _classify_channels(channel_rows: List[Dict[str, str]]) -> Tuple[int, int]:
    """sessionSourceMedium 목록을 검색 유입(네이버·구글 등) vs SNS·블로그 유입으로 분류 집계합니다."""
    search_users = 0
    social_blog_users = 0

    for r in channel_rows:
        src = (r.get("sessionSourceMedium") or "").lower()
        users = int(r.get("activeUsers", 0))
        if any(k in src for k in ("blog.naver", "m.blog.naver", "threads", "instagram", "kakao", "t.co", "facebook", "cafe.naver")):
            social_blog_users += users
        elif any(k in src for k in ("organic", "search.naver", "search.daum", "google", "bing", "yahoo")):
            search_users += users

    return search_users, social_blog_users


def fetch_ga4_weekly_metrics(
    curr_range: Tuple[str, str],
    prev_range: Tuple[str, str],
) -> Dict[str, Any]:
    """GA4 API에서 직전 주 vs 전전 주 핵심 지표(마케팅 유입 vs 제품 전환·깊이)를 조회합니다."""
    try:
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest, OrderBy, FilterExpression, Filter
        )

        client = _build_ga4_client()

        def run_query(start_date, end_date, dimensions, metrics, dim_filter=None, order_bys=None, limit=50):
            req = RunReportRequest(
                property=f"properties/{GA4_PROPERTY_ID}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimension_filter=dim_filter,
                order_bys=order_bys,
                limit=limit,
            )
            res = client.run_report(req)
            return [
                {
                    **{d: row.dimension_values[i].value for i, d in enumerate(dimensions)},
                    **{m: row.metric_values[i].value for i, m in enumerate(metrics)},
                }
                for row in res.rows
            ]

        book_filter = FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
                    value="/book/",
                ),
            )
        )

        def collect_period(start_date: str, end_date: str) -> Dict[str, Any]:
            summary_rows = run_query(start_date, end_date, [], ["activeUsers", "newUsers", "sessions", "screenPageViews"])
            summary = summary_rows[0] if summary_rows else {}

            active_users = int(summary.get("activeUsers", 0))
            new_users = int(summary.get("newUsers", 0))
            returning_users = max(active_users - new_users, 0)
            sessions = int(summary.get("sessions", 0))
            page_views = int(summary.get("screenPageViews", 0))

            book_total_rows = run_query(start_date, end_date, [], ["activeUsers", "screenPageViews"], dim_filter=book_filter)
            book_daily_rows = run_query(start_date, end_date, ["date"], ["activeUsers"], dim_filter=book_filter)
            book_users = int(book_total_rows[0]["activeUsers"]) if book_total_rows else 0
            book_dau_avg = round(sum(int(r["activeUsers"]) for r in book_daily_rows) / 7.0, 1)

            pv_per_user = round(page_views / active_users, 1) if active_users > 0 else 0.0
            detail_entry_rate = round((book_users / active_users) * 100.0, 1) if active_users > 0 else 0.0

            ev_rows = run_query(start_date, end_date, ["eventName"], ["eventCount"], limit=100)
            events = {r["eventName"]: int(r["eventCount"]) for r in ev_rows}

            ch_rows = run_query(
                start_date,
                end_date,
                ["sessionSourceMedium"],
                ["activeUsers"],
                order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
                limit=50,
            )
            search_users, social_blog_users = _classify_channels(ch_rows)

            return {
                "active_users": active_users,
                "new_users": new_users,
                "returning_users": returning_users,
                "search_users": search_users,
                "social_blog_users": social_blog_users,
                "sessions": sessions,
                "page_views": page_views,
                "pv_per_user": pv_per_user,
                "nsm_book_users": book_users,
                "nsm_book_dau_avg": book_dau_avg,
                "detail_entry_rate": detail_entry_rate,
                "kyobo_clicks": events.get("click_buy_kyobo", 0),
                "loan_checks": events.get("click_loan_check", 0) + events.get("check_loan_status", 0),
                "wishlist_toggles": events.get("toggle_save_book", 0),
                "sign_up_events": events.get("sign_up", 0),
                "channels": [{"source": r["sessionSourceMedium"], "users": int(r["activeUsers"])} for r in ch_rows[:5]],
            }

        curr = collect_period(*curr_range)
        prev = collect_period(*prev_range)

        # 유저 실검색어 Top 5 (q= 쿼리파라미터 파싱)
        search_rows = run_query(
            *curr_range,
            ["pagePathPlusQueryString"],
            ["eventCount"],
            limit=200,
        )
        kw_counter = Counter()
        for r in search_rows:
            path = r.get("pagePathPlusQueryString", "")
            if "q=" in path:
                parsed = urllib.parse.urlparse(path)
                params = urllib.parse.parse_qs(parsed.query)
                if "q" in params and params["q"][0].strip():
                    kw = urllib.parse.unquote(params["q"][0].strip())
                    kw_counter[kw] += int(r["eventCount"])

        top_keywords = [{"keyword": k, "count": v} for k, v in kw_counter.most_common(5)]

        return {
            "ok": True,
            "current": curr,
            "previous": prev,
            "channels": curr["channels"],
            "top_keywords": top_keywords,
        }
    except Exception as e:
        print(f"⚠️ [Weekly Report] GA4 조회 실패: {e}")
        return {"ok": False, "error": str(e)}


def fetch_supabase_weekly_metrics(curr_range: Tuple[str, str]) -> Dict[str, Any]:
    """Supabase에서 직전 주 신규 가입, 찜, 부모 리뷰, 누적 회원, Threads 발행 내역을 조회합니다."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        if not url or not key:
            return {"ok": False, "error": "Supabase credentials missing"}

        sb = create_client(url, key)
        start_iso = f"{curr_range[0]}T00:00:00+09:00"
        end_iso = f"{curr_range[1]}T23:59:59+09:00"

        new_members = sb.table("members").select("id", count="exact").gte("created_at", start_iso).lte("created_at", end_iso).execute()
        total_members = sb.table("members").select("id", count="exact").execute()
        new_wishlists = sb.table("wishlists").select("id", count="exact").gte("created_at", start_iso).lte("created_at", end_iso).execute()
        new_reviews = (
            sb.table("book_reviews")
            .select("id", count="exact")
            .gte("created_at", start_iso)
            .lte("created_at", end_iso)
            .neq("is_ai_generated", True)
            .execute()
        )

        published_threads = []
        try:
            tf = (
                sb.table("threads_feeds")
                .select("curation_tag,title,published_at")
                .gte("published_at", start_iso)
                .lte("published_at", end_iso)
                .execute()
            )
            for row in tf.data or []:
                tag = row.get("curation_tag") or row.get("title") or ""
                if tag:
                    published_threads.append(tag)
        except Exception:
            pass

        return {
            "ok": True,
            "new_signups": new_members.count or 0,
            "total_members": total_members.count or 0,
            "new_wishlists": new_wishlists.count or 0,
            "new_reviews": new_reviews.count or 0,
            "published_threads": published_threads,
        }
    except Exception as e:
        print(f"⚠️ [Weekly Report] Supabase 조회 실패: {e}")
        return {"ok": False, "error": str(e)}


async def fetch_notion_active_cards(reference_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """Notion 5단계 칸반보드에서 '🚧 진행', '🔍 QA' 및 최근 14일 이내 '✅ 완료(배포)' 카드를 조회합니다."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_KANBAN_DB_ID")
    if not api_key or not db_id:
        return {"ok": False, "error": "NOTION_API_KEY 또는 NOTION_KANBAN_DB_ID 미설정"}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }
        payload = {
            "filter": {
                "or": [
                    {"property": "상태", "select": {"equals": "🐛 버그"}},
                    {"property": "상태", "select": {"equals": "🚧 진행"}},
                    {"property": "상태", "select": {"equals": "🔍 QA"}},
                    {"property": "상태", "select": {"equals": "✅ 완료"}},
                ]
            }
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=headers,
                json=payload,
                timeout=15.0,
            )
            if res.status_code != 200:
                return {"ok": False, "error": f"HTTP {res.status_code}"}
            data = res.json()

        def _txt(prop):
            if not prop:
                return ""
            t = prop.get("type")
            if t == "title":
                return "".join(x.get("plain_text", "") for x in prop.get("title", [])).strip()
            if t == "rich_text":
                return "".join(x.get("plain_text", "") for x in prop.get("rich_text", [])).strip()
            if t == "select":
                return (prop.get("select") or {}).get("name", "")
            if t == "date":
                return (prop.get("date") or {}).get("start", "")
            return ""

        today = reference_date or datetime.datetime.now(KST).date()
        in_progress = []
        recent_deployed = []

        for page in data.get("results", []):
            p = page.get("properties", {})
            item = {
                "title": _txt(p.get("제목")),
                "status": _txt(p.get("상태")),
                "area": _txt(p.get("영역")),
                "kpi": _txt(p.get("타겟 KPI")),
                "deployed_at": _txt(p.get("배포일")),
            }
            if item["status"] in ("🐛 버그", "🚧 진행", "🔍 QA"):
                in_progress.append(item)
            elif item["status"] == "✅ 완료" and item["deployed_at"]:
                try:
                    dep_dt = datetime.date.fromisoformat(item["deployed_at"][:10])
                    days = (today - dep_dt).days
                    if 0 <= days <= 14:
                        item["days_since_deploy"] = days
                        recent_deployed.append(item)
                except ValueError:
                    pass

        recent_deployed.sort(key=lambda x: x.get("days_since_deploy", 99))
        return {"ok": True, "in_progress": in_progress, "recent_deployed": recent_deployed}
    except Exception as e:
        print(f"⚠️ [Weekly Report] Notion 조회 실패: {e}")
        return {"ok": False, "error": str(e)}


async def save_weekly_metrics_to_notion(
    curr_range: Tuple[str, str],
    ga4: Dict[str, Any],
    sb: Dict[str, Any],
    notion: Dict[str, Any],
) -> Dict[str, Any]:
    """Notion '📣 마케팅 · 유입 주간 지표'와 '🛠️ 제품 · 전환 주간 지표' DB에 각각 1행씩 자동 적재합니다 (중복 주차 방지)."""
    api_key = os.getenv("NOTION_API_KEY")
    mkt_db_id = os.getenv("NOTION_MARKETING_DB_ID")
    prd_db_id = os.getenv("NOTION_PRODUCT_DB_ID")
    if not api_key or (not mkt_db_id and not prd_db_id):
        return {"ok": False, "skipped": True, "reason": "NOTION_MARKETING_DB_ID / NOTION_PRODUCT_DB_ID 미설정"}

    start_s, end_s = curr_range
    week_label = f"{start_s} ~ {end_s[5:]}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    c = ga4.get("current", {}) if ga4.get("ok") else {}
    kws = ", ".join(k["keyword"] for k in ga4.get("top_keywords", [])[:5]) if ga4.get("ok") else ""
    actions = c.get("kyobo_clicks", 0) + c.get("loan_checks", 0) + (sb.get("new_wishlists", 0) if sb.get("ok") else 0)
    recent_deploys = [d["title"] for d in notion.get("recent_deployed", [])[:3]] if notion.get("ok") else []
    deploy_str = " / ".join(recent_deploys) if recent_deploys else "-"
    threads_list = sb.get("published_threads", []) if sb.get("ok") else []
    marketing_str = f"Threads {len(threads_list)}건 ({', '.join(threads_list[:3])})" if threads_list else "-"

    async def _upsert_row(client: httpx.AsyncClient, db_id: str, props: Dict[str, Any]) -> str:
        check_res = await client.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json={"filter": {"property": "시작일", "date": {"equals": start_s}}},
            timeout=15.0,
        )
        if check_res.status_code == 200 and check_res.json().get("results"):
            return "skipped"
        create_res = await client.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json={"parent": {"database_id": db_id}, "properties": props},
            timeout=15.0,
        )
        if create_res.status_code != 200:
            return f"error({create_res.status_code})"
        return "created"

    try:
        results = {}
        async with httpx.AsyncClient() as client:
            if mkt_db_id:
                mkt_props = {
                    "주차": {"title": [{"text": {"content": week_label}}]},
                    "시작일": {"date": {"start": start_s}},
                    "WAU(전체)": {"number": c.get("active_users", 0)},
                    "신규 유입": {"number": c.get("new_users", 0)},
                    "검색 유입": {"number": c.get("search_users", 0)},
                    "SNS·블로그 유입": {"number": c.get("social_blog_users", 0)},
                    "인기 검색어": {"rich_text": [{"text": {"content": kws or "-"}}]},
                    "마케팅 발행": {"rich_text": [{"text": {"content": marketing_str[:1800]}}]},
                }
                results["marketing"] = await _upsert_row(client, mkt_db_id, mkt_props)

            if prd_db_id:
                prd_props = {
                    "주차": {"title": [{"text": {"content": week_label}}]},
                    "시작일": {"date": {"start": start_s}},
                    "NSM 상세방문": {"number": c.get("nsm_book_users", 0)},
                    "NSM 일평균": {"number": c.get("nsm_book_dau_avg", 0)},
                    "재방문자": {"number": c.get("returning_users", 0)},
                    "1인당 PV": {"number": c.get("pv_per_user", 0)},
                    "상세 진입률(%)": {"number": c.get("detail_entry_rate", 0)},
                    "행동 전환": {"number": actions},
                    "신규가입": {"number": sb.get("new_signups", 0) if sb.get("ok") else 0},
                    "부모리뷰": {"number": sb.get("new_reviews", 0) if sb.get("ok") else 0},
                    "제품 배포": {"rich_text": [{"text": {"content": deploy_str[:1800]}}]},
                }
                results["product"] = await _upsert_row(client, prd_db_id, prd_props)

        return {"ok": True, "week": week_label, "results": results}
    except Exception as e:
        print(f"⚠️ [Weekly Report] Notion 주간 지표 적재 실패: {e}")
        return {"ok": False, "error": str(e)}


def format_weekly_report_html(
    curr_range: Tuple[str, str],
    ga4: Dict[str, Any],
    sb: Dict[str, Any],
    notion: Dict[str, Any],
) -> str:
    """수집된 데이터를 마케팅(유입) vs 제품(전환·깊이) 2그룹으로 포맷팅합니다."""
    start_s, end_s = curr_range
    lines = [
        f"📊 <b>[책자리 주간 성과 리포트]</b>",
        f"🗓 기간: {start_s} ~ {end_s} (전주 대비)",
        "━━━━━━━━━━━━━━━━━━━",
    ]

    if ga4.get("ok"):
        c = ga4["current"]
        p = ga4["previous"]

        # 1. 마케팅/유입
        lines.append("📣 <b>마케팅 · 유입 (얼마나 데려왔나)</b>")
        lines.append(
            f"• <b>신규 유입</b>: {c['new_users']}명 ({_pct_change(c['new_users'], p['new_users'])}) | "
            f"WAU {c['active_users']}명 ({_pct_change(c['active_users'], p['active_users'])})"
        )
        lines.append(
            f"• <b>채널 분리</b>: 검색 {c['search_users']}명 · SNS/블로그 {c['social_blog_users']}명"
        )
        if ga4.get("top_keywords"):
            kw_str = ", ".join(f"'{html.escape(k['keyword'])}'({k['count']})" for k in ga4["top_keywords"][:5])
            lines.append(f"• <b>실검색어</b>: {kw_str}")
        lines.append("")

        # 2. 제품/전환·깊이
        lines.append("🛠️ <b>제품 · 전환/깊이 (얼마나 깊이 썼나)</b>")
        lines.append(
            f"• <b>[NSM] 도서 상세</b>: {c['nsm_book_users']}명 ({_pct_change(c['nsm_book_users'], p['nsm_book_users'])}) "
            f"/ 일평균 {c['nsm_book_dau_avg']}명"
        )
        lines.append(
            f"• <b>탐색 깊이</b>: 1인당 PV <b>{c['pv_per_user']}</b> ({_pct_change(c['pv_per_user'], p['pv_per_user'])}) · "
            f"상세 진입률 <b>{c['detail_entry_rate']}%</b>"
        )
        lines.append(
            f"• <b>재방문자</b>: {c['returning_users']}명 ({_pct_change(c['returning_users'], p['returning_users'])}) | "
            f"구매 {c['kyobo_clicks']} · 대출 {c['loan_checks']}"
        )
    else:
        lines.append(f"⚠️ <b>GA4 조회 생략</b>: {html.escape(ga4.get('error', '알 수 없음'))}")

    if sb.get("ok"):
        lines.append(
            f"• <b>실데이터</b>: 가입 <b>{sb['new_signups']}명</b>(누적 {sb['total_members']}) · "
            f"찜 <b>{sb['new_wishlists']}</b> · 리뷰 <b>{sb['new_reviews']}</b>"
        )
    else:
        lines.append(f"⚠️ <b>Supabase 조회 생략</b>: {html.escape(sb.get('error', '알 수 없음'))}")

    lines.append("")

    # 3. Notion 칸반 (최근 14일 배포 완료 건 + 진행/QA)
    if notion.get("ok"):
        recent = notion.get("recent_deployed", [])
        in_progress = notion.get("in_progress", [])

        if recent:
            lines.append("🚀 <b>최근 14일 배포 완료 (성과 체크)</b>")
            for item in recent[:4]:
                lines.append(f"• {html.escape(item['title'])} (D+{item['days_since_deploy']})")
            lines.append("")

        lines.append("🚧 <b>이번 주 버그 / 진행 / QA</b>")
        if in_progress:
            for item in in_progress[:5]:
                prefix = "[버그] " if item["status"] == "🐛 버그" else ("[QA] " if item["status"] == "🔍 QA" else "")
                lines.append(f"• {prefix}{html.escape(item['title'])}")
        else:
            lines.append("• 없음 (Notion 보드에서 이번 주 과제를 옮겨주세요!)")
    else:
        lines.append(f"📌 <b>Notion 보드</b>: 연동 대기 ({html.escape(notion.get('error', ''))})")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 주간 추이는 아래 Notion 대시보드 표에 자동 누적됩니다.")
    return "\n".join(lines)


def append_weekly_metrics_csv(
    curr_range: Tuple[str, str],
    ga4: Dict[str, Any],
    sb: Dict[str, Any],
    csv_path: Optional[str] = None,
) -> bool:
    """로컬 docs/metrics/weekly_metrics.csv에 주간 지표를 중복 없이 누적합니다."""
    if not csv_path:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(os.path.dirname(backend_dir), "docs", "metrics", "weekly_metrics.csv")

    if not os.path.exists(os.path.dirname(csv_path)):
        return False

    existing_starts = set()
    if os.path.isfile(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing_starts.add(row.get("week_start"))

    if curr_range[0] in existing_starts:
        return False

    c = ga4.get("current", {}) if ga4.get("ok") else {}
    kws = "|".join(k["keyword"] for k in ga4.get("top_keywords", [])[:5]) if ga4.get("ok") else ""

    row_data = [
        curr_range[0],
        curr_range[1],
        c.get("nsm_book_users", ""),
        c.get("nsm_book_dau_avg", ""),
        c.get("active_users", ""),
        c.get("sessions", ""),
        c.get("page_views", ""),
        c.get("kyobo_clicks", ""),
        c.get("loan_checks", ""),
        sb.get("new_signups", "") if sb.get("ok") else "",
        sb.get("new_wishlists", "") if sb.get("ok") else "",
        sb.get("new_reviews", "") if sb.get("ok") else "",
        kws,
        "",
    ]
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row_data)
    return True


async def generate_weekly_report(reference_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """주간 리포트 데이터와 HTML 메시지를 생성합니다."""
    curr_range, prev_range = _get_week_ranges(reference_date)
    ga4 = fetch_ga4_weekly_metrics(curr_range, prev_range)
    sb = fetch_supabase_weekly_metrics(curr_range)
    notion = await fetch_notion_active_cards(reference_date)
    message_html = format_weekly_report_html(curr_range, ga4, sb, notion)
    return {
        "period": {"start": curr_range[0], "end": curr_range[1]},
        "ga4": ga4,
        "supabase": sb,
        "notion": notion,
        "message_html": message_html,
    }


async def send_weekly_report_to_telegram(reference_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """주간 리포트를 생성해 텔레그램으로 발송하고 Notion 주간 지표 트래커에도 자동 적재합니다."""
    report = await generate_weekly_report(reference_date)
    curr_range = (report["period"]["start"], report["period"]["end"])

    notion_saved = await save_weekly_metrics_to_notion(
        curr_range, report["ga4"], report["supabase"], report["notion"]
    )
    sent = await send_telegram_message(
        text=report["message_html"],
        button_text="📋 Notion 대시보드 열기",
        button_url=NOTION_PAGE_URL,
    )
    append_weekly_metrics_csv(curr_range, report["ga4"], report["supabase"])

    report["notion_metrics_saved"] = notion_saved
    report["telegram_sent"] = sent
    return report
