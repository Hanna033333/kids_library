
import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter
)

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"c:\Users\skplanet\Desktop\kids library\ga4-key.json"

PROPERTY_ID = "518474196"

# Daily #1 Books from previous step
DAILY_TOP_BOOKS = {
    "2026-01-29": "11315",
    "2026-01-30": "11306",
    "2026-01-31": "11291",
    "2026-02-01": "11304",
    "2026-02-02": "11305",
    "2026-02-03": "11325", # Jambi
    "2026-02-04": "11310",
}

TARGET_JAMBI = "11325"

def get_views_for_date(date_str):
    client = BetaAnalyticsDataClient()
    
    # Filter for book detail pages only to save processing
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        limit=1000
    )
    
    response = client.run_report(request=request)
    
    views_map = {}
    for row in response.rows:
        path = row.dimension_values[0].value
        views = int(row.metric_values[0].value)
        
        # Extract ID from /book/12345
        if path.startswith("/book/"):
            try:
                book_id = path.split("/")[-1]
                views_map[book_id] = views
            except:
                pass
            
    return views_map

def analyze():
    # Write to file
    with open("backend/daily_views_result.txt", "w", encoding="utf-8") as f:
        header = f"{'Date':^12} | {'#1 Book':^10} | {'#1 Views':^8} | {'Jambi(11325)':^12} | {'Top View(Any)':^12}"
        print(header)
        f.write(header + "\n")
        f.write("-" * 70 + "\n")
        print("-" * 70)

        for date_str, top_book_id in DAILY_TOP_BOOKS.items():
            views = get_views_for_date(date_str)
            
            # Views for the #1 book of that day
            top_book_views = views.get(top_book_id, 0)
            
            # Views for Jambi
            jambi_views = views.get(TARGET_JAMBI, 0)
            
            # Who was the actual top viewed book?
            if views:
                actual_top_id = max(views, key=views.get)
                actual_top_views = views[actual_top_id]
                actual_top_str = f"{actual_top_id}({actual_top_views})"
            else:
                actual_top_str = "None"
                
            line = f"{date_str:^12} | {top_book_id:^10} | {top_book_views:^8} | {jambi_views:^12} | {actual_top_str:^12}"
            print(line)
            f.write(line + "\n")

if __name__ == "__main__":
    analyze()
