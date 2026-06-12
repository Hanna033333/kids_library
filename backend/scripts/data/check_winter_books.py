from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('../frontend/.env.local')

sb = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))

# Check winter books
res = sb.table('childbook_items').select('id, title, pangyo_callno, is_hidden').eq('curation_tag', '겨울방학2026').order('id').execute()

print(f'📚 Total winter books in DB: {len(res.data)}')

# Filter non-hidden books with callno
visible_with_callno = [b for b in res.data if (b.get('is_hidden') is None or b.get('is_hidden') == False) and b.get('pangyo_callno')]

print(f'✅ Visible books with callno: {len(visible_with_callno)}')
print(f'❌ Hidden or without callno: {len(res.data) - len(visible_with_callno)}')

# Check specific winter books
test_titles = ['나는 오늘도 감정식당에 가요', '창덕궁에 불이 꺼지면', '가장 행복한 선물']
for t in test_titles:
    res_t = sb.table('childbook_items').select('id, title, pangyo_callno, is_hidden, curation_tag').eq('title', t).execute()
    print(f'\nBook [{t}]: {len(res_t.data)} items found')
    for b in res_t.data:
        print(f'  - [{b["id"]}] callno: {b.get("pangyo_callno")} - hidden: {b.get("is_hidden")} - tag: {b.get("curation_tag")}')



