
import requests
import json
import os
import sys
from pathlib import Path

# Add the current directory to sys.path to import core
sys.path.append(str(Path(__file__).parent))

from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
# 안녕, 나의 등대 (ISBN: 9788949113760)
test_isbn = "9788949113760"

def test_lib_srch():
    # libSrchByBook API 사용
    url = "http://data4library.kr/api/libSrchByBook"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn": test_isbn,
        "format": "json"
    }
    
    print(f"Testing libSrchByBook with ISBN: {test_isbn}")
    response = requests.get(url, params=params)
    data = response.json()
    
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_lib_srch()
