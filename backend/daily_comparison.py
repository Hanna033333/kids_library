
import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, 
    FilterExpression, Filter, FilterExpressionList, OrderBy
)

PROPERTY_ID = "518474196"  # Using the ID from analyze_weekend_traffic.py
KEY_PATH = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

if os.path.exists(KEY_PATH):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

def get_day_data(client, date_str, label, dev_filter):
    print(f"\n📊 Fetching data for {label} ({date_str})...")
    
    # 1. Overview
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"), 
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration")
        ],
        dimension_filter=dev_filter
    )
    response = client.run_report(request)
    
    metrics = {"users": 0, "sessions": 0, "views": 0, "avg_time": 0.0}
    if response.rows:
        row = response.rows[0]
        metrics["users"] = int(row.metric_values[0].value)
        metrics["sessions"] = int(row.metric_values[1].value)
        metrics["views"] = int(row.metric_values[2].value)
        duration = float(row.metric_values[3].value)
        metrics["avg_time"] = duration / metrics["users"] if metrics["users"] > 0 else 0
    
    # 2. Acquisition
    acq_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=dev_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        limit=5
    )
    acq_response = client.run_report(acq_request)
    channels = []
    for row in acq_response.rows:
        channels.append((row.dimension_values[0].value, int(row.metric_values[0].value)))
    
    return metrics, channels

def main():
    client = BetaAnalyticsDataClient()
    
    # Filter to exclude dev traffic (Seongnam/Yongin + Desktop)
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

    day1_label = "그제 (2/3)"
    day1_date = "2026-02-03"
    
    day2_label = "어제 (2/4)"
    day2_date = "2026-02-04"
    
    m1, c1 = get_day_data(client, day1_date, day1_label, dev_filter)
    m2, c2 = get_day_data(client, day2_date, day2_label, dev_filter)
    
    print("\n" + "="*40)
    print(f"📉 Traffic Comparison: {day1_label} vs {day2_label}")
    print("="*40)
    
    # Calculate Deltas
    user_delta = m2["users"] - m1["users"]
    user_pct = (user_delta / m1["users"] * 100) if m1["users"] > 0 else 0
    
    session_delta = m2["sessions"] - m1["sessions"]
    view_delta = m2["views"] - m1["views"]
    
    print(f"\n1. 핵심 지표 (Key Metrics)")
    print(f"- 활성 사용자 (Users): {m2['users']}명 (vs {m1['users']}, {user_delta:+d}, {user_pct:+.1f}%)")
    print(f"- 세션 (Sessions): {m2['sessions']} (vs {m1['sessions']}, {session_delta:+d})")
    print(f"- 페이지 뷰 (PV): {m2['views']} (vs {m1['views']}, {view_delta:+d})")
    print(f"- 평균 체류시간: {m2['avg_time']:.1f}초 (vs {m1['avg_time']:.1f}초)")
    
    print(f"\n2. 유입 경로 (Acquisition Channels) - {day2_label}")
    if not c2:
        print("  - 데이터 없음")
    else:
        for channel, users in c2:
            print(f"  - {channel}: {users}명")
            
    print(f"\n3. 유입 경로 (Acquisition Channels) - {day1_label}")
    if not c1:
        print("  - 데이터 없음")
    else:
        for channel, users in c1:
            print(f"  - {channel}: {users}명")

    # Top Pages for Yesterday
    print(f"\n4. 인기 페이지 (Top Pages) - {day2_label}")
    page_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=day2_date, end_date=day2_date)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        dimension_filter=dev_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5
    )
    page_response = client.run_report(page_request)
    for row in page_response.rows:
         print(f"  - [{row.metric_values[0].value} view] {row.dimension_values[1].value} ({row.dimension_values[0].value})")

if __name__ == "__main__":
    main()
