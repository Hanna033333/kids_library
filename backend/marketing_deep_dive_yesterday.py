
import sys
import os
# Force UTF-8 encoding
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

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

def run_deep_dive_analysis(property_id):
    client = BetaAnalyticsDataClient()
    
    # Common filter to exclude dev traffic (Seongnam/Yongin Desktop)
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

    with open("marketing_result_yesterday.txt", "w", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write(f"📊 REPORTING FOR PROPERTY: {property_id} (Yesterday)\n")
        f.write("="*50 + "\n")

        # 1. ACQUISITION
        f.write("\n[1] 🌍 Acquisition Source/Medium\n")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="sessionSourceMedium")],
            metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="userEngagementDuration")],
            date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
            # dimension_filter=dev_filter, # Optional: Turn off filter if we want to see EVERYTHING first. Let's keep it to see 'real' data? 
            # Actually, for yesterday's specific analysis, seeing everything is safer to match previous numbers. 
            # But the user asked for INSIGHTS, so filtering internal traffic is better. 
            # Let's Apply it.
            dimension_filter=dev_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
        )
        res = client.run_report(req)
        if not res.rows:
            f.write("   (No data found)\n")
        for row in res.rows:
            users = int(row.metric_values[0].value)
            sessions = int(row.metric_values[1].value)
            duration = float(row.metric_values[2].value)
            avg_time = duration / users if users > 0 else 0
            f.write(f"   - {row.dimension_values[0].value:30} | Users: {users:3} | Sess: {sessions:3} | AvgTime: {avg_time:.1f}s\n")

        # 2. TOP PAGES with TITLES
        f.write("\n[2] 📄 Top Content\n")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"), Metric(name="userEngagementDuration")],
            date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
            dimension_filter=dev_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "screenPageViews"}}],
            limit=20
        )
        res = client.run_report(req)
        for row in res.rows:
            path = row.dimension_values[0].value
            title = row.dimension_values[1].value
            views = int(row.metric_values[0].value)
            users = int(row.metric_values[1].value)
            duration = float(row.metric_values[2].value)
            avg_time = duration / users if users > 0 else 0
            f.write(f"   - {path:30} | {title[:40]:40} | Views: {views:3} | Users: {users:3} | AvgTime: {avg_time:.1f}s\n")

        # 3. LOCATION
        f.write("\n[3] 📍 Top Cities\n")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
            dimension_filter=dev_filter,
            order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}],
            limit=10
        )
        res = client.run_report(req)
        for row in res.rows:
             f.write(f"   - {row.dimension_values[0].value:30} | Users: {row.metric_values[0].value}\n")

if __name__ == "__main__":
    run_deep_dive_analysis("518474196")
