import requests
from bs4 import BeautifulSoup
import re

def search_full_callno(title):
    search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResultList.do"
    
    params = {
        "searchType": "SIMPLE",
        "searchCategory": "BOOK",
        "searchKeyword": title,
        "limit": 1000
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"Searching for: {title}")
    
    try:
        res = requests.post(search_url, data=params, headers=headers, timeout=15)
        print(f"Response Status: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Save HTML for inspection
        with open("debug_missing.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
            
        print("Scraping results for '청구기호'...")
        
        # Find all text nodes containing "청구기호:"
        callno_nodes = soup.find_all(string=re.compile(r"청구기호:"))
        
        found_callnos = []
        for node in callno_nodes:
            text = node.strip()
            print(f"  Found text node: {text}")
            
            # extract value after "청구기호:"
            if "청구기호:" in text:
                val = text.split("청구기호:")[1].strip()
                found_callnos.append(val)
                
        print(f"Found call numbers: {found_callnos}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # ISBN from Batch 2 sample: 가족 123
    search_full_callno("9788990614018")
