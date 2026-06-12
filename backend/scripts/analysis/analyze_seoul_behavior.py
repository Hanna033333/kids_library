
import sys
# Force UTF-8 encoding for Windows console/redirection
sys.stdout.reconfigure(encoding='utf-8')

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter,
    FilterExpressionList
)

def analyze_seoul_behavior(property_id):
    client = BetaAnalyticsDataClient()
    
    print("="*50)
    print(f"🕵️ SEOUL MOBILE BEHAVIOR ANALYSIS: {property_id}")
    print("="*50)

    # Filter: City = Seoul AND Device = Mobile
    target_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(filter=Filter(field_name="city", string_filter=Filter.StringFilter(value="Seoul"))),
                FilterExpression(filter=Filter(field_name="deviceCategory", string_filter=Filter.StringFilter(value="mobile")))
            ]
        )
    )

    with open("seoul_behavior.txt", "w", encoding="utf-8") as f:
        f.write(f"🕵️ Analysis Target: Seoul Mobile Users (Last 7 Days)\n")
        f.write("="*60 + "\n")

        # 1. WHAT did they view? (Page Paths)
        f.write("\n[1] 📄 Top Pages Visited\n")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[Metric(name="activeUsers"), Metric(name="screenPageViews"), Metric(name="userEngagementDuration")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimension_filter=target_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "screenPageViews"}}],
            limit=20
        )
        res = client.run_report(req)
        
        f.write(f"{'Page Path':<40} | {'Users':<5} | {'Views':<5} | {'Avg Time (s)':<10}\n")
        f.write("-" * 75 + "\n")
        
        for row in res.rows:
            path = row.dimension_values[0].value
            # title = row.dimension_values[1].value # Title might be long, let's stick to path mostly
            users = int(row.metric_values[0].value)
            views = int(row.metric_values[1].value)
            duration = float(row.metric_values[2].value)
            avg_time = duration / users if users > 0 else 0
            
            f.write(f"{path[:38]:<40} | {users:<5} | {views:<5} | {avg_time:.1f}\n")

        # 2. HOW MUCH did they explore? (Views per Session)
        # We can approximate this by total views / total sessions from summary
        # Let's run a summary for this segment
        f.write("\n[2] 🧭 Engagement Depth\n")
        req_summary = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[
                Metric(name="activeUsers"), 
                Metric(name="sessions"), 
                Metric(name="screenPageViews"),
                Metric(name="userEngagementDuration")
            ],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimension_filter=target_filter
        )
        res_summary = client.run_report(req_summary)
        
        if res_summary.rows:
            row = res_summary.rows[0]
            users = int(row.metric_values[0].value)
            sessions = int(row.metric_values[1].value)
            views = int(row.metric_values[2].value)
            duration = float(row.metric_values[3].value)
            
            avg_views_per_user = views / users if users > 0 else 0
            avg_time_per_user = duration / users if users > 0 else 0
            
            f.write(f"Total Users: {users}\n")
            f.write(f"Avg Page Views per User: {avg_views_per_user:.1f} pages\n")
            f.write(f"Avg Time Spent per User: {avg_time_per_user:.1f} seconds\n")
            
            if avg_views_per_user > 1.5:
                f.write(">> Insight: Users are browsing multiple pages (Good Sign).\n")
            else:
                f.write(">> Insight: Users mostly stay on one page (Bounce Risk).\n")

        # 3. EVENTS (Did they click anything?)
        f.write("\n[3] 🖱️ Key Events\n")
        req_events = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount"), Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimension_filter=target_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "eventCount"}}]
        )
        res_events = client.run_report(req_events)
        
        for row in res_events.rows:
            event = row.dimension_values[0].value
            count = int(row.metric_values[0].value)
            users = int(row.metric_values[1].value)
            f.write(f"- {event}: {count} times ({users} users)\n")

if __name__ == "__main__":
    analyze_seoul_behavior("518474196")
