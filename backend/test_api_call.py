import requests

resp = requests.post("http://127.0.0.1:8000/api/sync/callno")

print(resp.json())












