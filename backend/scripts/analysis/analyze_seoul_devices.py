
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

def analyze_seoul_devices(property_id):
    client = BetaAnalyticsDataClient()
    
    print("="*50)
    print(f"🕵️ SEOUL MOBILE DEVICE FORENSICS: {property_id}")
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

    with open("seoul_devices.txt", "w", encoding="utf-8") as f:
        f.write(f"🕵️ Device Breakdown for Seoul Mobile Users (Last 7 Days)\n")
        f.write("="*60 + "\n")

        # Breakdown by Device Model
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="deviceModel"), Dimension(name="operatingSystem"), Dimension(name="operatingSystemVersion")],
            metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="userEngagementDuration")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimension_filter=target_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
        )
        res = client.run_report(req)
        
        f.write(f"{'Model':<30} | {'OS':<10} | {'Ver':<8} | {'Users':<5} | {'AvgTime':<7}\n")
        f.write("-" * 80 + "\n")
        
        for row in res.rows:
            model = row.dimension_values[0].value
            os_name = row.dimension_values[1].value
            os_ver = row.dimension_values[2].value
            users = int(row.metric_values[0].value)
            duration = float(row.metric_values[2].value)
            avg_time = duration / users if users > 0 else 0
            
            f.write(f"{model:<30} | {os_name:<10} | {os_ver:<8} | {users:<5} | {avg_time:.1f}\n")

if __name__ == "__main__":
    analyze_seoul_devices("518474196")
