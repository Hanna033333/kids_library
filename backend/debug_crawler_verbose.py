import sys
import os
import requests
from bs4 import BeautifulSoup
import re

# Add current directory to path
sys.path.append(os.getcwd())

def debug_crawler(isbn13, title, base_callno):
    print(f"Testing with: ISBN={isbn13}, Title={title}, BaseCallNo={base_callno}")
    
    search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResultList.do"
    search_keyword = title if title else isbn13
    
    params = {
        "searchType": "SIMPLE",
        "searchCategory": "BOOK",
        "searchKey": "ALL",
        "searchKeyword": search_keyword,
        "searchLibrary": "",
        "searchPbLibrary": "ALL",
        "currentPageNo": "1",
        "searchRecordCount": "20"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"Requesting URL: {search_url}")
    print(f"Params: {params}")
    
    try:
        res = requests.post(search_url, data=params, headers=headers, timeout=15)
        print(f"Response Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Check for result count
        if "Total" in res.text:
             print("Found 'Total' in response.")
        
        # Save HTML for inspection
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
            
        print(f"HTML saved to debug.html")
        
        if title in res.text:
            print(f"SUCCESS: Title '{title}' found in response!")
        else:
            print(f"FAILURE: Title '{title}' NOT found in response.")

        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        found_pangyo = False
        
        for i, table in enumerate(tables):
            print(f"Checking table {i+1}...")
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Check for Pangyo library
                row_str = " | ".join(cell_texts)
                if '판교' in row_str:
                    found_pangyo = True
                    print(f"Found Pangyo row: {row_str}")
                    
                    if base_callno in row_str:
                        print(f"  -> Base callno '{base_callno}' found in row!")
                    else:
                        print(f"  -> Base callno '{base_callno}' NOT found in row.")

        if not found_pangyo:
            print("Pangyo library not found in any table row.")
            # Print full text preview
            print("First 1000 chars of text:")
            print(soup.get_text()[:1000])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_crawler('9788949110370', '난 곰인 채로 있고 싶은데…', '유 808.9-ㅂ966ㅂ')
