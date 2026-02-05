
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric,
    FilterExpression, Filter, FilterExpressionList, OrderBy
)

PROPERTY_ID = "518474196"
KEY_PATH = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

if os.path.exists(KEY_PATH):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

def get_segment_data(client, label, segment_filter, dev_filter):
    print(f"\n📊 Analyzing Segment: {label} ...")
    
    # Combine segment filter and dev filter
    combined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[segment_filter, dev_filter]
        )
    )

    # 1. Overview Metrics
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        # Look at last 30 days to ensure we catch the MomCafe traffic from earlier days
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")], 
        metrics=[
            Metric(name="activeUsers"), 
            Metric(name="sessions"), 
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration")
        ],
        dimension_filter=combined_filter
    )
    response = client.run_report(request)
    
    metrics = {"users": 0, "sessions": 0, "views": 0, "avg_time": 0.0}
    if response.rows:
        row = response.rows[0]
        metrics["users"] = int(row.metric_values[0].value)
        metrics["sessions"] = int(row.metric_values[1].value)
        metrics["views"] = int(row.metric_values[2].value)
        duration = float(row.metric_values[3].value)
        metrics["avg_time"] = duration / metrics["users"] if metrics["users"] > 0 else 0

    print(f"   - Users: {metrics['users']}")
    print(f"   - Avg Time: {metrics['avg_time']:.1f}s")
    print(f"   - Views/User: {metrics['views']/metrics['users']:.1f}" if metrics['users'] > 0 else "   - Views/User: 0")

    # 2. Book Detail Clicks (Conversion Proxy)
    event_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    combined_filter,
                    FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="click_book_detail")))
                ]
            )
        )
    )
    event_resp = client.run_report(event_request)
    clicks = int(event_resp.rows[0].metric_values[0].value) if event_resp.rows else 0
    conversion_rate = (clicks / metrics['users'] * 100) if metrics['users'] > 0 else 0
    print(f"   - Book Detail Clicks: {clicks} (Events/User: {conversion_rate:.1f}%)")

    # 3. Top Pages (to see where they go)
    page_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        dimension_filter=combined_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5
    )
    page_resp = client.run_report(page_request)
    print("   - Top Pages:")
    for row in page_resp.rows:
        print(f"     * {row.dimension_values[0].value}: {row.metric_values[0].value} views (by {row.metric_values[1].value} users)")

    return metrics

def main():
    client = BetaAnalyticsDataClient()
    
    # Dev Filter
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

    # GeekNews: source contains 'news.hada.io'
    geek_filter = FilterExpression(
        filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="news.hada.io"))
    )

    # MomCafe: source contains 'cafe.naver.com'
    mom_filter = FilterExpression(
        filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="cafe.naver.com"))
    )

    get_segment_data(client, "GeekNews (news.hada.io)", geek_filter, dev_filter)
    get_segment_data(client, "Mom Cafe (cafe.naver.com)", mom_filter, dev_filter)

if __name__ == "__main__":
    main()
