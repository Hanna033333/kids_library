"""
단계 1: 오매칭 첫 번째 태그 즉시 교체 스크립트
- 각 태그의 키워드가 도서 본문에 전혀 없는데 첫 번째 태그로 배정된 경우,
  해당 태그를 제거하고 두 번째 태그를 승격시킴.
- dry-run 모드: 변경 사항만 출력
- --commit 모드: 실제 DB 업데이트
"""
import sys
import os
import argparse
from pathlib import Path

# backend/.env 로드
env_path = Path("/Users/1004823/Desktop/kids_library/backend/.env")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

sys.path.append(str(Path("/Users/1004823/Desktop/kids_library/backend/scripts/data")))
from supabase_client import supabase

# populate_72_curations.py와 동일한 키워드 설정
THEMES_CONFIG = {
    "가족사랑": ["가족", "엄마", "아빠", "할머니", "할아버지", "동생", "형", "누나", "사랑"],
    "자존감": ["자존감", "나다움", "특별", "최고", "자신감"],
    "감정조절": ["감정", "마음", "화", "슬픔", "기쁨", "조절"],
    "잠자리": ["잠", "잠자리", "밤", "꿈", "잘 자", "달님"],
    "배려": ["배려", "양보", "나눔", "도움", "친구"],
    "생명존중": ["생명", "동물", "강아지", "고양이", "존중"],
    "상실": ["이별", "죽음", "기억", "슬픔", "떠나"],
    "적응": ["학교", "유치원", "어린이집", "입학", "등원", "적응"],
    "용기": ["용기", "겁", "두려움", "씩씩"],
    "우정": ["친구", "우정", "사이좋게", "약속"],
    "정직": ["거짓말", "정직", "진실", "비밀"],
    "나눔": ["선물", "나누", "양보", "욕심"],
    "분노조절": ["화", "짜증", "분노", "떼쓰"],
    "슬픔": ["눈물", "슬프", "위로", "울음"],
    "질투": ["질투", "샘", "욕심", "시샘"],
    "두려움": ["무서", "밤", "두려", "어둠"],
    "끈기": ["끝까지", "포기", "도전", "인내", "연습"],
    "위로": ["괜찮아", "위로", "토닥", "안아"],
    "행복": ["행복", "웃음", "기쁨", "감사"],
    "용서": ["잘못", "미안", "용서", "화해"],
    "사회성": ["사회성", "관계", "협동", "친구"],
    "다양성": ["다양", "차별", "다름", "세계", "편견"],
    "규칙": ["약속", "규칙", "질서", "법", "공공"],
    "다문화": ["다문화", "세계", "외국", "이주"],
    "진로": ["꿈", "일", "직업", "미래", "되고 싶"],
    "경제": ["돈", "은행", "저금", "소비", "가치"],
    "의사소통": ["말", "대화", "소통", "듣기", "이해"],
    "평화": ["평화", "전쟁", "화해", "싸움"],
    "장애": ["장애", "편견", "다름", "이해", "수어"],
    "양성평등": ["남자", "여자", "평등", "역할", "편견"],
    "이웃": ["이웃", "동네", "마을", "함께", "도움"],
    "미디어": ["스마트폰", "게임", "인터넷", "텔레비전", "미디어"],
    "인체": ["몸", "뼈", "피", "심장", "인체", "해부"],
    "자연관찰": ["자연", "나무", "숲", "꽃", "곤충"],
    "환경보호": ["환경", "지구", "쓰레기", "보호", "자연"],
    "과학원리": ["과학", "물리", "원리", "실험", "호기심"],
    "계절": ["봄", "여름", "가을", "겨울", "계절"],
    "곤충": ["곤충", "벌레", "나비", "개미", "벌"],
    "우주": ["우주", "별", "행성", "달", "태양"],
    "공룡": ["공룡", "티라노", "쥬라기", "화석"],
    "바다": ["바다", "물고기", "바닷속", "해양", "고래"],
    "식물": ["식물", "나무", "꽃", "씨앗", "풀"],
    "날씨": ["날씨", "비", "눈", "바람", "태풍", "구름"],
}

SPECIAL_TAGS = ['caldecott', '어린이도서연구회', '겨울방학2026', '여름방학2026', 'winter-vacation', 'summer-vacation', 'research-council']


def main():
    parser = argparse.ArgumentParser(description="Fix mismatched first tags.")
    parser.add_argument("--commit", action="store_true", help="Apply changes to DB.")
    args = parser.parse_args()

    print("=" * 70)
    print("🔧 [단계 1] 오매칭 첫 번째 태그 즉시 교체")
    print("=" * 70)

    try:
        response = supabase.table("childbook_items")\
            .select("id, title, description, keywords, curation_note, curation_tag, is_hidden")\
            .execute()
        all_books = response.data or []
        print(f"✅ DB 도서 {len(all_books)}권 로드 완료.")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return

    active_books = [b for b in all_books if not b.get('is_hidden')]
    print(f"Active 도서: {len(active_books)}권\n")

    updates = []
    for b in active_books:
        tag_str = b.get('curation_tag', '') or ''
        tags = [t.strip() for t in tag_str.split(',') if t.strip()]
        if len(tags) < 2:
            continue

        first_tag_raw = tags[0]
        first_tag = first_tag_raw.lstrip('#')

        if first_tag in SPECIAL_TAGS:
            continue
        if first_tag not in THEMES_CONFIG:
            continue

        keywords = THEMES_CONFIG[first_tag]
        title = b.get('title', '')
        desc = b.get('description', '') or ''
        keyw = b.get('keywords', '') or ''
        note = b.get('curation_note', '') or ''
        full_text = f"{title} {desc} {keyw} {note}"

        found = any(kw in full_text for kw in keywords)

        if not found:
            new_tags = tags[1:]
            new_tag_str = ",".join(new_tags)
            updates.append({
                "id": b['id'],
                "title": title,
                "old_first_tag": first_tag_raw,
                "old_tags": tag_str,
                "new_tags": new_tag_str,
                "new_first_tag": new_tags[0] if new_tags else "(없음)",
            })

    print(f"📊 교체 대상 도서: {len(updates)}권\n")

    if not updates:
        print("🎉 오매칭 첫 번째 태그가 없습니다!")
        return

    print("-" * 70)
    print(f"{'ID':<8} {'도서명':<30} {'기존 첫태그':<12} {'새 첫태그':<12}")
    print("-" * 70)
    for u in updates[:50]:
        title_short = u['title'][:28] + '..' if len(u['title']) > 28 else u['title']
        print(f"{u['id']:<8} {title_short:<30} {u['old_first_tag']:<12} → {u['new_first_tag']:<12}")
    if len(updates) > 50:
        print(f"  ... 외 {len(updates) - 50}건")

    removed_stats = {}
    for u in updates:
        tag = u['old_first_tag'].lstrip('#')
        removed_stats[tag] = removed_stats.get(tag, 0) + 1

    print(f"\n📈 태그별 제거 통계:")
    for tag, count in sorted(removed_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count}건 제거")

    if args.commit:
        print(f"\n💾 DB 업데이트 시작 (총 {len(updates)}건)...")
        success = 0
        for u in updates:
            try:
                supabase.table("childbook_items")\
                    .update({"curation_tag": u["new_tags"]})\
                    .eq("id", u["id"])\
                    .execute()
                success += 1
                if success % 20 == 0:
                    print(f"  ⏳ {success}/{len(updates)} 완료...")
            except Exception as e:
                print(f"  ❌ [{u['id']}] {u['title']} 업데이트 실패: {e}")
        print(f"\n🎉 단계 1 완료! {success}/{len(updates)}건 첫 번째 태그 교체 적용됨.")
    else:
        print(f"\nℹ️ Dry-run 모드입니다. 실제 적용하려면: --commit")


if __name__ == "__main__":
    main()
