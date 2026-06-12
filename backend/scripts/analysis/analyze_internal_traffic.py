
import sys
# Force UTF-8 encoding for Windows console/redirection
sys.stdout.reconfigure(encoding='utf-8')

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy
)

def analyze_traffic_quality(property_id):
    client = BetaAnalyticsDataClient()
    
    print("="*50)
    print(f"🕵️ INTERNAL TRAFFIC INVESTIGATION: {property_id}")
    print("="*50)

    # Breakdown by City + Device
    print("\n[1] 🏙️ Users by City & Device (Last 7 Days)")
    req = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city"), Dimension(name="deviceCategory")],
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"), 
            Metric(name="userEngagementDuration")
        ],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    res = client.run_report(req)
    
    with open("traffic_quality.txt", "w", encoding="utf-8") as f:
        f.write("City                  | Device    | Users | Sess | AvgTime (s)\n")
        f.write("-" * 60 + "\n")
        
        for row in res.rows:
            city = row.dimension_values[0].value
            device = row.dimension_values[1].value
            users = int(row.metric_values[0].value)
            sess = int(row.metric_values[1].value)
            duration = float(row.metric_values[2].value)
            avg_time = duration / users if users > 0 else 0
            
            line = f"{city:21} | {device:9} | {users:5} | {sess:4} | {avg_time:.1f}\n"
            print(line.strip())
            f.write(line)

if __name__ == "__main__":
    analyze_traffic_quality("518474196")
