import os
import sys
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    DateRange, 
    Dimension, 
    Metric, 
    OrderBy,
    FilterExpression,
    Filter,
    FilterExpressionList
)

# Set credentials
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

def query_ga(start_date, end_date, dimensions, metrics, filter_expr=None, limit=None):
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        dimension_filter=filter_expr,
        limit=limit
    )
    return client.run_report(request=request)

def main():
    # Dev traffic exclusion filter (excluding Seongnam/Yongin Desktop and hada.io referrer)
    base_dev_filter = FilterExpressionList(
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

    refined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                FilterExpression(not_expression=FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))))
            ]
        )
    )

    # 1. Compare dates
    # 어제: 2026-05-27
    # 전전일: 2026-05-26
    date_yesterday = "2026-05-27"
    date_day_before = "2026-05-26"

    print("======================================================================")
    print(f"📊 GA4 비교 분석: 어제({date_yesterday}) vs 전전일({date_day_before})")
    print("======================================================================\n")

    # Fetch daily overview for both days separately to make it crystal clear
    for date_label, target_date in [("전전일", date_day_before), ("어제", date_yesterday)]:
        print(f"🔹 [{date_label}: {target_date}]")
        
        # Overview Metrics
        resp_overview = query_ga(
            target_date, target_date, 
            [], 
            ["activeUsers", "sessions", "screenPageViews", "userEngagementDuration", "engagementRate", "bounceRate"],
            refined_filter
        )
        
        if resp_overview.rows:
            row = resp_overview.rows[0]
            users = int(row.metric_values[0].value)
            sessions = int(row.metric_values[1].value)
            views = int(row.metric_values[2].value)
            duration = float(row.metric_values[3].value)
            engagement_rate = float(row.metric_values[4].value) * 100
            bounce_rate = float(row.metric_values[5].value) * 100
            avg_dur = duration / users if users > 0 else 0
            
            print(f"   - 활성 사용자: {users}명")
            print(f"   - 세션: {sessions}회")
            print(f"   - 페이지뷰: {views}회")
            print(f"   - 평균 참여시간: {avg_dur:.1f}초")
            print(f"   - 참여율: {engagement_rate:.1f}%")
            print(f"   - 이탈율: {bounce_rate:.1f}%")
        else:
            print("   - 데이터가 없습니다.")

        # User Type (New vs Returning)
        resp_user_type = query_ga(
            target_date, target_date,
            ["newVsReturning"],
            ["activeUsers"],
            refined_filter
        )
        print("   - 신규 vs 재방문 사용자:")
        for r in resp_user_type.rows:
            utype = r.dimension_values[0].value
            u_count = r.metric_values[0].value
            print(f"      * {utype}: {u_count}명")

        # Acquisition Channels
        resp_channels = query_ga(
            target_date, target_date,
            ["sessionSourceMedium"],
            ["activeUsers", "sessions"],
            refined_filter
        )
        print("   - 유입 채널:")
        for r in resp_channels.rows:
            ch = r.dimension_values[0].value
            ch_users = r.metric_values[0].value
            ch_sess = r.metric_values[1].value
            print(f"      * {ch}: {ch_users}명 ({ch_sess}세션)")

        # Top Pages
        resp_pages = query_ga(
            target_date, target_date,
            ["pagePath"],
            ["screenPageViews", "activeUsers"],
            refined_filter,
            limit=10
        )
        print("   - 인기 페이지 (Top Pages):")
        book_details_dau = 0
        for r in resp_pages.rows:
            path = r.dimension_values[0].value
            p_views = r.metric_values[0].value
            p_users = int(r.metric_values[1].value)
            print(f"      * {path:35} | {p_views:3}뷰 | {p_users}명")
            if "/book/" in path:
                book_details_dau += p_users
        print(f"   👉 [NSM] 도서 상세 페이지 DAU 총합: {book_details_dau}명")

        # Top Events
        resp_events = query_ga(
            target_date, target_date,
            ["eventName"],
            ["eventCount"],
            refined_filter,
            limit=10
        )
        print("   - 주요 이벤트 (Events):")
        for r in resp_events.rows:
            ev = r.dimension_values[0].value
            ev_cnt = r.metric_values[0].value
            print(f"      * {ev}: {ev_cnt}회")
        
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
