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

def run_last_week_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📊 지난주 GA4 상세 리포트 (최근 7일)")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # Common dev traffic filter (Seongnam/Yongin Desktop)
    dev_filter = FilterExpression(
        not_expression=FilterExpression(
            or_group=FilterExpressionList(
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
        )
    )

    # 1. Daily Overview
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
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  일별 트래픽 개요 (Daily Traffic)")
    report_lines.append("-" * 70)
    total_users = 0
    total_views = 0
    for row in response.rows:
        date_str = row.dimension_values[0].value
        users = int(row.metric_values[0].value)
        sessions = row.metric_values[1].value
        views = int(row.metric_values[2].value)
        duration = float(row.metric_values[3].value)
        avg_time = duration / users if users > 0 else 0
        
        report_lines.append(f"   {date_str}: 사용자 {users}명 | 뷰 {views}회 | 평균 체류 {avg_time:.1f}초")
        total_users += users
        total_views += views
    report_lines.append(f"\n   합계: 총 사용자 {total_users} (중복 포함 합산) | 총 뷰 {total_views}\n")

    # 2. Top Pages
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"), Metric(name="averageSessionDuration")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=15,
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n2️⃣  인기 페이지 상세 (Top Pages)")
    report_lines.append("-" * 70)
    for row in response.rows:
        page = row.dimension_values[0].value
        title = row.dimension_values[1].value
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        avg_dur = float(row.metric_values[2].value)
        report_lines.append(f"   {views:4}회 | {users:3}명 | {avg_dur:5.1f}s | {page} ({title[:30]})")

    # 3. Acquisition Channels
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n3️⃣  유입 채널 (Acquisition)")
    report_lines.append("-" * 70)
    for row in response.rows:
        source_medium = row.dimension_values[0].value
        users = row.metric_values[0].value
        report_lines.append(f"   {source_medium:30}: {users}명")

    # 4. Top Events
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=10,
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n4️⃣  주요 이벤트 (Top Events)")
    report_lines.append("-" * 70)
    for row in response.rows:
        event = row.dimension_values[0].value
        count = row.metric_values[0].value
        report_lines.append(f"   {event:25}: {count}회")

    # 5. Funnel Analysis (Requested by Marketing Rules)
    # Funnel: Home (/) -> List (/books) -> Detail (view_book_detail) -> Buy (click_buy_kyobo)
    
    report_lines.append("\n\n5️⃣  핵심 퍼널 전환 분석 (Funnel Analysis)")
    report_lines.append("-" * 70)
    
    # Define Funnel Steps
    funnel_steps = [
        {"name": "1. 홈 진입 (Home)", "filter": FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(value="/")))},
        {"name": "2. 리스트 진입 (List)", "filter": FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.BEGINS_WITH, value="/books")))},
        {"name": "3. 상세 페이지 (Detail)", "filter": FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="view_book_detail")))},
        {"name": "4. 구매 클릭 (Buy)", "filter": FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="click_buy_kyobo")))}
    ]
    
    prev_users = 0
    for i, step in enumerate(funnel_steps):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[Metric(name="activeUsers")],
            dimension_filter=FilterExpression(
                and_group=FilterExpressionList(
                    expressions=[dev_filter, step["filter"]]
                )
            )
        )
        response = client.run_report(request=request)
        users = int(response.rows[0].metric_values[0].value) if response.rows else 0
        
        conversion = (users / prev_users * 100) if prev_users > 0 else 100
        if i == 0:
            report_lines.append(f"   {step['name']:20}: {users:4}명")
        else:
            report_lines.append(f"   {step['name']:20}: {users:4}명 (전이율: {conversion:.1f}%)")
        prev_users = users

    # 6. Retention Rate (returning / (new + returning))
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n6️⃣  리텐션 및 유저 타입 (Retention)")
    report_lines.append("-" * 70)
    new_users = 0
    returning_users = 0
    for row in response.rows:
        user_type = row.dimension_values[0].value
        count = int(row.metric_values[0].value)
        if user_type == "new": new_users = count
        if user_type == "returning": returning_users = count
        report_lines.append(f"   {user_type:15}: {count}명")
    
    total = new_users + returning_users
    retention_rate = (returning_users / total * 100) if total > 0 else 0
    report_lines.append(f"   계산된 리텐션율: {retention_rate:.1f}%")
    
    # Save to file
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_last_week_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n✅ 리포트가 완성되었습니다: {output_file}")

if __name__ == "__main__":
    run_last_week_analysis()
