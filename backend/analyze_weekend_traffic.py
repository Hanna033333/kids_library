import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter,
    FilterExpressionList,
    OrderBy
)

def run_analysis(property_id):
    client = BetaAnalyticsDataClient()
    
    # Common filter to exclude dev traffic
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

    dates = [
        {"start": "2026-01-31", "end": "2026-01-31", "label": "Jan 31 (Sat)"},
        {"start": "2026-02-01", "end": "2026-02-01", "label": "Feb 01 (Sun)"}
    ]

    with open("backend/ga_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Analyzing GA4 Property: {property_id}\n")

        for date in dates:
            f.write(f"\n=== {date['label']} ===\n")
            
            # 1. Basic Traffic
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="activeUsers"), 
                    Metric(name="sessions"), 
                    Metric(name="screenPageViews"),
                    Metric(name="userEngagementDuration")
                ],
                date_ranges=[DateRange(start_date=date['start'], end_date=date['end'])],
                dimension_filter=dev_filter
            )
            response = client.run_report(request)
            
            if not response.rows:
                f.write("No data found.\n")
            else:
                row = response.rows[0]
                users = int(row.metric_values[0].value)
                sessions = int(row.metric_values[1].value)
                views = int(row.metric_values[2].value)
                duration = float(row.metric_values[3].value)
                avg_time = duration / users if users > 0 else 0
                
                f.write(f"Users: {users}\n")
                f.write(f"Sessions: {sessions}\n")
                f.write(f"Page Views: {views}\n")
                f.write(f"Avg Engagement: {avg_time:.1f}s\n")

            # 2. Event Counts (click_book_detail)
            event_request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="eventName")],
                metrics=[Metric(name="eventCount")],
                date_ranges=[DateRange(start_date=date['start'], end_date=date['end'])],
                dimension_filter=FilterExpression(
                    and_group=FilterExpressionList(
                        expressions=[
                            dev_filter,
                            FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="click_book_detail")))
                        ]
                    )
                )
            )
            event_response = client.run_report(event_request)
            if event_response.rows:
                f.write(f"Book Clicks: {event_response.rows[0].metric_values[0].value}\n")
            else:
                f.write("Book Clicks: 0\n")

        # 3. Combined Top Pages (Both Days)
        f.write("\n=== Top Pages (Jan 31 - Feb 01) ===\n")
        page_request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="2026-01-31", end_date="2026-02-01")],
            dimension_filter=dev_filter,
            order_bys=[OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                desc=True
            )],
            limit=10
        )
        page_response = client.run_report(page_request)
        for row in page_response.rows:
            path = row.dimension_values[0].value
            title = row.dimension_values[1].value
            views = row.metric_values[0].value
            users = row.metric_values[1].value
            f.write(f"[{views} views] {title} ({path})\n")

    # Double check without filter if no data found
    print("Checking raw data (no filter)...")
    raw_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        date_ranges=[DateRange(start_date="2026-01-31", end_date="2026-02-01")]
    )
    raw_response = client.run_report(raw_request)
    
    with open("backend/ga_result.txt", "a", encoding="utf-8") as f:
        f.write("\n=== Raw Data (No Filter) ===\n")
        if not raw_response.rows:
            f.write("No raw data found either. (Zero traffic)\n")
        else:
            for row in raw_response.rows:
                date = row.dimension_values[0].value
                users = row.metric_values[0].value
                sessions = row.metric_values[1].value
                f.write(f"Date: {date} | Users: {users} | Sessions: {sessions}\n")

    print("Analysis complete. Results written to backend/ga_result.txt")

if __name__ == "__main__":
    run_analysis("518474196")
