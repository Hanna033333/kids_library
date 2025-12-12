import requests

API_URL = "http://data4library.kr/api/bookExist"

KEY = "def30b4852f8e59d803fb1ca1d19e866c45c76740c9b14f2d2cefe504d44d303"

params = {
    "authKey": KEY,
    "libCode": "141231",  # 분당아이파크도서관
    "isbn13": "9788949110851",  # 100만 번 산 고양이
    "format": "json"
}

res = requests.get(API_URL, params=params)
print(res.json())

