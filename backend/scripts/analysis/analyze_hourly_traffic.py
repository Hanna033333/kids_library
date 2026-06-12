"""
오늘 시간대별 트래픽 분석
"""
import sys
import os
sys.path.insert(0, '.')

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy
)
from google.oauth2 import service_account
from datetime import datetime

# GA4 Property ID
PROPERTY_ID = "518474196"

# Service Account 키 파일 (절대 경로)
KEY_FILE = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

print("=" * 60)
print("📊 오늘 시간대별 트래픽 분석")
print("=" * 60)
print(f"분석 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    # 인증
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    
    client = BetaAnalyticsDataClient(credentials=credentials)
    
    # 오늘 시간대별 리포트
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="today", end_date="today")],
        dimensions=[
            Dimension(name="hour"),
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="screenPageViews"),
            Metric(name="eventCount"),
        ],
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="hour"))
        ]
    )
    
    response = client.run_report(request)
    
    output_lines = []
    output_lines.append("🕐 시간대별 트래픽:")
    output_lines.append("")
    output_lines.append(f"{'시간':<10} {'활성사용자':<15} {'페이지뷰':<15} {'이벤트수':<15}")
    output_lines.append("-" * 60)
    
    spike_found = False
    for row in response.rows:
        hour = row.dimension_values[0].value
        users = row.metric_values[0].value
        pageviews = row.metric_values[1].value
        events = row.metric_values[2].value
        
        # 14시(오후 2시)와 15시(오후 3시) 강조
        marker = ""
        if hour in ["14", "15"]:
            marker = "🔴"
            spike_found = True
        
        line = f"{marker} {hour}시{'':<6} {users:<15} {pageviews:<15} {events:<15}"
        output_lines.append(line)
    
    output_lines.append("")
    output_lines.append("=" * 60)
    
    if spike_found:
        output_lines.append("💡 분석:")
        output_lines.append("   - 🔴 표시된 시간대(14~15시)의 트래픽 확인")
        output_lines.append("   - 다른 시간대와 비교하여 급증 여부 판단")
    else:
        output_lines.append("⚠️  오늘 14~15시 데이터가 아직 집계되지 않았을 수 있습니다.")
    
    output_lines.append("=" * 60)
    
    # 파일로 저장
    output_text = "\n".join(output_lines)
    with open("hourly_traffic_today.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
    
    # 콘솔 출력
    print(output_text)
    print("\n✅ 결과가 'hourly_traffic_today.txt' 파일에 저장되었습니다.")

    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
