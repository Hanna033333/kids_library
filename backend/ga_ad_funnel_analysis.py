import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    DateRange, 
    Dimension, 
    Metric, 
    FilterExpression,
    Filter,
    FilterExpressionList
)

# Set credentials
script_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(os.path.dirname(script_dir), "ga4-key.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

def run_ad_funnel_analysis():
    client = BetaAnalyticsDataClient()
    property_id = "518474196"
    
    # 분석 기간 설정 (최근 14일로 확대하여 모수 확보)
    start_date = "14daysAgo"
    end_date = "today"
    
    report_lines = []
    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"🚀 검색 광고(CPC) 전환 퍼널 분석 리포트")
    report_lines.append(f"분석 기간: {start_date} ~ {end_date}")
    report_lines.append(f"{'='*70}\n")
    
    # 1. 내부 트래픽 제외 필터 (성남/용인 데스크탑)
    dev_filter_list = FilterExpressionList(
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
    
    exclude_internal = FilterExpression(not_expression=FilterExpression(or_group=dev_filter_list))
    
    # 2. 광고 유입 필터 (CPC + Naver + Direct 중 주요 랜딩 포함)
    ad_filter = FilterExpression(
        or_group=FilterExpressionList(
            expressions=[
                FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(match_type=Filter.StringFilter.MatchType.CONTAINS, value="cpc"))),
                FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="naver"))),
                FilterExpression(filter=Filter(field_name="sessionSource", string_filter=Filter.StringFilter(value="m.naver.com"))),
                FilterExpression(filter=Filter(field_name="sessionSourceMedium", string_filter=Filter.StringFilter(value="(direct) / (none)")))
            ]
        )
    )
    
    combined_filter = FilterExpression(
        and_group=FilterExpressionList(
            expressions=[exclude_internal, ad_filter]
        )
    )

    # 3. 퍼널 데이터 추출
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount"), Metric(name="activeUsers")],
        dimension_filter=combined_filter
    )
    
    response = client.run_report(request=request)
    events = {row.dimension_values[0].value: {
        'count': int(row.metric_values[0].value),
        'users': int(row.metric_values[1].value)
    } for row in response.rows}
    
    # 4. 페이지 뷰 기반 분석 (Search/List 진입 확인)
    page_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=combined_filter
    )
    page_response = client.run_report(page_request)
    
    search_list_users = 0
    for row in page_response.rows:
        path = row.dimension_values[0].value
        users = int(row.metric_values[0].value)
        # 검색어나 필터가 포함된 페이지 확인 (/books?q=, /books?age= 등)
        if "/books" in path and ("q=" in path or "age=" in path or "category=" in path or "curation=" in path):
            search_list_users += users
            
    # 퍼널 산출
    total_sessions = events.get('session_start', {}).get('users', 0)
    detail_views = events.get('view_book_detail', {}).get('users', 0)
    conversions = events.get('click_buy_kyobo', {}).get('users', 0) # 구매 클릭을 최종 전환으로 간주
    
    report_lines.append("📊 [전체 광고 유입 퍼널]")
    report_lines.append(f"1. 광고 유입 (Session Start) : {total_sessions}명")
    report_lines.append(f"2. 검색/리스트 탐색          : {search_list_users}명 ({(search_list_users/total_sessions*100 if total_sessions>0 else 0):.1f}%)")
    report_lines.append(f"3. 도서 상세 진입            : {detail_views}명 ({(detail_views/total_sessions*100 if total_sessions>0 else 0):.1f}%)")
    report_lines.append(f"4. 최종 전환 (구매/링크 클릭)  : {conversions}명 ({(conversions/total_sessions*100 if total_sessions>0 else 0):.1f}%)")
    
    # 5. 상세 경로 및 소스 확인 (디버깅용)
    report_lines.append("\n\n🛠️ [디버깅: 상세 유입 데이터]")
    report_lines.append("-" * 70)
    
    debug_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionSourceMedium"), Dimension(name="pagePath")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=combined_filter
    )
    debug_response = client.run_report(debug_request)
    for row in debug_response.rows:
        src = row.dimension_values[0].value
        path = row.dimension_values[1].value
        users = row.metric_values[0].value
        report_lines.append(f" - 소스: {src:25} | 경로: {path:30} | {users}명")

    # 6. 광고 키워드/콘텐츠별 상세 성과 (Top 10)
    report_lines.append("\n\n📍 [광고 키워드/콘텐츠별 상세 성과 (Top 10)]")
    report_lines.append("-" * 70)
    
    kw_request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionManualTerm"), Dimension(name="sessionManualAdContent")],
        metrics=[Metric(name="activeUsers")],
        dimension_filter=combined_filter
    )
    kw_response = client.run_report(kw_request)
    
    report_lines.append(f"{'키워드(또는 소재)':<30} | {'유저수':<10}")
    report_lines.append("-" * 45)
    for row in kw_response.rows:
        term = row.dimension_values[0].value
        content = row.dimension_values[1].value
        users = row.metric_values[0].value
        label = term if term and term != "(not set)" else (content if content and content != "(not set)" else "기타광고")
        report_lines.append(f"{label:<30} | {users:<10}명")

    # 결과 저장
    report_text = "\n".join(report_lines)
    output_path = os.path.join(script_dir, "ga_ad_funnel_report.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(report_text)

if __name__ == "__main__":
    run_ad_funnel_analysis()
