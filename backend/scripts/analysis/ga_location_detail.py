import os
import sys
from datetime import datetime, timedelta
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

def get_detailed_location():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📍 상세 지역 분석 - {yesterday} (어제)")
    report_lines.append(f"{'='*70}\n")
    
    # 1. Detailed Location with Region
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="country"),
            Dimension(name="region"),
            Dimension(name="city"),
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration")
        ],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("1️⃣  상세 지역 정보 (Country > Region > City)")
    report_lines.append("-" * 70)
    for row in response.rows:
        country = row.dimension_values[0].value
        region = row.dimension_values[1].value
        city = row.dimension_values[2].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        views = row.metric_values[2].value
        duration = float(row.metric_values[3].value)
        avg_duration = duration / int(users) if int(users) > 0 else 0
        
        report_lines.append(f"   국가: {country}")
        report_lines.append(f"   지역(시/도): {region}")
        report_lines.append(f"   도시(구): {city}")
        report_lines.append(f"      → {users}명, {sessions} 세션, {views} 페이지뷰, 평균 {avg_duration:.1f}초\n")
    
    # 2. Check referrer information by location
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="city"),
            Dimension(name="pageReferrer"),
            Dimension(name="landingPage")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions")
        ],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n2️⃣  도시별 유입 경로 및 랜딩 페이지")
    report_lines.append("-" * 70)
    for row in response.rows:
        city = row.dimension_values[0].value
        referrer = row.dimension_values[1].value
        landing = row.dimension_values[2].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        
        report_lines.append(f"   도시: {city}")
        report_lines.append(f"   유입 경로: {referrer if referrer else '(직접 접속 또는 북마크)'}")
        report_lines.append(f"   첫 방문 페이지: {landing}")
        report_lines.append(f"      → {users}명, {sessions} 세션\n")
    
    # 3. Full source/medium/campaign by city
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="city"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="firstUserSource"),
            Dimension(name="firstUserMedium")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions")
        ],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n3️⃣  도시별 상세 유입 분석")
    report_lines.append("-" * 70)
    for row in response.rows:
        city = row.dimension_values[0].value
        session_source = row.dimension_values[1].value
        session_medium = row.dimension_values[2].value
        first_source = row.dimension_values[3].value
        first_medium = row.dimension_values[4].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        
        report_lines.append(f"   도시: {city}")
        report_lines.append(f"   현재 세션 출처: {session_source} / {session_medium}")
        report_lines.append(f"   최초 유입 출처: {first_source} / {first_medium}")
        report_lines.append(f"      → {users}명, {sessions} 세션\n")
    
    # 4. User type by city (new vs returning)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
        dimensions=[
            Dimension(name="city"),
            Dimension(name="newVsReturning")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions")
        ],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    report_lines.append("\n4️⃣  도시별 신규/재방문 사용자")
    report_lines.append("-" * 70)
    for row in response.rows:
        city = row.dimension_values[0].value
        user_type = row.dimension_values[1].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        
        user_type_kr = "신규 사용자" if user_type == "new" else "재방문 사용자"
        report_lines.append(f"   도시: {city}")
        report_lines.append(f"   유형: {user_type_kr}")
        report_lines.append(f"      → {users}명, {sessions} 세션\n")
    
    report_lines.append("="*70)
    
    # Save to file
    report_text = "\n".join(report_lines)
    with open("ga_location_detail.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    # Print to console
    print(report_text)
    print(f"\n✅ 상세 지역 리포트가 'ga_location_detail.txt' 파일에 저장되었습니다.")

if __name__ == "__main__":
    get_detailed_location()
