"""
임베딩 유사도 기반 태그 순서 재정렬 스크립트
- Google text-embedding-004 모델 사용
- 각 책의 내용(제목+설명)과 각 태그 설명 간의 코사인 유사도 계산
- 유사도가 높은 태그 = 내용에 가장 적합한 태그 → 첫 번째(primary)로 배치
- Gemini 재실행 없이 기존 태그 세트의 순서만 재정렬
- 특수 태그(caldecott 등)는 항상 마지막에 보존
- --commit 없이 실행 시 dry-run (변경 예정 목록만 출력)
"""
import os
import sys
import argparse
import time
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional

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

import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

EMBED_MODEL = "models/gemini-embedding-2"  # text-embedding-004 후속 모델

SPECIAL_TAGS = {
    'caldecott', '어린이도서연구회', '겨울방학2026', '여름방학2026',
    'winter-vacation', 'summer-vacation', 'research-council'
}

# ─────────────────────────────────────────────────────────────────────────────
# 79개 태그 풍부한 설명
# 유사 태그 간 구분력을 높이기 위해 핵심 특징을 명확히 기술
# ─────────────────────────────────────────────────────────────────────────────
TAG_DESCRIPTIONS: Dict[str, str] = {
    # 감성/정서 발달
    "잠자리":   "잠자리 루틴, 잠자리 의식, 자장가, 달님, 잠드는 시간에 관한 이야기. 잘 자라는 내용이나 밤 루틴의 그림책.",
    "감정조절": "다양한 감정(슬픔, 기쁨, 두려움)을 인식하고 이름 붙이며 건강하게 표현하고 조절하는 방법. 감정 다스리기, 마음 표현.",
    "자존감":   "나 자신을 있는 그대로 사랑하고 자신감을 키우는 이야기. 나다움, 특별한 나, 나를 믿기, 있는 그대로의 내가 충분함.",
    "배려":     "다른 사람의 마음을 헤아리고 도와주며 나누는 따뜻한 마음. 친구와 나누고 양보하기.",
    "생명존중": "동물, 식물 등 모든 생명을 소중히 여기고 돌보는 이야기. 반려동물, 자연 속 작은 생명.",
    "가족사랑": "엄마, 아빠, 할머니, 할아버지, 형제자매 등 가족 간의 사랑과 유대를 따뜻하게 그린 이야기.",
    "적응":     "새로운 환경에 적응하는 이야기. 유치원 첫 등원, 학교 입학, 이사, 새 동생, 새로운 시작과 변화.",
    "상실":     "사랑하는 사람이나 반려동물과의 이별, 죽음, 소중한 것을 잃는 슬픔과 기억을 다루는 이야기.",
    "용기":     "무섭고 두려운 상황에서도 씩씩하게 도전하고 극복하는 용기. 겁쟁이가 용감해지는 이야기.",
    "우정":     "친구와의 우정, 진정한 친구의 의미, 함께 도우며 이어지는 우정 이야기.",
    "정직":     "거짓말하지 않고 솔직하고 진실하게 말하며 양심을 지키는 이야기. 솔직함의 중요성.",
    "나눔":     "가진 것을 나누고 양보하며 욕심을 버리고 함께 행복해지는 따뜻한 나눔의 가치.",
    "분노조절": "화, 짜증, 분노, 떼쓰기 등 격한 감정을 다스리는 이야기. 화를 올바르게 표현하고 조절하는 방법. 버럭하지 않기.",
    "슬픔":     "눈물, 슬픔, 상처받은 마음을 위로받고 다독이는 감성적인 이야기. 슬픔을 표현하고 나누기.",
    "질투":     "질투심, 샘, 시기의 감정을 다루며 욕심 없이 지내는 방법을 배우는 이야기.",
    "두려움":   "어둠, 무서운 것, 낯선 것에 대한 두려움을 이겨내는 이야기. 밤의 공포, 겁 극복.",
    "끈기":     "포기하지 않고 끝까지 도전하며 연습과 인내로 목표를 이루는 이야기. 꾸준히 노력하기.",
    "위로":     "힘든 마음을 안아주고 괜찮다고 토닥여주는 따뜻한 위로와 공감의 이야기.",
    "행복":     "작은 것에서 행복을 찾고 웃음과 감사로 가득한 즐거운 일상 이야기.",
    "용서":     "잘못을 인정하고 미안하다 말하며 화해하고 용서하는 이야기. 화해의 소중함.",
    # 사회/관계
    "사회성":   "여럿이 함께 어울리고 협동하며 사회적 관계와 공동체 생활을 배우는 이야기.",
    "다양성":   "다름을 인정하고 차별 없이 모두를 존중하는 이야기. 편견 없이 다양한 사람들을 받아들이기.",
    "규칙":     "공공질서, 약속, 규칙을 지키는 중요성을 배우는 이야기. 질서와 규율.",
    "다문화":   "다양한 나라와 문화, 외국인 친구, 이주 가족, 혼혈 가족의 이야기.",
    "진로":     "장래희망, 직업, 되고 싶은 꿈을 꾸며 미래를 상상하는 이야기. 어른이 되면 무엇이 될까.",
    "경제":     "돈, 저금, 소비, 가치, 은행 등 경제 개념을 어린이 눈높이로 다루는 이야기.",
    "의사소통": "대화하고 경청하며 자신의 생각을 올바르게 표현하는 소통의 중요성을 다루는 이야기.",
    "평화":     "싸움 없이 평화롭게 지내기, 전쟁의 비극, 화해와 공존을 다루는 이야기.",
    "장애":     "신체적 또는 발달 장애를 가진 인물을 이해하고 공감하는 이야기. 수어, 휠체어, 점자, 장애 친구.",
    "양성평등": "남녀 역할 고정관념 없이 평등하게 지내는 이야기. 성 역할 편견 극복.",
    "이웃":     "이웃, 동네, 마을 공동체 안에서 함께 도와가며 사는 이야기.",
    "미디어":   "스마트폰, 인터넷, 게임, 텔레비전 등 미디어를 올바르게 사용하는 이야기.",
    # 과학/자연
    "인체":     "우리 몸, 뼈, 심장, 피, 소화기관 등 인체 구조와 기능을 탐구하는 과학 그림책.",
    "자연관찰": "숲, 나무, 꽃, 곤충, 계절의 동식물 등 자연 현상을 관찰하고 탐구하는 이야기.",
    "환경보호": "지구 환경 오염, 기후 위기, 쓰레기 줄이기, 재활용, 지구를 지키자는 이야기.",
    "과학원리": "물리, 화학, 생물 등 과학적 원리와 실험을 호기심 있게 탐구하는 이야기.",
    "계절":     "봄, 여름, 가을, 겨울 사계절의 변화와 날씨, 자연의 아름다움을 담은 이야기.",
    "곤충":     "나비, 개미, 벌, 메뚜기, 딱정벌레 등 곤충의 생태와 생활을 관찰하는 이야기.",
    "우주":     "별, 달, 행성, 태양, 우주 탐험, 우주비행사를 주제로 한 과학 이야기.",
    "공룡":     "공룡의 종류, 화석, 쥐라기 시대, 티라노사우루스를 탐구하는 이야기.",
    "바다":     "바닷속 세계, 물고기, 고래, 문어, 해양 생물을 탐구하는 이야기.",
    "식물":     "꽃, 나무, 씨앗, 풀이 자라는 과정과 식물의 생태를 다루는 이야기.",
    "날씨":     "비, 눈, 바람, 태풍, 구름, 무지개 등 날씨 현상과 기상을 다루는 이야기.",
    "코딩":     "컴퓨터 프로그래밍, 알고리즘, 코딩의 기초 개념을 배우는 이야기.",
    "인공지능": "인공지능, 로봇, 미래 기술, 기계와 인간의 관계를 어린이 눈높이로 소개하는 이야기.",
    "수학":     "숫자, 도형, 계산, 측정, 패턴 등 수학 개념을 재미있게 배우는 이야기.",
    "발명":     "발명가, 창의적 발상, 새로운 도구를 만들어내는 이야기.",
    # 문화/예술
    "우리문화": "한국의 전통문화, 명절, 풍습, 우리 고유의 생활방식을 담은 이야기.",
    "역사이야기":"역사적 사건이나 인물을 통해 역사를 배우는 이야기 책.",
    "전래동화": "우리나라 전통 설화, 옛이야기, 민담, 신화를 담은 그림책.",
    "예술감성": "그림, 미술, 예술 작품, 화가를 통해 감성과 창의력을 키우는 이야기.",
    "음악":     "노래, 악기, 음악가, 연주를 주제로 한 이야기.",
    "연극":     "연극, 공연, 무대 위의 이야기, 역할놀이를 다루는 이야기.",
    "세계역사": "세계 각국의 역사적 사건과 인물을 탐구하는 이야기.",
    "명화":     "세계적인 미술 작품과 화가를 소개하는 이야기.",
    "건축":     "집, 건물, 건축물과 건축가를 이야기하는 책.",
    "명절":     "설날, 추석 등 한국 명절의 풍습과 의미를 담은 이야기.",
    "전통놀이": "제기차기, 윷놀이, 팽이치기 등 한국 전통 놀이를 소개하는 이야기.",
    "한글":     "한글의 창제와 우리 글의 아름다움, 자음과 모음을 배우는 이야기.",
    "글쓰기":   "일기, 편지, 이야기 만들기 등 글쓰기의 즐거움을 다루는 이야기.",
    # 이야기/장르
    "모험":     "낯선 세계로 떠나는 흥미진진한 탐험과 여정, 퀘스트를 담은 이야기.",
    "판타지":   "마법, 상상의 나라, 비현실적 세계관, 요정, 마법사를 가진 환상적인 이야기.",
    "유머":     "웃기고 재치 있는 상황과 말장난, 엉뚱한 설정으로 웃음을 주는 이야기.",
    "추리":     "수수께끼, 미스터리, 사건을 해결하는 탐정 이야기.",
    "상상력":   "엉뚱한 상상, 독창적 아이디어, 현실을 뛰어넘는 창의적 발상을 다루는 이야기.",
    "하늘":     "하늘, 구름, 바람, 비행, 날아오르기를 꿈꾸는 이야기.",
    "요리":     "음식 만들기, 요리, 먹는 즐거움, 맛있는 음식을 담은 이야기.",
    "패션":     "옷, 패션, 스타일, 의상을 주제로 한 이야기.",
    "탈것":     "자동차, 기차, 비행기, 배 등 다양한 탈것을 소개하는 이야기.",
    "스포츠":   "운동, 경기, 스포츠 정신, 팀워크를 다루는 이야기.",
    "괴물":     "괴물, 무서운 존재와 친해지거나 극복하는 이야기.",
    "미래도시": "미래 사회, 첨단 도시, 스마트 시티를 배경으로 한 이야기.",
    "신체활동": "몸을 움직이고 뛰어노는 신체 활동의 즐거움, 놀이와 운동.",
    "자연재해": "지진, 홍수, 화산, 태풍 등 자연재해를 다루는 이야기.",
    "생활습관": "양치질, 손 씻기, 규칙적인 생활 습관, 건강한 일상 루틴을 익히는 이야기.",
    "인문지리": "지도, 나라, 도시, 지형, 세계 각지 사람들의 생활을 다루는 이야기.",
    "동물도감": "다양한 동물의 생태와 특징을 백과사전식으로 소개하는 이야기.",
    "미래상상": "미래에 어떤 세상이 될지 상상하는 이야기.",
}


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """코사인 유사도 계산 (numpy 없이)"""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def embed_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """텍스트 배열 임베딩 (배치). 실패 시 None 반환."""
    try:
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=texts,
            task_type="SEMANTIC_SIMILARITY",
        )
        embs = result['embedding']
        # 단일 텍스트 입력 시 list of floats 반환 → 래핑
        if texts and isinstance(embs[0], float):
            return [embs]
        return embs
    except Exception as e:
        print(f"  ⚠️ 배치 임베딩 실패 ({len(texts)}개): {e}")
        return [None] * len(texts)


def main():
    parser = argparse.ArgumentParser(description="임베딩 유사도 기반 태그 순서 재정렬")
    parser.add_argument("--commit", action="store_true",
                        help="실제 DB 업데이트 (기본: dry-run)")
    parser.add_argument("--limit", type=int, default=None,
                        help="처리할 도서 수 제한 (테스트 시 사용)")
    args = parser.parse_args()

    print("=" * 70)
    print("🔢 임베딩 유사도 기반 태그 순서 재정렬 (Hybrid 방식)")
    print("   Gemini text-embedding-004 | 코사인 유사도 | 특수 태그 보존")
    print("=" * 70)

    # ── 1. DB 로드 ──────────────────────────────────────────────────────────
    print("\n📚 DB 도서 로드 중...")
    response = supabase.table("childbook_items") \
        .select("id, title, description, curation_tag, is_hidden") \
        .or_("is_hidden.is.null,is_hidden.eq.false") \
        .execute()
    all_books = response.data or []

    def has_two_or_more_normal_tags(book: Dict) -> bool:
        tag_str = book.get('curation_tag', '') or ''
        normal = [t for t in tag_str.split(',')
                  if t.strip() and t.strip().lstrip('#') not in SPECIAL_TAGS]
        return len(normal) >= 2

    target_books = [b for b in all_books if has_two_or_more_normal_tags(b)]
    if args.limit:
        target_books = target_books[:args.limit]

    print(f"✅ 전체 활성 도서: {len(all_books)}권")
    print(f"✅ 재정렬 대상 (일반 태그 2개 이상): {len(target_books)}권")

    # ── 2. 태그 임베딩 사전 계산 ─────────────────────────────────────────────
    print(f"\n🔢 태그 임베딩 계산 중 ({len(TAG_DESCRIPTIONS)}개)...")
    tag_names = list(TAG_DESCRIPTIONS.keys())
    tag_texts = [f"{name}: {desc}" for name, desc in TAG_DESCRIPTIONS.items()]

    tag_embeddings: Dict[str, List[float]] = {}
    BATCH = 20  # gemini-embedding-2 배치 사이즈
    for i in range(0, len(tag_texts), BATCH):
        names_chunk = tag_names[i:i + BATCH]
        texts_chunk = tag_texts[i:i + BATCH]
        embs = embed_batch(texts_chunk)
        for name, emb in zip(names_chunk, embs):
            if emb is not None:
                tag_embeddings[name] = emb
        time.sleep(0.3)

    print(f"✅ {len(tag_embeddings)}/{len(TAG_DESCRIPTIONS)}개 태그 임베딩 완료")

    # ── 3. 도서별 처리 ───────────────────────────────────────────────────────
    print(f"\n🔄 도서 태그 순서 재정렬 중...")
    updates = []
    error_count = 0
    BOOK_BATCH = 20

    for batch_start in range(0, len(target_books), BOOK_BATCH):
        batch = target_books[batch_start:batch_start + BOOK_BATCH]

        # 도서 텍스트: 제목 + 설명 앞 600자
        book_texts = []
        for b in batch:
            title = b.get('title', '')
            desc = (b.get('description') or '')[:600]
            book_texts.append(f"{title}. {desc}")

        book_embs = embed_batch(book_texts)
        time.sleep(0.5)

        for book, book_emb in zip(batch, book_embs):
            if book_emb is None:
                error_count += 1
                continue

            tag_str = book.get('curation_tag', '') or ''
            all_tags = [t.strip() for t in tag_str.split(',') if t.strip()]

            # 특수 태그 / 일반 태그 분리
            special_tags = [t for t in all_tags if t.lstrip('#') in SPECIAL_TAGS]
            normal_tags  = [t for t in all_tags if t.lstrip('#') not in SPECIAL_TAGS]

            if len(normal_tags) < 2:
                continue

            # 각 일반 태그와 책 내용 간 코사인 유사도 계산
            scored: List[Tuple[str, float]] = []
            for tag in normal_tags:
                clean = tag.lstrip('#')
                if clean in tag_embeddings:
                    sim = cosine_similarity(book_emb, tag_embeddings[clean])
                else:
                    sim = 0.0  # 사전에 없는 태그는 최하위
                scored.append((tag, sim))

            # 유사도 내림차순 정렬 → primary tag = 가장 높은 유사도
            scored.sort(key=lambda x: x[1], reverse=True)
            reordered_normal = [t for t, _ in scored]

            # 최종 순서: 재정렬된 일반 태그 + 특수 태그(끝에 보존)
            new_tags = reordered_normal + special_tags
            new_tag_str = ",".join(new_tags)

            if new_tag_str != tag_str:
                updates.append({
                    "id":        book['id'],
                    "title":     book['title'],
                    "old_tags":  tag_str,
                    "new_tags":  new_tag_str,
                    "old_first": all_tags[0],
                    "new_first": new_tags[0] if new_tags else "",
                    "scores":    [(t, round(s, 4)) for t, s in scored],
                })

        done = min(batch_start + BOOK_BATCH, len(target_books))
        print(f"  ⏳ {done}/{len(target_books)} 완료...")

    # ── 4. 결과 출력 ─────────────────────────────────────────────────────────
    primary_changed = sum(1 for u in updates if u['old_first'] != u['new_first'])
    print(f"\n{'='*70}")
    print(f"📊 결과 요약")
    print(f"{'='*70}")
    print(f"  순서 변경:           {len(updates)}권")
    print(f"  primary 태그 변경:   {primary_changed}권")
    print(f"  순서 동일:           {len(target_books) - len(updates) - error_count}권")
    print(f"  임베딩 실패 건너뜀:  {error_count}권")

    if updates:
        # primary 태그 변경 케이스 상세 출력 (최대 30건)
        changed_primary = [u for u in updates if u['old_first'] != u['new_first']]
        print(f"\n🔀 Primary 태그 변경 케이스 (상위 30건):")
        print(f"{'ID':<8} {'도서명':<26} {'기존':<14} {'새':<14} {'유사도'}")
        print("-" * 72)
        for u in changed_primary[:30]:
            title_s = u['title'][:24] + '..' if len(u['title']) > 24 else u['title']
            top_score = u['scores'][0][1] if u['scores'] else 0
            print(f"{u['id']:<8} {title_s:<26} {u['old_first']:<14} → {u['new_first']:<14} ({top_score:.3f})")
        if len(changed_primary) > 30:
            print(f"  ... 외 {len(changed_primary) - 30}건")

    if not args.commit:
        print(f"\nℹ️  Dry-run 모드입니다. 실제 적용하려면: --commit")
        return

    # ── 5. DB 업데이트 ───────────────────────────────────────────────────────
    print(f"\n💾 DB 업데이트 중 ({len(updates)}건)...")
    success = 0
    for u in updates:
        try:
            supabase.table("childbook_items") \
                .update({"curation_tag": u["new_tags"]}) \
                .eq("id", u["id"]) \
                .execute()
            success += 1
            if success % 50 == 0:
                print(f"  ⏳ {success}/{len(updates)} 완료...")
        except Exception as e:
            print(f"  ❌ [{u['id']}] {u['title']} 실패: {e}")

    print(f"\n🎉 완료! {success}/{len(updates)}권 태그 순서 재정렬 적용됨.")
    print(f"   Primary 태그 변경: {primary_changed}권")


if __name__ == "__main__":
    main()
