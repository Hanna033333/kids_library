
import os
import sys
import subprocess
from datetime import datetime

# 1. Install dependencies if missing
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, FilterExpression, Filter
    from google.analytics.admin import AnalyticsAdminServiceClient
except ImportError:
    print("📦 Installing Google Analytics libraries...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-analytics-data", "google-analytics-admin"])
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
    from google.analytics.admin import AnalyticsAdminServiceClient

# 2. Configuration
KEY_PATH = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

if not os.path.exists(KEY_PATH):
    print(f"❌ Key file not found at: {KEY_PATH}")
    sys.exit(1)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

def get_property_id():
    """Finds the GA4 Property ID for the project."""
    try:
        client = AnalyticsAdminServiceClient()
        # List accounts first? No, list properties directly usually works if service account has access
        # But we might need to know the parent account.
        # Let's try searching properties accessible.
        # Note: 'list_properties' requires a filter for parent, or just list accessible ones if supported.
        # Actually, list_account_summaries is easier to find accessible properties.
        from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient as AdminClientV1Alpha
        
        # Fallback to hardcoded if lookup fails or use Account Summaries
        # Let's try to just list account summaries which is standard for "what can I see?"
        client = AdminClientV1Alpha()
        request = client.list_account_summaries(parent="")
        
        print("\n🔎 Searching for GA4 Properties...")
        for account in request:
            for property_summary in account.property_summaries:
                print(f"   - Found Property: {property_summary.display_name} (ID: {property_summary.property})")
                if "kids" in property_summary.display_name.lower() or "library" in property_summary.display_name.lower() or "책자리" in property_summary.display_name:
                    return property_summary.property.split('/')[-1]
        
        # If loop finishes without return
        print("⚠️ No matching property found automatically.")
        return None
    except Exception as e:
        print(f"⚠️ Error listing properties: {e}")
        # Default/Hardcoded from previous context if available, else fail
        # Previous conversation mentioned kids-library-483408, but that's project ID.
        return None

def run_marketing_report(property_id):
    if not property_id:
        print("❌ Property ID is missing. Cannot run report.")
        return

    client = BetaAnalyticsDataClient()
    
    print(f"\n📊 Generating Report for Property ID: {property_id}")
    print("=" * 50)

    # 1. Overview Metrics (Last 7 Days)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="userEngagementDuration"),
        ]
    )
    response = client.run_report(request=request)
    
    print("\n1️⃣  Traffic Overview (Last 7 Days)")
    for row in response.rows:
        users = row.metric_values[0].value
        sessions = row.metric_values[1].value
        views = row.metric_values[2].value
        duration = float(row.metric_values[3].value)
        avg_time = duration / int(users) if int(users) > 0 else 0
        
        print(f"   - Active Users: {users}")
        print(f"   - Total Sessions: {sessions}")
        print(f"   - Page Views: {views}")
        print(f"   - Avg Engagement: {avg_time:.1f} sec")

    # 2. Acquisition Channels
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="activeUsers"), Metric(name="sessions")],
        order_bys=[{"desc": True, "metric": {"metric_name": "activeUsers"}}]
    )
    response = client.run_report(request=request)
    
    print("\n2️⃣  Acquisition Channels (Where they came from)")
    for row in response.rows:
        print(f"   - {row.dimension_values[0].value}: {row.metric_values[0].value} users")

    # 3. Top Pages
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        order_bys=[{"desc": True, "metric": {"metric_name": "screenPageViews"}}]
    )
    response = client.run_report(request=request)
    
    print("\n3️⃣  Top Pages (What they watched)")
    for row in response.rows:
        print(f"   - {row.dimension_values[0].value}: {row.metric_values[0].value} views")

if __name__ == "__main__":
    pid = get_property_id()
    if pid:
        run_marketing_report(pid)
    else:
        print("\n❌ Could not find any GA4 property. Please check permissions.")
