import os
import sys
from datetime import datetime, timedelta

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/1004823/Desktop/kids_library/ga4-key.json"

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def run_report():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    # Yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_lines = []
    report_lines.append(f"\n{'='*60}")
    report_lines.append(f"GA4 REPORT - {yesterday} (어제)")
    report_lines.append(f"{'='*60}\n")
    
    # 1. Overview Metrics
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration"),
        ]
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  트래픽 개요 (Traffic Overview)")
    report_lines.append("-" * 60)
    for row in response.rows:
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        views = row.metric_values[2].value
        duration = float(row.metric_values[3].value)
        avg_time = duration / int(users) if int(users) > 0 else 0
        
        report_lines.append(f"   활성 사용자 (Active Users): {users}")
        report_lines.append(f"   총 세션 (Total Sessions): {sessions}")
        report_lines.append(f"   페이지뷰 (Page Views): {views}")
        report_lines.append(f"   평균 참여시간 (Avg Engagement): {avg_time:.1f}초\n")
    
    # 2. Acquisition Channels
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n2️⃣  유입 채널 (Acquisition Channels)")
    report_lines.append("-" * 60)
    for row in response.rows:
        source = row.dimension_values[0].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        report_lines.append(f"   {source}: {users}명 ({sessions} 세션)")
    
    # 3. Top Pages
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        order_bys=[{"desc": True, "metric": {"metric_name": "screenPageViews"}}],
        limit=10
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n3️⃣  인기 페이지 (Top Pages)")
    report_lines.append("-" * 60)
    for row in response.rows:
        page = row.dimension_values[0].value
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        report_lines.append(f"   {page}: {views}회 조회 ({users}명)")
    
    report_lines.append("\n" + "="*60)
    
    # Save to file
    report_text = "\n".join(report_lines)
    with open("ga_report_yesterday.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    # Print to console
    print(report_text)
    print(f"\n✅ 리포트가 'ga_report_yesterday.txt' 파일에 저장되었습니다.")

if __name__ == "__main__":
    run_report()
