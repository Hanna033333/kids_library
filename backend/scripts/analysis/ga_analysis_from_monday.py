import os
import sys
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    DateRange, 
    Dimension, 
    Metric, 
    OrderBy,
    FilterExpression,
    Filter,
    FilterExpressionList
)

# Set credentials to ga4-key.json
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

def run_monday_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    today = datetime.now()
    # Monday of this week
    monday = today - timedelta(days=today.weekday())
    start_date = monday.strftime("%Y-%m-%d")
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📊 이번주 월요일부터의 GA4 상세 분석 리포트")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date} (어제)")
    report_lines.append(f"{'='*70}\n")
    
    # ---------------------------------------------------------
    # 1. Filters Setup
    # ---------------------------------------------------------
    # 내부 개발 트래픽 제외 필터 (성남/용인 Desktop)
    base_dev_filter = FilterExpressionList(
        expressions=[
            FilterExpression(
                and_group=FilterExpressionList(
                    expressions=[
                        FilterExpression(filter=Filter(field_name="city", string_filter=Filter.StringFilter(value="Seongnam-si"))),
                        FilterExpression(filter=Filter(field_name="deviceCategory", string_filter=Filter.StringFilter(value="desktop")))
                    ]
                )
            ),
            FilterExpression(
                and_group=FilterExpressionList(
                    expressions=[
                        FilterExpression(filter=Filter(field_name="city", string_filter=Filter.StringFilter(value="Yongin-si"))),
                        FilterExpression(filter=Filter(field_name="deviceCategory", string_filter=Filter.StringFilter(value="desktop")))
                    ]
                )
            )
        ]
    )

    # 순수 유저 필터 (개발 트래픽 및 Gecko News 제외)
    refined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                FilterExpression(not_expression=FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))))
            ]
        )
    )

    # ---------------------------------------------------------
    # 2. Daily Overview (일별 트래픽 개요)
    # ---------------------------------------------------------
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration")
        ],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
        dimension_filter=refined_filter
    )
    
    try:
        response = client.run_report(request=request)
        report_lines.append("1️⃣  일별 트래픽 개요 (Daily Traffic)")
        report_lines.append("-" * 70)
        total_unique_users = 0 # 일별 합산이 아닌 전체 유니크는 뒤에서 구함
        total_views = 0
        total_sessions = 0
        
        for row in response.rows:
            date_raw = row.dimension_values[0].value
            date_formatted = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
            users = int(row.metric_values[0].value)
            sessions = int(row.metric_values[1].value)
            views = int(row.metric_values[2].value)
            duration = float(row.metric_values[3].value)
            avg_time = duration / users if users > 0 else 0
            
            report_lines.append(f"   {date_formatted}: 활성 사용자 {users:3}명 | 세션 {sessions:3}회 | 페이지뷰 {views:4}회 | 평균 체류 {avg_time:.1f}초")
            total_views += views
            total_sessions += sessions
            
    except Exception as e:
        report_lines.append(f"일별 트래픽 개요 조회 실패: {e}")

    # ---------------------------------------------------------
    # 3. Overall Unique Users (기간 내 순수 활성 사용자 수)
    # ---------------------------------------------------------
    request_total = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews")
        ],
        dimension_filter=refined_filter
    )
    try:
        response_total = client.run_report(request_total)
        if response_total.rows:
            row = response_total.rows[0]
            total_users = int(row.metric_values[0].value)
            total_sess = int(row.metric_values[1].value)
            total_pvs = int(row.metric_values[2].value)
            report_lines.append(f"\n   👉 기간 전체 요약: 순수 활성 사용자 {total_users}명 | 총 세션 {total_sess}회 | 총 페이지뷰 {total_pvs}회\n")
    except Exception as e:
        report_lines.append(f"기간 요약 조회 실패: {e}")

    # ---------------------------------------------------------
    # 4. NSM (도서 상세 페이지 DAU 및 트래픽)
    # ---------------------------------------------------------
    report_lines.append("2️⃣  북마크/도서 상세 성과 (NSM: 도서 상세 페이지 DAU)")
    report_lines.append("-" * 70)
    
    # NSM 필터: pagePath contains "/book/" (단, "/books" 제외)
    nsm_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                refined_filter,
                FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="/book/")))
            ]
        )
    )
    
    # NSM Daily Trend
    request_nsm_daily = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="activeUsers"), Metric(name="screenPageViews")],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
        dimension_filter=nsm_filter
    )
    try:
        res_nsm_daily = client.run_report(request_nsm_daily)
        report_lines.append("   [도서 상세 페이지 일별 추이]")
        for row in res_nsm_daily.rows:
            date_raw = row.dimension_values[0].value
            date_formatted = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
            users = row.metric_values[0].value
            views = row.metric_values[1].value
            report_lines.append(f"      {date_formatted}: 상세 페이지 DAU {users:3}명 | 페이지뷰 {views:3}회")
            
        # NSM Total Unique
        request_nsm_total = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[Metric(name="activeUsers"), Metric(name="screenPageViews"), Metric(name="userEngagementDuration")],
            dimension_filter=nsm_filter
        )
        res_nsm_total = client.run_report(request_nsm_total)
        if res_nsm_total.rows:
            row = res_nsm_total.rows[0]
            nsm_users = int(row.metric_values[0].value)
            nsm_views = int(row.metric_values[1].value)
            nsm_dur = float(row.metric_values[2].value)
            nsm_avg_dur = nsm_dur / nsm_users if nsm_users > 0 else 0
            report_lines.append(f"\n      도서 상세 전체: 순수 방문자 {nsm_users}명 | 총 상세 뷰 {nsm_views}회 | 평균 상세 체류 {nsm_avg_dur:.1f}초")
            
    except Exception as e:
        report_lines.append(f"NSM 상세 분석 실패: {e}")

    # ---------------------------------------------------------
    # 5. Top 10 Books (인기 도서 상세 페이지)
    # ---------------------------------------------------------
    request_top_books = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=10,
        dimension_filter=nsm_filter
    )
    try:
        res_top_books = client.run_report(request_top_books)
        report_lines.append("\n   [가장 많이 본 도서 상세 TOP 10]")
        for idx, row in enumerate(res_top_books.rows):
            page = row.dimension_values[0].value
            title = row.dimension_values[1].value
            views = row.metric_values[0].value
            users = row.metric_values[1].value
            # Clean up title
            clean_title = title.split(" | ")[0] if " | " in title else title
            report_lines.append(f"      {idx+1:2}. {views:4}뷰 | {users:3}명 | {page} ({clean_title[:25]})")
    except Exception as e:
        report_lines.append(f"인기 도서 조회 실패: {e}")

    # ---------------------------------------------------------
    # 6. Acquisition Channels (유입 채널)
    # ---------------------------------------------------------
    report_lines.append("\n\n3️⃣  유입 채널 성과 (Acquisition)")
    report_lines.append("-" * 70)
    request_acq = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="screenPageViews")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        dimension_filter=refined_filter
    )
    try:
        res_acq = client.run_report(request_acq)
        for row in res_acq.rows:
            source = row.dimension_values[0].value
            users = row.metric_values[0].value
            sess = row.metric_values[1].value
            pvs = row.metric_values[2].value
            report_lines.append(f"   {source:35}: 활성 사용자 {users:3}명 | 세션 {sess:3}회 | 페이지뷰 {pvs:4}회")
    except Exception as e:
        report_lines.append(f"유입 채널 조회 실패: {e}")

    # ---------------------------------------------------------
    # 7. Funnel Analysis (퍼널 전환 분석)
    # ---------------------------------------------------------
    report_lines.append("\n\n4️⃣  핵심 퍼널 전환 분석 (Funnel Analysis)")
    report_lines.append("-" * 70)
    
    funnel_steps = [
        {"name": "1. 홈 진입 (Home)", "filter": FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(value="/")))},
        {"name": "2. 리스트 진입 (List)", "filter": FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.BEGINS_WITH, value="/books")))},
        {"name": "3. 상세 페이지 (Detail)", "filter": FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="/book/")))},
        {"name": "4. 구매 클릭 (Buy)", "filter": FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="click_buy_kyobo")))}
    ]
    
    prev_users = 0
    for i, step in enumerate(funnel_steps):
        # We need to construct filter combining refined_filter and step filter
        step_filter = FilterExpression(
            and_group=FilterExpressionList(
                expressions=[refined_filter, step["filter"]]
            )
        )
        request_step = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[Metric(name="activeUsers")],
            dimension_filter=step_filter
        )
        try:
            res_step = client.run_report(request_step)
            users = int(res_step.rows[0].metric_values[0].value) if res_step.rows else 0
            
            conversion = (users / prev_users * 100) if prev_users > 0 else 100
            if i == 0:
                report_lines.append(f"   {step['name']:25}: {users:4}명")
            else:
                report_lines.append(f"   {step['name']:25}: {users:4}명 (전환율: {conversion:.1f}%)")
            prev_users = users
        except Exception as e:
            report_lines.append(f"   {step['name']:25}: 조회 실패 ({e})")

    # ---------------------------------------------------------
    # 8. Top Events (주요 행동 분석)
    # ---------------------------------------------------------
    report_lines.append("\n\n5️⃣  사용자 주요 행동 이벤트 (Top Events)")
    report_lines.append("-" * 70)
    request_events = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount"), Metric(name="activeUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=15,
        dimension_filter=refined_filter
    )
    try:
        res_events = client.run_report(request_events)
        for row in res_events.rows:
            evt_name = row.dimension_values[0].value
            count = row.metric_values[0].value
            users = row.metric_values[1].value
            report_lines.append(f"   {evt_name:30}: 발생 건수 {count:4}회 | 참여 사용자 {users:3}명")
    except Exception as e:
        report_lines.append(f"이벤트 조회 실패: {e}")

    # ---------------------------------------------------------
    # 9. Retention Analysis (리텐션 및 재방문)
    # ---------------------------------------------------------
    report_lines.append("\n\n6️⃣  리텐션 및 유저 타입 (Retention)")
    report_lines.append("-" * 70)
    
    # Total Retention
    request_ret = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=refined_filter
    )
    try:
        res_ret = client.run_report(request_ret)
        new_users = 0
        returning_users = 0
        for row in res_ret.rows:
            user_type = row.dimension_values[0].value
            count = int(row.metric_values[0].value)
            if user_type == "new": new_users = count
            if user_type == "returning": returning_users = count
            report_lines.append(f"   {user_type:15}: {count}명")
        
        total = new_users + returning_users
        retention_rate = (returning_users / total * 100) if total > 0 else 0
        report_lines.append(f"   종합 재방문율(리텐션율): {retention_rate:.1f}%")
        
        # Channel Retention Comparison
        report_lines.append("\n   [주요 채널별 리텐션 비교]")
        channels = [
            {"name": "Naver Cafe (Mobile/PC)", "filter": "cafe.naver.com"},
            {"name": "Naver Search", "filter": "naver / organic"},
            {"name": "Direct (직접 유입)", "filter": "(direct)"}
        ]
        
        for ch in channels:
            ch_filter = FilterExpression(
                and_group=FilterExpressionList(
                    expressions=[
                        refined_filter,
                        FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value=ch["filter"])))
                    ]
                )
            )
            request_ch_ret = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="newVsReturning")],
                metrics=[Metric(name="activeUsers")],
                dimension_filter=ch_filter
            )
            res_ch_ret = client.run_report(request_ch_ret)
            ch_new = 0
            ch_ret = 0
            for row in res_ch_ret.rows:
                utype = row.dimension_values[0].value
                cnt = int(row.metric_values[0].value)
                if utype == "new": ch_new = cnt
                if utype == "returning": ch_ret = cnt
            ch_total = ch_new + ch_ret
            ch_rate = (ch_ret / ch_total * 100) if ch_total > 0 else 0
            report_lines.append(f"      - {ch['name']:30}: 재방문율 {ch_rate:4.1f}% (신규 {ch_new} / 재방문 {ch_ret})")
            
    except Exception as e:
        report_lines.append(f"리텐션 분석 실패: {e}")

    # Save to file
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_monday_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(report_text)

if __name__ == "__main__":
    run_monday_analysis()
