import os
import sys
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
# Assumes key is in the parent directory of backend, similar to existing scripts
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
if not os.path.exists(key_path):
    print(f"Error: Key file not found at {key_path}")
    sys.exit(1)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

def run_weekly_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"📊 주간 GA4 마케팅/퍼널 분석 리포트")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # ---------------------------------------------------------
    # 1. Filters Setup (Exclude Internal & Bots)
    # ---------------------------------------------------------
    
    # Internal filter: Seongnam/Yongin Desktop
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

    # Exclude Gecko News (Bot/Crawler traffic)
    exclude_gecko_filter = FilterExpression(
        not_expression=FilterExpression(
            filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="news.hada.io"))
        )
    )

    # Combined Filter: Not Internal AND Not Gecko
    marketing_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                FilterExpression(not_expression=FilterExpression(or_group=base_dev_filter)),
                exclude_gecko_filter
            ]
        )
    )

    # ---------------------------------------------------------
    # 2. Key Funnel Analysis
    # Funnel: Session Start (Home/Entry) -> View Book Detail -> Click Buy
    # ---------------------------------------------------------
    report_lines.append("1️⃣  핵심 퍼널 분석 (Core Funnel Analysis)")
    report_lines.append(f"   (Internal & Gecko News 트래픽 제외)")
    report_lines.append("-" * 70)

    funnel_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="totalUsers"), Metric(name="eventCount")],
        dimension_filter=marketing_filter
    )
    
    funnel_resp = client.run_report(request=funnel_request)
    
    # Extract event counts
    events = {row.dimension_values[0].value: int(row.metric_values[1].value) for row in funnel_resp.rows}
    users_event = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in funnel_resp.rows}
    
    # Funnel Steps
    step1_visits = events.get('session_start', 0)
    step2_details = events.get('view_book_detail', 0)
    step3_buys = events.get('click_buy_kyobo', 0)
    
    # Conversion Rates
    conv_home_to_detail = (step2_details / step1_visits * 100) if step1_visits > 0 else 0
    conv_detail_to_buy = (step3_buys / step2_details * 100) if step2_details > 0 else 0
    conv_total = (step3_buys / step1_visits * 100) if step1_visits > 0 else 0
    
    report_lines.append(f"   [단계별 지표]")
    report_lines.append(f"   1. 홈/진입 (Session Start) : {step1_visits:,}회")
    report_lines.append(f"      ↓ 전환율: {conv_home_to_detail:.1f}%")
    report_lines.append(f"   2. 상세 진입 (View Detail) : {step2_details:,}회")
    report_lines.append(f"      ↓ 전환율: {conv_detail_to_buy:.1f}%")
    report_lines.append(f"   3. 구매 클릭 (Click Buy)   : {step3_buys:,}회")
    report_lines.append(f"   ----------------------------------------")
    report_lines.append(f"   🎯 전체 전환율 (Visit -> Buy): {conv_total:.2f}%")
    
    # Details per User (Engagement proxy)
    unique_viewers = users_event.get('view_book_detail', 0)
    avg_views = (step2_details / unique_viewers) if unique_viewers > 0 else 0
    report_lines.append(f"\n   👉 인당 평균 도서 상세 조회수: {avg_views:.1f}권 (활성 유저 기준)")


    # ---------------------------------------------------------
    # 3. Retention Analysis
    # ---------------------------------------------------------
    report_lines.append("\n\n2️⃣  리텐션(Retention) 지표")
    report_lines.append("-" * 70)
    
    # Total Retention
    retention_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=marketing_filter
    )
    ret_resp = client.run_report(request=retention_request)
    
    ret_data = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in ret_resp.rows}
    new_users = ret_data.get('new', 0)
    returning_users = ret_data.get('returning', 0)
    total_active = new_users + returning_users
    retention_rate = (returning_users / total_active * 100) if total_active > 0 else 0
    
    report_lines.append(f"   [전체 트래픽]")
    report_lines.append(f"   - 총 활성 유저: {total_active:,}명")
    report_lines.append(f"   - 신규 유저   : {new_users:,}명 ({(new_users/total_active*100 if total_active else 0):.1f}%)")
    report_lines.append(f"   - 재방문 유저 : {returning_users:,}명")
    report_lines.append(f"   🔥 리텐션(재방문) 비율: {retention_rate:.1f}%")

    # Channel Breakdown (Top 5)
    report_lines.append("\n   [유입 채널별 리텐션 Top 5]")
    
    channel_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSource"), Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=marketing_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)]
    )
    ch_resp = client.run_report(request=channel_request)
    
    # Process channel data
    channel_stats = {}
    for row in ch_resp.rows:
        source = row.dimension_values[0].value
        user_type = row.dimension_values[1].value
        count = int(row.metric_values[0].value)
        
        if source not in channel_stats:
            channel_stats[source] = {'new': 0, 'returning': 0, 'total': 0}
        
        if user_type == 'new':
            channel_stats[source]['new'] += count
        else:
            channel_stats[source]['returning'] += count
        channel_stats[source]['total'] += count
        
    # Sort by total users and take Top 5
    sorted_channels = sorted(channel_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
    
    for source, stats in sorted_channels:
        rate = (stats['returning'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report_lines.append(f"   - {source:<15} : {rate:4.1f}% 재방문 ({stats['returning']}/{stats['total']})")

    # ---------------------------------------------------------
    # 4. Book Engagement (Top Books)
    # ---------------------------------------------------------
    report_lines.append("\n\n3️⃣  인기 도서 (Top 5)")
    report_lines.append("-" * 70)
    
    book_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pageTitle")], # approximates book title if title tag is set correctly
        metrics=[Metric(name="screenPageViews")],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    marketing_filter,
                    FilterExpression(filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.BEGINS_WITH, value="/book/")))
                ]
            )
        ),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5
    )
    book_resp = client.run_report(request=book_request)
    
    for row in book_resp.rows:
        title = row.dimension_values[0].value.replace(" - 책자리", "").strip() # Remove site name if present
        views = int(row.metric_values[0].value)
        report_lines.append(f"   - {title[:30]:<30} : {views} Views")


    # Save and Print
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_weekly_report.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)

if __name__ == "__main__":
    run_weekly_analysis()
