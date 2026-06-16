import sys
import os
import argparse
from pathlib import Path

# backend/scripts/data 디렉토리를 path에 추가
sys.path.append(str(Path(__file__).parent))

# backend/.env를 수동 로드
env_path = Path("/Users/1004823/Desktop/kids_library/backend/.env")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

from supabase_client import supabase

VALID_AI_TAGS = [
  "가족사랑", "모험", "인체", "판타지", "우리문화", "자연관찰", "잠자리", "사회성", "환경보호",
  "자존감", "전래동화", "계절", "생명존중", "다양성", "예술감성", "배려", "역사이야기", "용기",
  "감정조절", "우정", "과학원리", "상실", "정직", "곤충", "적응", "나눔", "우주", "분노조절",
  "규칙", "공룡", "슬픔", "다문화", "바다", "질투", "진로", "식물", "두려움", "경제", "날씨",
  "끈기", "의사소통", "코딩", "위로", "평화", "인공지능", "행복", "장애", "수학", "용서",
  "양성평등", "발명", "음악", "이웃", "연극", "세계역사", "미디어", "명화", "건축", "유머",
  "명절", "전통놀이", "추리", "한글", "글쓰기", "상상력", "하늘", "요리", "패션", "탈것",
  "스포츠", "괴물", "미래도시", "신체활동", "자연재해", "생활습관", "인문지리", "동물도감", "미래상상"
]

def main():
    parser = argparse.ArgumentParser(description="Reorder book curation tags by scarcity to satisfy 7-Book Rule.")
    parser.add_argument("--commit", action="store_true", help="Apply changes to Supabase database.")
    args = parser.parse_args()

    print("🚀 [태그 재배치 마이그레이션] 시작...")
    
    # 1. 모든 도서 정보 로드
    try:
        response = supabase.table("childbook_items")\
            .select("id, title, curation_tag, is_hidden")\
            .execute()
        books = response.data if hasattr(response, 'data') else response
        print(f"✅ DB 도서 총 {len(books)}권 로드 완료.")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return

    active_books = [b for b in books if b.get("is_hidden") is not True]
    print(f"Active (non-hidden) books count: {len(active_books)}")

    # 2. 전체 도서 내에서 각 태그의 등장 빈도(Scarcity) 계산
    # (모든 도서가 가진 태그 목록 중 빈도를 구함)
    global_tag_counts = {}
    for b in active_books:
        tag_str = b.get("curation_tag")
        if not tag_str:
            continue
        tags = [t.strip() for t in tag_str.split(",") if t.strip()]
        for t in tags:
            # '#' 기호가 있을 경우 제거해서 통일하여 빈도 계산
            cleaned = t[1:] if t.startswith("#") else t
            global_tag_counts[cleaned] = global_tag_counts.get(cleaned, 0) + 1

    print("\n--- 전체 DB 내 태그 빈도수 상위 10개 ---")
    sorted_global = sorted(global_tag_counts.items(), key=lambda x: x[1], reverse=True)
    for t, c in sorted_global[:10]:
        print(f"  {t}: {c}회")

    # 3. 동적 굶주림(Hunger) 기반 정렬 알고리즘
    # 각 태그가 첫 번째 태그로 채택된 횟수를 추적하며, 횟수가 적은 태그를 앞으로 당겨 배분합니다.
    print("\n🔄 동적 분배 태그 순서 재배치 시뮬레이션 중...")
    
    # 각 태그별 첫 번째 태그 누적 카운트
    first_tag_allocations = {tag: 0 for tag in VALID_AI_TAGS}
    
    # 특수 태그들은 카운트 관리에서 제외
    SPECIAL_TAGS = ['겨울방학2026', '어린이도서연구회', 'caldecott']
    for st in SPECIAL_TAGS:
        first_tag_allocations[st] = 999999

    updates_needed = []
    
    # 각 도서의 태그 중 allocation 카운트가 가장 적은 것을 앞으로 보냄
    # 루프 순서에 따라 결과가 다소 달라질 수 있으므로, 태그 개수가 적은 도서부터 처리하면 기회가 균등해짐
    # (선택의 여지가 적은 책을 먼저 처리하고, 태그가 많은 책은 나중에 남는 자리를 메움)
    def get_book_flexibility(b_data):
        t_str = b_data.get("curation_tag") or ""
        return len([t.strip() for t in t_str.split(",") if t.strip()])
    
    sorted_active_books = sorted(active_books, key=get_book_flexibility)

    for b in sorted_active_books:
        book_id = b.get("id")
        title = b.get("title")
        tag_str = b.get("curation_tag")
        if not tag_str:
            continue

        tags = [t.strip() for t in tag_str.split(",") if t.strip()]
        if not tags:
            continue

        # 태그별로 현재까지의 할당 카운트 구하기
        # 할당 카운트가 작은 순서대로 정렬하되, 특수 태그는 맨 뒤로
        def get_current_allocation(tag_name):
            cleaned = tag_name[1:] if tag_name.startswith("#") else tag_name
            if cleaned in SPECIAL_TAGS:
                return 999999
            return first_tag_allocations.get(cleaned, 9999)

        sorted_tags = sorted(tags, key=get_current_allocation)
        
        # 첫 번째 태그 확정 및 카운트 1 증가
        first = sorted_tags[0][1:] if sorted_tags[0].startswith("#") else sorted_tags[0]
        if first in first_tag_allocations:
            first_tag_allocations[first] += 1

        new_tag_str = ",".join(sorted_tags)
        if new_tag_str != tag_str:
            updates_needed.append((book_id, title, tag_str, new_tag_str))

    print(f"💡 정렬 변경이 필요한 도서 수: {len(updates_needed)}권 / {len(active_books)}권")

    # 4. 시뮬레이션 결과에 대한 7-Book Rule 검증
    violating_tags = []
    for tag, count in first_tag_allocations.items():
        if tag not in SPECIAL_TAGS and count < 7:
            violating_tags.append((tag, count))

    print("\n📊 === 재배치 후 7-Book Rule 검증 결과 ===")
    if not violating_tags:
        print("🎉 [성공] 모든 큐레이션 주제가 7권 이상을 만족합니다! 위반 항목 0개.")
    else:
        print(f"⚠️ [주의] 재배치 후에도 {len(violating_tags)}개 주제가 7권 미만입니다:")
        for tag, count in sorted(violating_tags, key=lambda x: x[1]):
            print(f"  - {tag}: {count}권")

    # 5. 실제 DB 적용
    if args.commit:
        print(f"\n💾 Supabase DB 업데이트 시작 (총 {len(updates_needed)}건)...")
        updated_count = 0
        for book_id, title, old_tags, new_tags in updates_needed:
            try:
                supabase.table("childbook_items")\
                    .update({"curation_tag": new_tags})\
                    .eq("id", book_id)\
                    .execute()
                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"  ⏳ {updated_count}권 완료...")
            except Exception as e:
                print(f"  ❌ [{book_id}] {title} 업데이트 실패: {e}")
        print(f"🎉 마이그레이션 적용 완료! 총 {updated_count}권의 도서 태그가 재배치되었습니다.")
    else:
        print("\nℹ️ Dry-run 모드입니다. 실제 DB에 반영하려면 스크립트 실행 시 --commit 플래그를 붙여주세요.")

if __name__ == "__main__":
    main()
