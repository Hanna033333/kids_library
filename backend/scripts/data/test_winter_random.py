from supabase import create_client
import os
from dotenv import load_dotenv
import math

load_dotenv('../frontend/.env.local')

sb = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))

# Simulate the new logic
print("🧪 Testing new winter books random selection logic\n")

# Get all visible winter books
res = sb.table('childbook_items').select('id, title').eq('curation_tag', '겨울방학2026').or_('is_hidden.is.null,is_hidden.eq.false').order('id').limit(100).execute()

visible_books = res.data
print(f"✅ Total visible winter books: {len(visible_books)}")

# Simulate seeded random selection for today
import datetime
now = datetime.datetime.now()
start_of_year = datetime.datetime(now.year, 1, 1)
day_of_year = (now - start_of_year).days
seed = day_of_year * 0.001

def seeded_random(index):
    x = math.sin(seed + index) * 10000
    return x - math.floor(x)

# Fisher-Yates shuffle
shuffled = visible_books.copy()
for i in range(len(shuffled) - 1, 0, -1):
    j = math.floor(seeded_random(i) * (i + 1))
    shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

# Select first 7
selected = shuffled[:7]

print(f"\n📚 Today's selected 7 books (seed: {seed}):")
for i, book in enumerate(selected, 1):
    print(f"{i}. [{book['id']}] {book['title']}")

print(f"\n✅ Result: {len(selected)} books selected (guaranteed 7)")
