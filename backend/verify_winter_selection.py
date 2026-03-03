from supabase_client import supabase

data = supabase.table('childbook_items').select('id, age, title').eq('curation_tag', '겨울방학2026').execute()
print(f'Total Winter Vacation books: {len(data.data)}')
for item in data.data:
    print(f'{item["age"]}: {item["title"]}')

