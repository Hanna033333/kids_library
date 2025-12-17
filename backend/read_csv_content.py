import os

filename = "category_list.csv"
if not os.path.exists(filename):
    print(f"File not found: {filename}")
else:
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                content = f.read()
            print(f"--- Content ({enc}) ---")
            print(content)
            break
        except:
            continue
