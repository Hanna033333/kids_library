from supabase_client import supabase
import sys

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Check total count
result_total = supabase.table('childbook_items').select('id', count='exact').execute()
total = result_total.count

# Check non-empty description count (approximate, just checking not equal to empty string)
result_desc = supabase.table('childbook_items').select('id', count='exact').neq('description', '').execute()
has_desc = result_desc.count

print(f"Total books: {total}")
print(f"Books with description (neq ''): {has_desc}")

# Sample descriptions
print("\nSample descriptions:")
result = supabase.table('childbook_items').select('title, description').neq('description', '').limit(5).execute()
for book in result.data:
    desc = book.get('description', '')
    if desc:
        print(f"- {book['title']}: {desc[:50]}...")
    else:
        print(f"- {book['title']}: (No description)")
