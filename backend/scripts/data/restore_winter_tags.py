from supabase import create_client
import os
import sys
from dotenv import load_dotenv

# Load Env
possible_paths = [
    'frontend/.env.local',
    '../frontend/.env.local',
    './frontend/.env.local',
    'backend/.env',
    '.env'
]

env_path = None
for path in possible_paths:
    if os.path.exists(path):
        env_path = path
        break
        
# Force load backend/.env for Service Role Key
backend_env = 'backend/.env'
if os.path.exists(backend_env):
    load_dotenv(backend_env, override=True)
    print(f"ℹ️ Loaded backend env from {backend_env}")
elif os.path.exists('.env'):
    load_dotenv('.env', override=True)
    print("ℹ️ Loaded root env from .env")

sb_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
sb_key = os.getenv('SUPABASE_SERVICE_KEY')

if not sb_url or not sb_key:
    # Try next_public as fallback
    sb_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    sb_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    print("⚠️ WARNING: Using Anon Key. DB Update might fail due to RLS!")
else:
    print("ℹ️ Loaded SUPABASE_SERVICE_KEY. Updating with Service Role permission.")

if not sb_url or not sb_key:
    print("❌ Supabase credentials not found!")
    sys.exit(1)

sb = create_client(sb_url, sb_key)

WINTER_BOOKS = [
    {"title": "나는 오늘도 감정식당에 가요", "callno": "유 813.8-ㄹ434-11"},
    {"title": "창덕궁에 불이 꺼지면", "callno": "유 380.911-ㅇ475ㅊ-24"},
    {"title": "가장 행복한 선물", "callno": "818-ㄱ975ㅅ"},
    {"title": "(말해 볼까?) 예쁜 말 한마디", "callno": "유 199.4-ㅇ114ㅁ"},
    {"title": "힘내라, 힘!", "callno": "747.5-ㅇ614ㅎ"},
    {"title": "너 지도 볼 줄 알아?", "callno": "아 408-ㅅ194채-17"},
    {"title": "뉴욕 양말 탐정단", "callno": "아 808.9-ㅇ175ㅂ-2"},
    {"title": "책 요정 도도 : 도서관을 구해 줘!", "callno": "유 375.1-ㅍ15-9"},
    {"title": "불안이 사르르 사라지는 그림책 : 작은 일에도 걱정부터 앞서는 아이를 위한 마음 사용법", "callno": "아 813.8-ㅇ692ㅂ"},
    {"title": "바닷마을 호호책방", "callno": "아 813.8-ㄱ866ㅂ"},
    {"title": "전쟁과 나", "callno": "아 813.8-ㅇ591ㅈ"},
    {"title": "내 고양이 포", "callno": "아 833.8-ㅇ8255ㄴ"},
    {"title": "일곱 빛깔 감정 나라 : 내 안의 다채로운 감정과 만나는 곳", "callno": "아 813.8-ㄱ928기-1"},
    {"title": "엄마 규칙에 반대한다고?", "callno": "아 808.9-ㅇ965-47"},
    {"title": "쥐들 G들", "callno": "아 808.9-ㅇ176ㅂ-58"},
    {"title": "평양냉면을 좋아하게 될 줄이야!", "callno": "유 813.8-ㅁ374ㄴ-4"},
    {"title": "진실한 동물도감", "callno": "아 490-ㅊ752ㅈ=2"},
    {"title": "탐정 명아루 : 폐가 괴물 사건", "callno": "아 813.8-ㄷ52-2"},
    {"title": "너에게 사과하는 방법", "callno": "아 813.8-ㅇ977ㄴ"},
    {"title": "주게무의 여름", "callno": "아 808.9-ㄷ37ㄷ-15"},
    {"title": "찰랑찰랑 슬픔 하나", "callno": "아 813.8-ㅍ12ㅇ-22"},
    {"title": "여름에 내리는 비, 잠비", "callno": "아 808.9-ㅇ965ㅂ-116=2"}
]

print("🔄 1. 겨울방학 추천도서 Curation Tag 및 청구기호 복원 시작...")
restored_count = 0
for book in WINTER_BOOKS:
    # 1. 제목으로 책 찾기 (겨울방학 책들은 제목이 유니크함)
    res = sb.table('childbook_items').select('id, title, curation_tag, pangyo_callno, is_hidden').eq('title', book['title']).execute()
    if res.data:
        for item in res.data:
            # 업데이트
            update_data = {
                "curation_tag": "겨울방학2026",
                "pangyo_callno": book['callno'],
                "is_hidden": False
            }
            sb.table('childbook_items').update(update_data).eq('id', item['id']).execute()
            print(f"   ✅ 복원 완료: {book['title']} [ID: {item['id']}] -> tag: 겨울방학2026, callno: {book['callno']}, hidden: False")
            restored_count += 1
    else:
        print(f"   ❌ DB에서 도서를 찾을 수 없음: {book['title']}")

print(f"🎉 겨울방학 도서 총 {restored_count}개 항목 복원 및 업데이트 완료!")

print("\n🔄 2. 청구기호 없는 책 숨김 처리 시작...")
# 청구기호가 없거나 '없음'인 책들 중 is_hidden이 false/null인 것 숨기기
res_unowned = sb.table('childbook_items').select('id, title, pangyo_callno, is_hidden') \
    .or_('pangyo_callno.is.null,pangyo_callno.eq.없음') \
    .or_('is_hidden.is.null,is_hidden.eq.false') \
    .execute()

hidden_count = 0
if res_unowned.data:
    print(f"🔍 청구기호 없는 노출 가능 도서 {len(res_unowned.data)}개 발견.")
    for b in res_unowned.data:
        sb.table('childbook_items').update({"is_hidden": True}).eq('id', b['id']).execute()
        print(f"   🔒 숨김 처리 완료: {b['title']} [ID: {b['id']}] - callno: {b.get('pangyo_callno')}")
        hidden_count += 1
else:
    print("✅ 청구기호 없는 노출 도서 없음.")

print(f"🎉 청구기호 없는 도서 총 {hidden_count}개 숨김 처리 완료!")
