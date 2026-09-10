import json
import urllib.request
import urllib.error

INDEXNOW_KEY = "a89f31bc5e904b7f9202dfb845d401ef"
HOST = "www.checkjari.com"
KEY_LOCATION = f"https://{HOST}/{INDEXNOW_KEY}.txt"

# 70개 큐레이션 슬러그 목록
TAXONOMY_SLUGS = [
    "sleep", "self-esteem", "care", "animal", "family", "school", "loss", "courage",
    "friendship", "honesty", "sharing", "anger", "jealousy", "fear", "patience",
    "comfort", "happiness", "forgiveness", "social", "rules", "global", "jobs",
    "economy", "peace", "inclusion", "community", "media", "body", "nature",
    "eco", "science", "bugs", "space", "dinosaurs", "ocean", "weather", "ai",
    "math", "invention", "culture", "history", "folktale", "art", "theater",
    "world-history", "painting", "architecture", "holiday", "language", "writing",
    "adventure", "fantasy", "humor", "mystery", "imagination", "aviation", "cooking",
    "fashion", "vehicles", "sports", "physical-activity", "habit", "geography",
    "animal-encyclopedia", "future-imagination", "summer-vacation",
    "winter-vacation", "research-council", "caldecott"
]

curation_urls = [f"https://{HOST}/collections/curation/{slug}" for slug in TAXONOMY_SLUGS]
age_urls = [
    f"https://{HOST}/collections/age/0-3",
    f"https://{HOST}/collections/age/4-7",
    f"https://{HOST}/collections/age/8-12",
    f"https://{HOST}/collections/age/teen"
]
main_urls = [
    f"https://{HOST}/",
    f"https://{HOST}/caldecott",
    f"https://{HOST}/collections/research-council"
]

all_urls = list(dict.fromkeys(main_urls + age_urls + curation_urls))

print(f"총 제출 대상 URL 수: {len(all_urls)}개")

payload = {
    "host": HOST,
    "key": INDEXNOW_KEY,
    "keyLocation": KEY_LOCATION,
    "urlList": all_urls
}

# 1. IndexNow 표준 엔드포인트
endpoints = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow"
]

data = json.dumps(payload).encode('utf-8')
headers = {'Content-Type': 'application/json; charset=utf-8'}

for ep in endpoints:
    print(f"\nSubmitting to: {ep}...")
    req = urllib.request.Request(ep, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Status Code: {response.status} (성공: 200 또는 202 Accepted)")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

# 네이버 서치어드바이저 수동 입력용 우선순위 URL 파일 생성
with open("/Users/1004823/Desktop/kids_library/docs/naver_searchadvisor_urls.txt", "w", encoding="utf-8") as f:
    for url in all_urls:
        f.write(url + "\n")

print("\n✅ 네이버 서치어드바이저용 URL 목록 저장 완료: docs/naver_searchadvisor_urls.txt")
