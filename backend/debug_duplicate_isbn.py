from supabase_client import supabase

# Conflict ISBN from error
isbn = '9788949113692'
title_target = '눈보라'

print(f"Checking for ISBN: {isbn}")
res_isbn = supabase.table("childbook_items").select("*").eq("isbn", isbn).execute()
for item in res_isbn.data:
    print(f"Found Item with ISBN {isbn}: ID={item['id']}, Title='{item['title']}', Tag='{item['curation_tag']}'")

print(f"\nChecking for Title: {title_target}")
res_title = supabase.table("childbook_items").select("*").eq("title", title_target).execute()
for item in res_title.data:
    print(f"Found Item with Title {title_target}: ID={item['id']}, Title='{item['title']}', ISBN='{item['isbn']}', Tag='{item['curation_tag']}'")
