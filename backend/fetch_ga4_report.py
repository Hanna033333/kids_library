import os
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

def run_detailed_analysis(property_id):
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

    # 1. Page Analysis (Top Pages & Book Detail Views)
    print("\n--- TOP PAGES ANALYSIS ---")
    page_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="yesterday")],
        dimension_filter=dev_filter,
        limit=10
    )
    page_response = client.run_report(page_request)
    for row in page_response.rows:
        print(f"Page: {row.dimension_values[0].value:40} | Views: {row.metric_values[0].value:5} | Users: {row.metric_values[1].value}")

    # 2. Average Session Duration / Engagement Time
    print("\n--- PERFORMANCE & ENGAGEMENT ---")
    perf_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="userEngagementDuration"), 
            Metric(name="activeUsers"),
            Metric(name="sessions")
        ],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="yesterday")],
        dimension_filter=dev_filter
    )
    perf_response = client.run_report(perf_request)
    total_duration = 0
    total_users = 0
    for row in perf_response.rows:
        total_duration += float(row.metric_values[0].value)
        total_users += int(row.metric_values[1].value)
    
    avg_engagement = (total_duration / total_users) if total_users > 0 else 0
    print(f"Average Engagement Time per User: {avg_engagement:.2f} seconds")

if __name__ == "__main__":
    run_detailed_analysis("518474196")
