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

def run_last_week_analysis(property_id):
    client = BetaAnalyticsDataClient()
    
    # Range: 2026-03-09 to 2026-03-15
    start_date = "2026-03-09"
    end_date = "2026-03-15"
    
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

    print(f"GA4 Analysis Report: {start_date} to {end_date}")
    print("=" * 50)

    # 1. Funnel Stages (Events and Page Views)
    print("\n[1] Funnel Analysis")
    
    # Home & List Views
    page_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    dev_filter,
                    FilterExpression(
                        or_group=FilterExpressionList(
                            expressions=[
                                FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(value="/"))),
                                FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(value="/books")))
                            ]
                        )
                    )
                ]
            )
        )
    )
    
    # Custom Events
    event_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    dev_filter,
                    FilterExpression(
                        or_group=FilterExpressionList(
                            expressions=[
                                FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="view_book_detail"))),
                                FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="click_buy_kyobo")))
                            ]
                        )
                    )
                ]
            )
        )
    )

    page_response = client.run_report(page_request)
    event_response = client.run_report(event_request)

    funnel = {
        "Home": 0,
        "List": 0,
        "Book Detail": 0,
        "Purchase Click": 0
    }

    for row in page_response.rows:
        path = row.dimension_values[0].value
        views = int(row.metric_values[0].value)
        if path == "/": funnel["Home"] = views
        elif path == "/books": funnel["List"] = views

    for row in event_response.rows:
        name = row.dimension_values[0].value
        count = int(row.metric_values[0].value)
        if name == "view_book_detail": funnel["Book Detail"] = count
        elif name == "click_buy_kyobo": funnel["Purchase Click"] = count

    for stage, count in funnel.items():
        print(f" - {stage:15}: {count:5}")

    # 2. Performance & Engagement
    print("\n[2] Performance & Engagement")
    perf_request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[
            Metric(name="userEngagementDuration"), 
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=dev_filter
    )
    perf_response = client.run_report(perf_request)
    
    if perf_response.rows:
        row = perf_response.rows[0]
        duration = float(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        sessions = int(row.metric_values[2].value)
        views = int(row.metric_values[3].value)
        
        avg_engagement = (duration / users) if users > 0 else 0
        views_per_session = (views / sessions) if sessions > 0 else 0
        
        print(f" - Active Users: {users}")
        print(f" - Sessions: {sessions}")
        print(f" - Views per Session: {views_per_session:.2f}")
        print(f" - Avg Engagement Time: {avg_engagement:.2f} seconds")

    # 3. Top Content (Top Books based on view_book_detail)
    print("\n[3] Top Books (by View Event)")
    # Since custom parameters might not be registered as dimensions, 
    # we'll use pageTitle or pagePath which usually contains the title/id
    top_books_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    dev_filter,
                    FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.BEGINS_WITH, value="/book/")))
                ]
            )
        ),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5
    )
    top_books_response = client.run_report(top_books_request)
    for row in top_books_response.rows:
        title = row.dimension_values[0].value.replace(" - 책자리", "")
        views = row.metric_values[0].value
        print(f" - {title[:40]:40}: {views:5} views")

    # 4. Traffic Sources
    print("\n[4] Top Traffic Sources")
    source_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=dev_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=5
    )
    source_response = client.run_report(source_request)
    for row in source_response.rows:
        source = row.dimension_values[0].value
        count = row.metric_values[0].value
        print(f" - {source:30}: {count:5} sessions")

if __name__ == "__main__":
    run_last_week_analysis("518474196")
