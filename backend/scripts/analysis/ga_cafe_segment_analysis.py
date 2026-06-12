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

def run_cafe_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"🔍 맘카페(Naver Cafe) 유입 트래픽 심층 분석")
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

    # 1. Engagement metrics by Source/Medium
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration")
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣ 채널별 인게이지먼트 (Engagement by Channel)")
    report_lines.append("-" * 70)
    for row in response.rows:
        source_medium = row.dimension_values[0].value
        users = int(row.metric_values[0].value)
        sessions = int(row.metric_values[1].value)
        views = int(row.metric_values[2].value)
        duration = float(row.metric_values[3].value)
        
        avg_time_per_user = duration / users if users > 0 else 0
        pages_per_session = views / sessions if sessions > 0 else 0
        
        report_lines.append(f"🔹 {source_medium}")
        report_lines.append(f"   - 사용자: {users}명 | 세션: {sessions}회")
        report_lines.append(f"   - 유저당 평균 체류시간: {avg_time_per_user:.1f}초")
        report_lines.append(f"   - 세션당 페이지뷰: {pages_per_session:.1f}장\n")
        
    # 2. Key Events by Source/Medium
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium"), Dimension(name="eventName")],
        metrics=[Metric(name="activeUsers"), Metric(name="eventCount")],
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="sessionSourceMedium")),
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)
        ],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("2️⃣ 채널별 핵심 행동 (Core Events by Channel)")
    report_lines.append("-" * 70)
    
    current_source = None
    for row in response.rows:
        source_medium = row.dimension_values[0].value
        event_name = row.dimension_values[1].value
        users = int(row.metric_values[0].value)
        count = int(row.metric_values[1].value)
        
        # Only show specific events
        if event_name not in ["page_view", "view_book_detail", "click_buy_kyobo", "scroll", "user_engagement"]:
            continue
            
        if source_medium != current_source:
            if current_source is not None:
                report_lines.append("")
            report_lines.append(f"🔹 {source_medium}")
            current_source = source_medium
            
        report_lines.append(f"   - {event_name:20}: {count}회 (실행 유저 {users}명)")
        
    report_lines.append("\n" + "=" * 70)
    
    report_text = "\n".join(report_lines)
    print(report_text)
    
    with open(os.path.join(script_dir, "ga_cafe_analysis_report.txt"), "w", encoding="utf-8") as f:
        f.write(report_text)

if __name__ == "__main__":
    run_cafe_analysis()
