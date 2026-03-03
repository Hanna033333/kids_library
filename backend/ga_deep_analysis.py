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

def run_deep_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    start_date = "7daysAgo"
    end_date = "yesterday"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"🔍 GA4 심층 분석 리포트 (최종 업데이트)")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # Common dev traffic filter
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

    # 1. /caldecott Page Time-based Analysis (Filtering by Title)
    report_lines.append("1️⃣  칼데콧 관련 트래픽 시간대별 분석 (금요일 저녁/토요일 새벽)")
    report_lines.append("-" * 70)
    
    caldecott_title_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[
                dev_filter,
                FilterExpression(filter=Filter(field_name="pageTitle", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="칼데콧")))
            ]
        )
    )
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="date"), Dimension(name="hour")],
        metrics=[Metric(name="screenPageViews")],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date")), OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="hour"))],
        dimension_filter=caldecott_title_filter
    )
    response = client.run_report(request=request)
    
    for row in response.rows:
        date_str = row.dimension_values[0].value
        hour = row.dimension_values[1].value
        views = row.metric_values[0].value
        # Focus on Feb 6 (Fri) evening and Feb 7 (Sat) dawn/day
        if "20260206" in date_str and int(hour) >= 18:
            report_lines.append(f"   [금요일] {date_str} {hour}시: {views}회")
        elif "20260207" in date_str and int(hour) <= 6:
            report_lines.append(f"   [토요일 새벽] {date_str} {hour}시: {views}회")
        elif "20260207" in date_str:
             report_lines.append(f"   [토요일 기타] {date_str} {hour}시: {views}회")

    # 2. Retention Analysis (New vs Returning)
    report_lines.append("\n\n2️⃣  리텐션 분석 (New vs Returning)")
    report_lines.append("-" * 70)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions"), Metric(name="averageSessionDuration")],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    for row in response.rows:
        status = row.dimension_values[0].value
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        avg_dur = float(row.metric_values[2].value)
        report_lines.append(f"   {status:10}: {users:3}명 | {sessions:3}세션 | 평균체류 {avg_dur:.1f}s")

    # 3. Funnel Analysis by Source
    report_lines.append("\n\n3️⃣  유입 채널별 상세 퍼널 (방문 -> 도서 상세 -> 구매 클릭)")
    report_lines.append("-" * 70)
    
    sources = [
        {"name": "Naver Cafe (M)", "filter": "m.cafe.naver.com / referral"},
        {"name": "Naver Organic", "filter": "naver / organic"},
        {"name": "Direct", "filter": "(direct) / (none)"},
        {"name": "Gecko News", "filter": "news.hada.io / referral"}
    ]
    
    for src in sources:
        src_filter = FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    dev_filter,
                    FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(value=src["filter"])))
                ]
            )
        )
        
        event_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=src_filter
        )
        evt_resp = client.run_report(event_request)
        
        events = {row.dimension_values[0].value: int(row.metric_values[0].value) for row in evt_resp.rows}
        visits = events.get('session_start', 0)
        details = events.get('view_book_detail', 0)
        buys = events.get('click_buy_kyobo', 0)
        
        conv_rate = (buys / visits * 100) if visits > 0 else 0
        report_lines.append(f"\n   [{src['name']}]")
        report_lines.append(f"      - 방문: {visits:3}회")
        report_lines.append(f"      - 상세조회: {details:3}회 ({(details/visits*100 if visits>0 else 0):.1f}%)")
        report_lines.append(f"      - 구매클릭: {buys:3}회 ({conv_rate:.1f}%)")

    # 4. Paid Search Keywords (Trying broader search)
    report_lines.append("\n\n4️⃣  유료 검색(Paid Search) 및 키워드 분석")
    report_lines.append("-" * 70)
    
    # Try different search term dimensions
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium"), Dimension(name="googleAdsKeyword")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=dev_filter
    )
    response = client.run_report(request=request)
    paid_found = False
    for row in response.rows:
        source = row.dimension_values[0].value
        keyword = row.dimension_values[1].value
        users = row.metric_values[0].value
        if 'cpc' in source.lower() or 'paid' in source.lower() or 'ad' in source.lower():
            report_lines.append(f"   출처: {source} | 키워드: {keyword} | 유저: {users}명")
            paid_found = True
    
    if not paid_found:
        report_lines.append("   유료 검색 유입이 발견되지 않았습니다. (CPC 트래픽은 있으나 키워드 연동 전일 수 있음)")

    # Save and Print
    report_text = "\n".join(report_lines)
    output_file = os.path.join(script_dir, "ga_deep_analysis_report_v2.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)

if __name__ == "__main__":
    run_deep_analysis()
