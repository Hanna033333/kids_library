import os
import sys
from datetime import datetime, timedelta
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def run_detailed_report():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📊 상세 GA4 리포트 - {yesterday} (어제)")
    report_lines.append(f"{'='*70}\n")
    
    # 1. Overview Metrics
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration"),
            Metric(name="engagementRate"),
            Metric(name="bounceRate"),
        ]
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  트래픽 개요 (Traffic Overview)")
    report_lines.append("-" * 70)
    for row in response.rows:
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        views = row.metric_values[2].value
        duration = float(row.metric_values[3].value)
        engagement_rate = float(row.metric_values[4].value) * 100
        bounce_rate = float(row.metric_values[5].value) * 100
        avg_time = duration / int(users) if int(users) > 0 else 0
        
        report_lines.append(f"   활성 사용자 (Active Users): {users}명")
        report_lines.append(f"   총 세션 (Total Sessions): {sessions}회")
        report_lines.append(f"   페이지뷰 (Page Views): {views}회")
        report_lines.append(f"   평균 참여시간 (Avg Engagement): {avg_time:.1f}초")
        report_lines.append(f"   참여율 (Engagement Rate): {engagement_rate:.1f}%")
        report_lines.append(f"   이탈률 (Bounce Rate): {bounce_rate:.1f}%\n")
    
    # 2. Device Information
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="deviceCategory"),
            Dimension(name="operatingSystem"),
            Dimension(name="browser")
        ],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n2️⃣  디바이스 & 플랫폼 (Device & Platform)")
    report_lines.append("-" * 70)
    for row in response.rows:
        device = row.dimension_values[0].value
        os_name = row.dimension_values[1].value
        browser = row.dimension_values[2].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        report_lines.append(f"   {device} / {os_name} / {browser}: {users}명 ({sessions} 세션)")
    
    # 3. Geographic Location
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="country"),
            Dimension(name="city")
        ],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n3️⃣  지역 정보 (Geographic Location)")
    report_lines.append("-" * 70)
    for row in response.rows:
        country = row.dimension_values[0].value
        city = row.dimension_values[1].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        report_lines.append(f"   {country} / {city}: {users}명 ({sessions} 세션)")
    
    # 4. Acquisition Channels (Detailed)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="sessionCampaignName")
        ],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n4️⃣  유입 채널 상세 (Acquisition Details)")
    report_lines.append("-" * 70)
    for row in response.rows:
        source = row.dimension_values[0].value
        medium = row.dimension_values[1].value
        campaign = row.dimension_values[2].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        report_lines.append(f"   출처: {source} / 매체: {medium} / 캠페인: {campaign}")
        report_lines.append(f"      → {users}명 ({sessions} 세션)")
    
    # 5. Top Events
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        order_bys=[{"desc": True, "metric": {"metric_name": "eventCount"}}],
        limit=10
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n5️⃣  주요 이벤트 (Top Events)")
    report_lines.append("-" * 70)
    for row in response.rows:
        event = row.dimension_values[0].value
        count = row.metric_values[0].value
        report_lines.append(f"   {event}: {count}회")
    
    # 6. Top Pages (Detailed)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
            Metric(name="averageSessionDuration")
        ],
        order_bys=[{"desc": True, "metric": {"metric_name": "screenPageViews"}}],
        limit=10
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n6️⃣  인기 페이지 상세 (Top Pages Details)")
    report_lines.append("-" * 70)
    for row in response.rows:
        page = row.dimension_values[0].value
        title = row.dimension_values[1].value
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        avg_duration = float(row.metric_values[2].value)
        report_lines.append(f"   페이지: {page}")
        report_lines.append(f"   제목: {title}")
        report_lines.append(f"      → {views}회 조회, {users}명, 평균 체류: {avg_duration:.1f}초\n")
    
    # 7. Session Details (Hour by Hour)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[Dimension(name="hour")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": False, "dimension": {"dimension_name": "hour"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n\n7️⃣  시간대별 트래픽 (Traffic by Hour)")
    report_lines.append("-" * 70)
    for row in response.rows:
        hour = row.dimension_values[0].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        if int(users) > 0:  # Only show hours with traffic
            report_lines.append(f"   {hour}시: {users}명 ({sessions} 세션)")
    
    report_lines.append("\n" + "="*70)
    
    # Save to file
    report_text = "\n".join(report_lines)
    with open("ga_detailed_report_yesterday.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    # Print to console
    print(report_text)
    print(f"\n✅ 상세 리포트가 'ga_detailed_report_yesterday.txt' 파일에 저장되었습니다.")

if __name__ == "__main__":
    run_detailed_report()
