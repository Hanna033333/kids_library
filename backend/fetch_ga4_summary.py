from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

def verify_details(property_id):
    client = AnalyticsAdminServiceClient()
    print(f"PROPERTY DETAILS FOR {property_id}:")
    streams = client.list_data_streams(parent=f"properties/{property_id}")
    for stream in streams:
        mid = stream.web_stream_data.measurement_id if stream.web_stream_data else "N/A"
        print(f" - Data Stream: {stream.display_name} | Measurement ID: {mid}")

if __name__ == "__main__":
    verify_details("518474196")
