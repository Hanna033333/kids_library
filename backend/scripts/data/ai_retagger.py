"""
단계 3: Gemini AI 의미 기반 전체 재태깅 스크립트
- 기존 키워드 규칙 기반 태깅을 AI 의미 분석 기반으로 전환
- 모드:
  --mode risky: 위험도 높은 태그(분노조절, 위로, 다양성 등) 도서만 재태깅
  --mode all: 전체 도서 재태깅 (confidence_score 기준 필터 가능)
  --mode tag --target 태그명: 특정 태그만 재태깅
- 특수 태그(caldecott 등) 보존
"""
import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Set

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

import google.generativeai as genai
from supabase_client import supabase

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
BATCH_SIZE = 7  # 79개 태그 프롬프트가 길어서 7권씩

# 특수 태그 (AI 재태깅에서 보존)
SPECIAL_TAGS = {'caldecott', '어린이도서연구회', '겨울방학2026', '여름방학2026',
                'winter-vacation', 'summer-vacation', 'research-council'}

# 위험도 높은 태그 (--mode risky 대상)
RISKY_TAGS = [
    "분노조절", "위로", "다양성", "다문화", "진로", "사회성", "장애",
    "감정조절", "두려움", "배려", "정직", "우정", "용서", "자연관찰",
    "자존감", "잠자리", "양성평등", "적응", "상실", "인체", "과학원리"
]

# 79개 전체 택소노미 (taxonomy.py 기준)
ALL_TAGS = [
    # 감성/정서 발달
    "잠자리", "감정조절", "자존감", "배려", "생명존중", "가족사랑", "적응", "상실",
    "용기", "우정", "정직", "나눔", "분노조절", "슬픔", "질투", "두려움",
    "끈기", "위로", "행복", "용서",
    # 사회/관계
    "사회성", "다양성", "규칙", "다문화", "진로", "경제", "의사소통", "평화",
    "장애", "양성평등", "이웃", "미디어",
    # 과학/자연
    "인체", "자연관찰", "환경보호", "과학원리", "계절", "곤충", "우주", "공룡",
    "바다", "식물", "날씨", "코딩", "인공지능", "수학", "발명",
    # 문화/예술
    "우리문화", "역사이야기", "전래동화", "예술감성", "음악", "연극", "세계역사",
    "명화", "건축", "명절", "전통놀이", "한글", "글쓰기",
    # 이야기/장르
    "모험", "판타지", "유머", "추리", "상상력", "하늘", "요리", "패션",
    "탈것", "스포츠", "괴물", "미래도시", "신체활동", "자연재해", "생활습관",
    "인문지리", "동물도감", "미래상상"
]


def build_retagging_prompt(books: List[Dict]) -> str:
    """79개 태그 기반 AI 재태깅 프롬프트 생성"""

    tag_list_str = ", ".join(ALL_TAGS)

    books_str = ""
    for i, b in enumerate(books):
        desc = (b.get('description') or '')[:500]
        books_str += f"[{i+1}] ID: {b['id']}, 제목: {b['title']}, 작가: {b.get('author', '미상')}\n"
        books_str += f"내용: {desc}\n\n"

    prompt = f"""당신은 20년 경력의 베테랑 어린이 도서 사서이자, 부모들의 마음을 읽는 육아 전문가입니다.

제공된 {len(books)}권의 도서를 깊이 있게 분석하여, 도서의 **핵심 주제와 메시지**에 가장 정확하게 부합하는 태그를 선택해주세요.

[사용 가능한 태그 목록 (79개)]
{tag_list_str}

[중요한 태깅 규칙]
1. 각 도서에 1~3개 태그만 선택하세요. 핵심 메시지와 정확히 일치하는 것만 고르세요.
2. 키워드 단순 매칭이 아닌 **도서의 실제 주제와 교훈**을 기준으로 판단하세요.
3. 반드시 위 목록에 있는 태그만 사용하세요.
4. 태그 앞에 '#'을 붙이지 마세요.
5. confidence_score는 태그 매칭의 정확도를 0~100으로 평가하세요.

[오매칭 방지 예시 — 이런 실수를 하지 마세요]
- "출생의 비밀" 이야기 → "정직" 태그 ❌ → 올바른 태그: "생명존중", "가족사랑"
- "일어나서 학교에 갔다" → "진로" 태그 ❌ → 올바른 태그: "적응"
- "화가 난 것처럼 빨간 얼굴" → "분노조절" 태그 ❌ (색상 묘사일 뿐)
- "비밀의 문을 열었다" → "정직" 태그 ❌ → 올바른 태그: "모험", "판타지"
- "친구와 놀았다" → 이것만으로 "우정" 태그 ❌ (우정이 핵심 주제가 아닌 한)

[출력 형식 (JSON 배열로만 응답)]
[
  {{
    "id": 123,
    "tags": ["잠자리", "가족사랑"],
    "confidence_score": 95
  }},
  ...
]

[분석 대상 도서]
{books_str}"""
    return prompt


def extract_special_tags(tag_str: str) -> List[str]:
    """기존 태그에서 특수 태그만 추출"""
    tags = [t.strip() for t in tag_str.split(',') if t.strip()]
    return [t for t in tags if t.lstrip('#') in SPECIAL_TAGS]


def fetch_risky_books() -> List[Dict]:
    """위험도 높은 태그가 첫 번째 태그인 도서를 가져옴 (전체 조회 후 Python 필터링)"""
    try:
        response = supabase.table("childbook_items")\
            .select("id, title, author, description, curation_tag, curation_note, confidence_score, is_hidden")\
            .or_("is_hidden.is.null,is_hidden.eq.false")\
            .execute()
        all_books = response.data or []
    except Exception as e:
        print(f"❌ 전체 도서 조회 실패: {e}")
        return []

    # 위험 태그 set (# 접두사 포함/미포함 모두 체크)
    risky_set = set(RISKY_TAGS) | {f"#{t}" for t in RISKY_TAGS}

    all_risky = []
    seen_ids: Set[int] = set()

    for b in all_books:
        tag_str = b.get('curation_tag', '') or ''
        tags = [t.strip() for t in tag_str.split(',') if t.strip()]
        if not tags:
            continue
        first_tag = tags[0]
        # 첫 번째 태그만 체크 (정밀 매칭)
        if first_tag in risky_set:
            if b['id'] not in seen_ids:
                seen_ids.add(b['id'])
                all_risky.append(b)

    return all_risky


def fetch_all_books(min_score: int = 0, max_score: int = 100) -> List[Dict]:
    """전체 도서 또는 신뢰도 필터링된 도서를 가져옴"""
    try:
        response = supabase.table("childbook_items")\
            .select("id, title, author, description, curation_tag, curation_note, confidence_score, is_hidden")\
            .or_("is_hidden.is.null,is_hidden.eq.false")\
            .execute()
        books = response.data or []
        if max_score < 100:
            books = [b for b in books if (b.get('confidence_score') or 0) <= max_score]
        if min_score > 0:
            books = [b for b in books if (b.get('confidence_score') or 0) >= min_score]
        return books
    except Exception as e:
        print(f"❌ 전체 도서 조회 실패: {e}")
        return []


def run_ai_retagging(books: List[Dict], dry_run: bool = False):
    """AI 재태깅 실행"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)

    total = len(books)
    success = 0
    failed = 0
    skipped = 0

    print(f"\n{'='*70}")
    print(f"🤖 AI 재태깅 시작 — 총 {total}권, {BATCH_SIZE}권씩 배치 처리")
    print(f"{'='*70}\n")

    for i in range(0, total, BATCH_SIZE):
        chunk = books[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"[Batch {batch_num}/{total_batches}] {len(chunk)}권 처리 중...")

        # description이 없는 도서는 건너뜀
        valid_chunk = [b for b in chunk if b.get('description')]
        if not valid_chunk:
            print(f"  ⚠️ description 없는 도서만 있어 건너뜀")
            skipped += len(chunk)
            continue

        prompt = build_retagging_prompt(valid_chunk)

        try:
            if i > 0:
                time.sleep(2)  # Rate limit 방지

            response = model.generate_content(prompt)
            text = response.text.strip()

            # JSON 파싱
            if "```json" in text:
                start_idx = text.find("```json") + 7
                end_idx = text.rfind("```")
                text = text[start_idx:end_idx].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()

            results = json.loads(text)

            for res in results:
                book_id = res['id']
                new_tags = res.get('tags', [])
                score = res.get('confidence_score', 0)

                if not new_tags:
                    skipped += 1
                    continue

                # 기존 특수 태그 보존
                original_book = next((b for b in chunk if b['id'] == book_id), None)
                if original_book:
                    special = extract_special_tags(original_book.get('curation_tag', ''))
                else:
                    special = []

                # 새 태그 조합: AI 태그 + 보존된 특수 태그
                final_tags = new_tags + [t for t in special if t not in new_tags]
                final_tag_str = ",".join(final_tags)

                old_tags = original_book.get('curation_tag', '') if original_book else ''
                title = original_book.get('title', '') if original_book else ''

                if dry_run:
                    print(f"  📝 [{book_id}] {title[:30]}")
                    print(f"     기존: {old_tags[:60]}")
                    print(f"     새로: {final_tag_str} (score: {score})")
                else:
                    try:
                        supabase.table("childbook_items").update({
                            "curation_tag": final_tag_str,
                            "confidence_score": score
                        }).eq("id", book_id).execute()
                        success += 1
                    except Exception as e:
                        print(f"  ❌ [{book_id}] DB 업데이트 실패: {e}")
                        failed += 1

            if not dry_run and (batch_num % 5 == 0 or batch_num == total_batches):
                print(f"  ✅ 진행: {min(i + BATCH_SIZE, total)}/{total}권 완료 (성공: {success}, 실패: {failed})")

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON 파싱 실패 (Batch {batch_num}): {e}")
            if 'text' in dir(response):
                print(f"     Raw response: {response.text[:200]}")
            failed += len(valid_chunk)
        except Exception as e:
            print(f"  ❌ API 에러 (Batch {batch_num}): {e}")
            failed += len(valid_chunk)
            time.sleep(5)  # 에러 시 대기 후 계속

    print(f"\n{'='*70}")
    print(f"🎉 AI 재태깅 완료!")
    print(f"  총 {total}권 | 성공: {success}건 | 실패: {failed}건 | 건너뜀: {skipped}건")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Gemini AI 의미 기반 도서 재태깅")
    parser.add_argument("--mode", choices=["risky", "all", "tag"], default="risky",
                        help="risky: 위험 태그만, all: 전체, tag: 특정 태그")
    parser.add_argument("--target", type=str, help="--mode tag일 때 대상 태그명")
    parser.add_argument("--max-score", type=int, default=100,
                        help="이 점수 이하인 도서만 재태깅 (default: 100 = 전체)")
    parser.add_argument("--dry-run", action="store_true", help="DB 수정 없이 결과만 출력")
    parser.add_argument("--exclude-ids", type=str, default="",
                        help="제외할 도서 ID 목록 (쉼표 구분)")
    args = parser.parse_args()

    exclude_ids = set()
    if args.exclude_ids:
        exclude_ids = {int(x.strip()) for x in args.exclude_ids.split(',') if x.strip()}

    print(f"🚀 AI 재태깅 모드: {args.mode}")

    if args.mode == "risky":
        print(f"📌 위험 태그 대상: {', '.join(RISKY_TAGS)}")
        books = fetch_risky_books()
    elif args.mode == "all":
        print(f"📌 전체 도서 대상 (max_score: {args.max_score})")
        books = fetch_all_books(max_score=args.max_score)
    elif args.mode == "tag":
        if not args.target:
            print("❌ --mode tag를 사용할 때는 --target 태그명을 지정하세요.")
            return
        print(f"📌 특정 태그 대상: {args.target}")
        target_tag = args.target
        target_set = {target_tag, f"#{target_tag}"}
        try:
            response = supabase.table("childbook_items")\
                .select("id, title, author, description, curation_tag, curation_note, confidence_score, is_hidden")\
                .or_("is_hidden.is.null,is_hidden.eq.false")\
                .execute()
            all_books = response.data or []
            books = []
            seen: Set[int] = set()
            for b in all_books:
                tag_str = b.get('curation_tag', '') or ''
                first = (tag_str.split(',')[0].strip()) if tag_str else ''
                if first in target_set and b['id'] not in seen:
                    seen.add(b['id'])
                    books.append(b)
        except Exception as e:
            print(f"❌ 조회 실패: {e}")
            return

    if exclude_ids:
        books = [b for b in books if b['id'] not in exclude_ids]

    print(f"📚 대상 도서: {len(books)}권")

    if not books:
        print("대상 도서가 없습니다.")
        return

    run_ai_retagging(books, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
