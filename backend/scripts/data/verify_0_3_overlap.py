from supabase_client import supabase

data = supabase.table('childbook_items').select('id, age, title').or_('age.eq.3세부터,age.eq.유아').limit(50).execute()
print(f'Sample 3세/유아 books:')
for item in data.data:
    print(f'{item["age"]}: {item["title"]}')

