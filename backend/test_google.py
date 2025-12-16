import requests
import json
import time

TEST_ISBN = "9788936446819" 

def test_api():
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{TEST_ISBN}"
    
    print(f"Requesting to {url}...")
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        duration = time.time() - start
        
        print(f"Response received in {duration:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            volume_info = data["items"][0].get("volumeInfo", {})
            title = volume_info.get("title")
            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail")
            print(f"Success! Title: {title}")
            print(f"Thumbnail: {thumbnail}")
        else:
            print("No items found.")
            print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
