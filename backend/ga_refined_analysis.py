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

# Set credentials
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

def run_refined_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"🧹 GA4 데이터 정제 및 정교화 리포트")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # ---------------------------------------------------------
    # 1. Filters Setup
    # ---------------------------------------------------------
    
    # Internal filter (Enhanced: Exclude internal traffic)
    # The user said "Saturday dawn was me", based on prev report it was Seoul or unspecified.
    # We already have Seongnam/Yongin Desktop.
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

    # Add specific internal filter for Saturday dawn if possible OR broader internal filter
    # For now, let's keep the user's advice the Saturdays was them.
    
    # Filter to exclude Gecko News
    exclude_gecko_filter = FilterExpression(
        not_expression=FilterExpression(
            filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))
        )
    )

    # ---------------------------------------------------------
    # 2. Main Traffic Analysis (Excluding Gecko & Internal)
    # ---------------------------------------------------------
    report_lines.append("1️⃣  순수 유저 트래픽 (Gecko News 및 내부 트래픽 제외)")
    report_lines.append("-" * 70)
    
    # Combined filter: Not (Internal OR Gecko)
    refined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(
                    not_expression=FilterExpression(
                        or_group=base_dev_filter
                    )
                ),
                exclude_gecko_filter
            ]
        )
    )

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="screenPageViews")],
        dimension_filter=refined_filter
    )
    response = client.run_report(request=request)
    for row in response.rows:
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        views = row.metric_values[2].value
        report_lines.append(f"   활성 사용자: {users}명 | 세션: {sessions}회 | 페이지뷰: {views}회")

    # ---------------------------------------------------------
    # 3. Naver Cafe + Direct Segment Analysis
    # ---------------------------------------------------------
    report_lines.append("\n\n2️⃣  Naver Cafe + Direct 통합 퍼널 분석 (주요 타겟)")
    report_lines.append("-" * 70)
    
    combined_segment_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(
                    not_expression=FilterExpression(or_group=base_dev_filter)
                ),
                FilterExpression(
                    or_group=FilterExpressionList(
                        expressions=[
                            FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(value="m.cafe.naver.com / referral"))),
                            FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(value="cafe.naver.com / referral"))),
                            FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(value="(direct) / (none)")))
                        ]
                    )
                )
            ]
        )
    )

    event_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=combined_segment_filter
    )
    evt_resp = client.run_report(event_request)
    events = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in evt_resp.rows}
    
    visits = events.get('session_start', 0)
    details = events.get('view_book_detail', 0)
    buys = events.get('click_buy_kyobo', 0)
    report_lines.append(f"   [Naver Cafe + Direct 통합]")
    report_lines.append(f"      - 방문: {visits:3}회")
    report_lines.append(f"      - 상세조회: {details:3}회 ({(details/visits*100 if visits>0 else 0):.1f}%)")
    report_lines.append(f"      - 구매클릭: {buys:3}회 ({(buys/visits*100 if visits>0 else 0):.1f}%)")

    # ---------------------------------------------------------
    # 4. Retention Rate Analysis
    # ---------------------------------------------------------
    report_lines.append("\n\n3️⃣  리텐션(Retention) 상세 분석")
    report_lines.append("-" * 70)
    
    # Total Retention
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter))
    )
    resp = client.run_report(request=request)
    users_data = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in resp.rows}
    new_users = users_data.get('new', 0)
    returning_users = users_data.get('returning', 0)
    total_users = new_users + returning_users
    retention_rate = (returning_users / total_users * 100) if total_users > 0 else 0
    report_lines.append(f"   전체 리텐션 비율: {retention_rate:.1f}% ({returning_users}/{total_users})")

    # Comparison: Naver Cafe vs Gecko News
    report_lines.append("\n   [채널별 리텐션 비교]")
    channels = [
        {"name": "Naver Cafe", "filter": "cafe.naver.com"},
        {"name": "Gecko News", "filter": "news.hada.io"}
    ]
    
    for ch in channels:
        ch_filter = FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                    FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value=ch["filter"])))
                ]
            )
        )
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="newVsReturning")],
            metrics=[Metric(name="activeUsers")],
            dimension_filter=ch_filter
        )
        res = client.run_report(request=request)
        ch_users = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in res.rows}
        ch_new = ch_users.get('new', 0)
        ch_ret = ch_users.get('returning', 0)
        ch_total = ch_new + ch_ret
        ch_rate = (ch_ret / ch_total * 100) if ch_total > 0 else 0
        report_lines.append(f"      - {ch['name']:10}: {ch_rate:4.1f}% ({ch_ret}/{ch_total})")

    # ---------------------------------------------------------
    # 5. Save and Finish
    # ---------------------------------------------------------
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_refined_analysis_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)

if __name__ == "__main__":
    run_refined_analysis()
