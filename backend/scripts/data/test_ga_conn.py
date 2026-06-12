from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

def test_connection():
    try:
        client = BetaAnalyticsDataClient()
        property_id = "518474196"
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
            metrics=[Metric(name="activeUsers")]
        )
        response = client.run_report(request=request)
        print(f"SUCCESS: {response.rows[0].metric_values[0].value if response.rows else 0} active users yesterday.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_connection()
