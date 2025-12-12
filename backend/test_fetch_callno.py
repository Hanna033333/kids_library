import time
start = time.time()
from library_api import fetch_callno

# 아무 ISBN 하나 넣어서 속도 측정
print(fetch_callno("9788997226423"))
print("걸린 시간:", time.time() - start)













