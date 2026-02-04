
import os
import math
import sys
from datetime import datetime
from supabase_client import supabase

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def seeded_random(seed, index):
    # Matches JS: Math.sin(seed + index) * 10000; return x - Math.floor(x)
    x = math.sin(seed + index) * 10000
    return x - math.floor(x)

def get_winter_books_for_date(target_date):
    # Logic from home-api.ts:
    # const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (24 * 60 * 60 * 1000))
    # const seed = dayOfYear * 0.001
    
    start_of_year = datetime(target_date.year, 1, 1)
    # JS getTime() returns milliseconds. 
    # Python timestamp is seconds.
    # Note: JS 'new Date(year, 0, 1)' is Jan 1st 00:00:00 local time usually, but in server environment might be UTC.
    # Checkjari seems to run on Vercel (UTC) or similar? 
    # Let's assume UTC or standard behavior. The difference between now and Jan 1st.
    
    diff = target_date - start_of_year
    day_of_year = diff.days # This matches Math.floor(diff_ms / day_ms) approximately
    
    # In JS: (now - Jan 1) includes time. 
    # Math.floor(...) means effectively just the day count from Jan 1.
    # Jan 1 is day 0.
    
    seed = day_of_year * 0.001
    
    print(f"\n📅 Analysis for Date: {target_date.strftime('%Y-%m-%d')} (Day Of Year: {day_of_year})")
    print(f"   Seed: {seed}")

    # Fetch books
    response = supabase.table('childbook_items') \
        .select('id, title') \
        .eq('curation_tag', '겨울방학2026') \
        .or_('is_hidden.is.null,is_hidden.eq.false') \
        .order('id') \
        .limit(100) \
        .execute()
        
    books = response.data
    if not books:
        print("   ❌ No books found.")
        return []

    # Shuffle
    # JS:
    # for (let i = shuffled.length - 1; i > 0; i--) {
    #    const j = Math.floor(seededRandom(i) * (i + 1))
    #    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    # }
    
    shuffled = books.copy()
    n = len(shuffled)
    for i in range(n - 1, 0, -1):
        # Pass 'i' as index to seeded_random, same as JS: seededRandom(i)
        rand_val = seeded_random(seed, i) 
        j = math.floor(rand_val * (i + 1))
        
        # Swap
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

    selected = shuffled[:7]
    return selected

def check_book_exposure():
    # Check last 7 days
    from datetime import timedelta
    today = datetime.now()
    dates = [(today - timedelta(days=i)) for i in range(7)]
    dates.reverse() # Oldest first
    
    print(f"\n{'='*50}")
    print(f"🕵️‍♂️ Daily #1 Book Check (Last 7 Days)")
    print(f"{'='*50}")
    
    with open("backend/verification_result_weekly.txt", "w", encoding="utf-8") as f:
        f.write("# Daily #1 Book Report\n\n")
        
        for d in dates:
            books = get_winter_books_for_date(d)
            if books:
                first_book = books[0]
                date_str = d.strftime('%Y-%m-%d')
                print(f"📅 {date_str}: [#{first_book['id']}] {first_book['title']}")
                f.write(f"- {date_str}: [#{first_book['id']}] {first_book['title']}\n")
            else:
                print(f"📅 {d.strftime('%Y-%m-%d')}: No data")

if __name__ == "__main__":
    check_book_exposure()
