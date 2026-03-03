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

def run_daily_trend_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📅 일별 트래픽 추이 분석 (순수 유저 기준)")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # ---------------------------------------------------------
    # 1. Filters Setup
    # ---------------------------------------------------------
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

    refined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                FilterExpression(not_expression=FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))))
            ]
        )
    )

    # ---------------------------------------------------------
    # 2. Daily Analysis
    # ---------------------------------------------------------
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"), 
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration")
        ],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
        dimension_filter=refined_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  일별 활성 사용자 및 페이지 뷰 추이")
    report_lines.append("-" * 70)
    for row in response.rows:
        date_raw = row.dimension_values[0].value
        date_formatted = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
        users = row.metric_values[0].value
        views = row.metric_values[2].value
        avg_dur = float(row.metric_values[3].value)
        report_lines.append(f"   {date_formatted}: {users:3}명 | {views:3}뷰 | 평균 체류 {avg_dur:5.1f}s")

    # ---------------------------------------------------------
    # 3. Daily Top Source Analysis
    # ---------------------------------------------------------
    report_lines.append("\n\n2️⃣  날짜별 주요 유입 채널 및 리텐션 신호")
    report_lines.append("-" * 70)
    
    # We need to iterate by date or use multiple dimensions
    request_src = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="date"), Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers")],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date")), OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        dimension_filter=refined_filter
    )
    resp_src = client.run_report(request_src)
    
    current_date = ""
    for row in resp_src.rows:
        date_raw = row.dimension_values[0].value
        date_formatted = f"{date_raw[4:6]}/{date_raw[6:]}"
        source = row.dimension_values[1].value
        users = row.metric_values[0].value
        
        if date_raw != current_date:
            report_lines.append(f"\n   [{date_formatted}]")
            current_date = date_raw
        
        report_lines.append(f"      - {source:30}: {users}명")

    # Save and Print
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_daily_trend_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)

if __name__ == "__main__":
    run_daily_trend_analysis()
