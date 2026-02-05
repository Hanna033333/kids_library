
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, FilterExpression, Filter
)
from datetime import datetime

PROPERTY_ID = "518474196"
KEY_PATH = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

if os.path.exists(KEY_PATH):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

def analyze_retention(client):
    print(f"\n📊 Analyzing Retention (User Stickiness)...")
    
    # 1. New vs Returning (Last 30 Days)
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"),
            Metric(name="userEngagementDuration")
        ]
    )
    response = client.run_report(request)
    
    print("\n1. 재방문 현황 (New vs Returning)")
    total_users = 0
    returning_users = 0
    
    for row in response.rows:
        user_type = row.dimension_values[0].value
        count = int(row.metric_values[0].value)
        duration = float(row.metric_values[2].value)
        avg_time = duration / count if count > 0 else 0
        
        total_users += count
        if user_type == "returning":
            returning_users = count
            
        print(f"   - {user_type}: {count} users (Avg Engagement: {avg_time:.1f}s)")

    retention_rate = (returning_users / total_users * 100) if total_users > 0 else 0
    print(f"👉 단순 재방문율 (Period): {retention_rate:.1f}%")

    # 2. Cohort Analysis (Simulated via Weekly Active Users)
    # Retention by definition requires Cohort API which is limited in Data API.
    # Instead, we check DAU / WAU / MAU stickiness.
    
    stickiness_req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        metrics=[
            Metric(name="active28DayUsers"),
            Metric(name="active7DayUsers"),
            Metric(name="active1DayUsers")
        ]
    )
    stickiness_resp = client.run_report(stickiness_req)
    
    if stickiness_resp.rows:
        mau = int(stickiness_resp.rows[0].metric_values[0].value)
        wau = int(stickiness_resp.rows[0].metric_values[1].value)
        dau = int(stickiness_resp.rows[0].metric_values[2].value) # This is average DAU over period? No, it's active users in range. Actually for single range it returns total.
        
        # To get DAU, we need a daily breakdown.
        # But stickiness ratio (DAU/MAU) is usually a snapshot.
        
        print(f"\n2. 사용자 고착도 (Stickiness)")
        print(f"   - MAU (30일 활성자): {mau}")
        print(f"   - WAU (7일 활성자): {wau}")
        # print(f"   - DAU (1일 활성자): {dau}") # Last day DAU
        
        if mau > 0:
            print(f"👉 WAU/MAU Ratio: {wau/mau*100:.1f}%")
            
def main():
    client = BetaAnalyticsDataClient()
    analyze_retention(client)

if __name__ == "__main__":
    main()
