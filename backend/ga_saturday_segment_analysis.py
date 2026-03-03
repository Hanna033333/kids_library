import os
import sys
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

def run_saturday_segment_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    # Target date: Saturday, Feb 7, 2026
    target_date = "2026-02-07"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"🕵️ 토요일(2/7) 순수 진성 유저 세그먼트 분석")
    report_lines.append(f"{'='*70}\n")
    
    # ---------------------------------------------------------
    # 1. Filters Setup
    # ---------------------------------------------------------
    # Exclude internal traffic (Seongnam/Yongin Desktop)
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

    # Combined Refined Filter: Not Internal AND Not Gecko
    refined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                FilterExpression(not_expression=FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))))
            ]
        )
    )

    # ---------------------------------------------------------
    # 2. Saturday Acquisition & Device Analysis
    # ---------------------------------------------------------
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=target_date, end_date=target_date)],
        dimensions=[
            Dimension(name="sessionSourceMedium"),
            Dimension(name="deviceCategory"),
            Dimension(name="operatingSystem")
        ],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration")
        ],
        dimension_filter=refined_filter
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  토요일 유저 유입 채널 및 디바이스 상세")
    report_lines.append("-" * 70)
    
    if not response.rows:
        report_lines.append("   분석 조건에 맞는 순수 유저 데이터가 없습니다.")
    else:
        for row in response.rows:
            source = row.dimension_values[0].value
            device = row.dimension_values[1].value
            os_name = row.dimension_values[2].value
            users = row.metric_values[0].value
            views = row.metric_values[1].value
            avg_dur = float(row.metric_values[2].value)
            
            report_lines.append(f"   출처: {source:30}")
            report_lines.append(f"   환경: {device} / {os_name}")
            report_lines.append(f"   지표: {users}명 | {views}뷰 | 평균 체류 {avg_dur:.1f}s")
            report_lines.append("   " + "." * 60)

    # Save and Print
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_saturday_segment_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)

if __name__ == "__main__":
    run_saturday_segment_analysis()
