#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import urllib.parse
import json
import datetime
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# backend/.env 파일을 명시적으로 로드
load_dotenv(dotenv_path="/Users/1004823/Desktop/kids_library/backend/.env", override=True)

# backend 및 scripts/data 디렉토리를 path에 추가
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "scripts" / "data"))

try:
    from supabase_client import supabase
except ImportError as e:
    print(f"❌ supabase_client 임포트 실패: {e}")
    sys.exit(1)

from core.taxonomy import get_weekly_curations, ALL_TAXONOMY
from services.card_generator import generate_card_news
from services.text_trimmer import trim_text_fallback
import google.generativeai as genai

def get_slug_by_tag(tag: str) -> str:
    for item in ALL_TAXONOMY:
        if item.get("tag") == tag:
            return item.get("slug", tag)
    return tag

def get_title_by_tag(tag: str) -> str:
    for item in ALL_TAXONOMY:
        if item.get("tag") == tag:
            return item.get("title", f"{tag} 그림책 추천")
    return f"{tag} 그림책 추천"

# 1. 큐레이션 도서 조회
def select_curation_books(curation_tag: str) -> List[dict]:
    """도서 데이터베이스에서 조건에 맞는 책 최대 5권을 조회합니다. (is_hidden=False, 이미지 필수, 첫 번째 태그 정밀 매칭)"""
    query = supabase.table("childbook_items").select("*")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")
    
    # 첫 번째 태그 정밀 매칭 (Rule 29 준수)
    or_filter = f'curation_tag.eq."{curation_tag}",curation_tag.like."{curation_tag},%",curation_tag.eq."#{curation_tag}",curation_tag.like."#{curation_tag},%"'
    query = query.or_(or_filter)
    query = query.order("title")
    
    result = query.execute()
    books = result.data if result.data else []
    
    # 5권보다 부족할 때 보충
    if len(books) < 5:
        needed = 5 - len(books)
        fallback_query = supabase.table("childbook_items").select("*")
        fallback_query = fallback_query.or_("is_hidden.is.null,is_hidden.eq.false")
        fallback_query = fallback_query.not_.is_("image_url", "null")
        fallback_query = fallback_query.neq("image_url", "")
        if books:
            book_ids = [b["id"] for b in books]
            fallback_query = fallback_query.not_.in_("id", book_ids)
        fallback_query = fallback_query.order("title").limit(needed)
        fallback_result = fallback_query.execute()
        if fallback_result.data:
            books.extend(fallback_result.data)
            
    return books[:5]

def get_books_from_latest_threads_feed(curation_tag: str) -> List[dict]:
    """threads_feeds 테이블에서 해당 태그의 가장 최근 피드에 등록된 도서 목록을 순서대로 가져옵니다."""
    try:
        tag_clean = curation_tag.lstrip("#")
        result = supabase.table("threads_feeds").select("book_ids")\
            .or_(f'curation_tag.eq."{tag_clean}",curation_tag.eq."#{tag_clean}"')\
            .order("id", desc=True).limit(1).execute()
        
        if result.data and result.data[0].get("book_ids"):
            book_ids = result.data[0]["book_ids"]
            print(f"💾 [Threads 연동] 최근 스레드 피드에서 도서 ID 목록을 가져왔습니다: {book_ids}")
            
            books_res = supabase.table("childbook_items").select("*").in_("id", book_ids).execute()
            if books_res.data:
                id_map = {b["id"]: b for b in books_res.data}
                books = []
                for bid in book_ids:
                    if bid in id_map:
                        books.append(id_map[bid])
                return books
    except Exception as e:
        print(f"⚠️ threads_feeds 조회 중 오류 발생: {e}")
    return []

# 2. AI 기반 카드뉴스 매력 줄거리 요약 생성
def generate_card_descriptions_ai(tag: str, books: List[dict]) -> List[str]:
    """도서 5권에 대해 서지정보/수상내역 대신 아이와 부모를 사로잡는 매력적인 3줄 핵심 줄거리 요약(각 58~68자)을 AI로 생성합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [trim_text_fallback(b.get("description") or b.get("curation_note") or b.get("title")) for b in books]
        
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    except Exception:
        try:
            model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})
        except Exception:
            return [trim_text_fallback(b.get("description") or b.get("curation_note") or b.get("title")) for b in books]
        
    books_summary_info = [
        {
            "index": idx + 1,
            "title": b.get("title"),
            "raw_description": b.get("description") or b.get("curation_note") or ""
        }
        for idx, b in enumerate(books)
    ]
    
    prompt = f"""
당신은 아동 도서 카드뉴스 전문 에디터입니다.
아래 {len(books)}권의 그림책에 대해, 카드뉴스 이미지(1080x1080) 중앙에 들어갈 **생생하고 매력적인 핵심 줄거리 3줄 요약(공백 포함 정확히 55자~62자)**을 작성해 주세요.

[절대 주의 사항]
1. ❌ 딱딱한 서지정보/수상내역 절대 금지: "OO상 수상작", "OO협회 선정도서", "OO 시리즈" 같은 무미건조한 출판사 홍보 문구는 절대 쓰지 마세요.
2. ⭕ 오직 재미있는 책 줄거리와 흥미 포인트만 작성: 아이가 어떤 모험을 떠나는지, 어떤 재미있는 일이 벌어지는지 생생한 이야기 중심으로 요약하세요.
3. ⭕ 분량 엄수: 각 도서당 공백 포함 정확히 55자~62자 이내로 완결된 1~2개 문장으로 작성하세요.
4. ⭕ 끝마침: 반드시 마침표(.)로 끝나는 완전한 존댓말 문장 ("~ 이야기예요.", "~ 펼쳐집니다.", "~ 전해줍니다.")

[도서 데이터]
{json.dumps(books_summary_info, ensure_ascii=False, indent=2)}

[반환 JSON 포맷]
{{
  "card_descriptions": [
    "1번 책의 생생한 줄거리 요약 (55~62자 완성형 문장)",
    "2번 책의 생생한 줄거리 요약 (55~62자 완성형 문장)",
    "3번 책의 생생한 줄거리 요약 (55~62자 완성형 문장)",
    "4번 책의 생생한 줄거리 요약 (55~62자 완성형 문장)",
    "5번 책의 생생한 줄거리 요약 (55~62자 완성형 문장)"
  ]
}}
"""
    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        descs = res_data.get("card_descriptions", [])
        if len(descs) == len(books):
            print(f"✨ [AI 요약] 총 {len(books)}권의 매력적인 3줄 카드뉴스 줄거리 요약 생성을 완료했습니다.")
            clean_descs = []
            for d in descs:
                d = d.strip()
                if not d.endswith(('.', '!', '?')):
                    d += '.'
                clean_descs.append(d)
            return clean_descs
    except Exception as e:
        print(f"⚠️ AI 카드 요약 생성 실패 ({e}), 폴백 로직 적용")
        
    return [trim_text_fallback(b.get("description") or b.get("curation_note") or b.get("title")) for b in books]

# 3. 카드뉴스 이미지 일괄 생성
def create_card_news_images(tag: str, books: List[dict]) -> List[str]:
    """블로그용 1080x1080 고화질 독창적 카드뉴스 이미지를 생성하고 로컬 파일 경로 목록을 반환합니다."""
    output_img_dir = Path(__file__).parent / "output" / "blog_posts" / "images" / tag
    output_img_dir.mkdir(parents=True, exist_ok=True)
    
    curation_title = get_title_by_tag(tag)
    saved_paths = []
    
    print(f"🎨 [카드뉴스 생성] 총 {len(books)}권에 대한 1080x1080 고화질 카드뉴스 이미지를 렌더링합니다...")
    ai_descriptions = generate_card_descriptions_ai(tag, books)
    
    for idx, b in enumerate(books):
        try:
            title = b.get("title") or "제목 없음"
            author = b.get("author") or ""
            publisher = b.get("publisher") or ""
            cover_url = b.get("image_url") or ""
            desc_for_card = ai_descriptions[idx] if idx < len(ai_descriptions) else trim_text_fallback(b.get("description") or "")
            
            card_img = generate_card_news(
                title=title,
                author=author,
                publisher=publisher,
                cover_url=cover_url,
                description=desc_for_card,
                curation_title=curation_title
            )
            
            card_path = output_img_dir / f"card_{idx + 1}.png"
            card_img.save(str(card_path), format="PNG", quality=95)
            saved_paths.append(str(card_path))
            print(f"  ✓ [{idx + 1}/{len(books)}] {title[:15]}... -> {card_path.name}")
        except Exception as e:
            print(f"  ⚠️ 카드뉴스 {idx + 1} 생성 실패 ({e}), 원본 표지로 폴백")
            saved_paths.append(b.get("image_url") or "")
            
    return saved_paths

# 3. 블로그용 원고 생성
def generate_blog_content(tag: str, books: List[dict], card_paths: List[str]) -> str:
    """Gemini API를 사용하여 네이버 블로그 DIA+ 상위 노출에 최적화된 체험형 마크다운 원고를 생성합니다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY가 설정되어 있지 않아 글을 생성할 수 없습니다.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    
    # 모델 정의
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"❌ GenerativeModel 초기화 에러: {e}")
            sys.exit(1)

    # 도서 리스트 가공
    books_info = []
    tag_slug = get_slug_by_tag(tag)
    for idx, b in enumerate(books):
        card_file = card_paths[idx] if idx < len(card_paths) else b.get("image_url") or ""
        books_info.append({
            "index": idx + 1,
            "title": b.get("title"),
            "author": b.get("author") or "",
            "publisher": b.get("publisher"),
            "card_image_path": card_file,
            "description": b.get("description") or b.get("curation_note") or ""
        })

    book_count = len(books_info)
    main_curation_url = f"https://checkjari.com/collections/curation/{tag_slug}?utm_source=naver_blog&utm_medium=referral&utm_campaign=weekly_{tag_slug}"

    prompt = f"""
당신은 6살 아이를 직접 키우며 매주 동네 도서관에서 책을 빌려 읽히는 실전 육아맘입니다.
네이버 최신 알고리즘(C-Rank 및 DIA+) 기준 검색 상위 노출을 달성할 수 있는 리얼하고 정성스러운 체험형 블로그 원고를 한글로 작성해 주세요.

[제공된 도서 데이터 - 정확히 {book_count}권]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[핵심 키워드 및 링크]
- 주제 태그: '{tag}'
- 메인 검색 키워드: '{tag} 그림책 추천' (또는 '{tag} 책 추천')
- 서브 키워드: '5세 {tag} 책', '6세 그림책', '7세 추천도서', '도서관 대출', '어린이도서관 청구기호'
- 대표 랜딩 URL: {main_curation_url}

[절대 금지 사항 - 위반 시 즉시 재작성]
1. ❌ 마크다운 문법 일체 사용 금지! (네이버 블로그는 마크다운을 지원하지 않습니다)
   - `###`, `##`, `**볼드**`, `*기울임*`, `---` 구분선, `[링크](URL)`, `![이미지](URL)` 등의 마크다운 특수기호를 본문에 절대 쓰지 마세요.
   - 강조가 필요할 땐 [소제목], '따옴표', 이모지, 대괄호 등을 활용하세요.
2. ❌ 다자녀(첫째, 둘째, 두 아이 등) 설정 절대 금지! - 저희 집 아이는 **"6살 아이 한 명(외동)"**입니다. "첫째", "둘째" 같은 표현을 절대 쓰지 마세요.
3. ❌ 허위 SNS 계정명 금지 - "@육아맘닉네임" 같은 가공의 계정명/아이디를 절대 만들어내지 마세요
4. ❌ 과장된 수식어 금지 - "네이버 1위 인플루언서", "10년 차 전문가" 같은 허위 타이틀 금지
5. ❌ 마케터/AI 홍보 톤 금지 - "책자리 서비스 마케터입니다", "큐레이션 전문 서비스" 같은 상업적 소개 금지
6. ❌ 과도한 이모지 남발 금지 - 이모지는 문단당 1개 이하로 절제해서 사용

[필수 작성 원칙]
1. ⭕ 1인칭 실전 육아맘 체험 톤 - "저희 집 6살 아이가 밤마다 떼를 써서 직접 도서관에서 빌려 읽혀본 리얼 후기예요"처럼 생생하게
2. ⭕ 아이의 구체적인 반응 묘사 - "아이가 이 장면에서 깔깔 웃더라고요", "눈을 비비며 쿨쿨 잠들었어요" 등 6살 아이 한 명의 반응을 실감나게 묘사
3. ⭕ 모바일 가독성 - 1~2문장마다 반드시 엔터(개행)와 빈 줄을 넣어 스마트폰에서 읽기 편하게
4. ⭕ 총 글자 수 - 공백 제외 최소 1,800자 이상

---

[반환 출력 포맷 - 아래 3단 구조를 반드시 지킬 것 (마크다운 기호 없이 순수 텍스트로만)]

출력 시작은 반드시 아래 구분선과 제목 섹션 헤더로 시작하세요:

=== 네이버 블로그 제목 (제목 입력창에 복사하세요) ===
(여기에 제목 1줄만 작성. 형식: {tag} 그림책 추천 + 클릭 유도 후킹 문구 + 도서 수 + 괄호 팁.
예시: 잠자리 그림책 추천 6세 아이 꿀잠 부른 베스트 {book_count}선 (도서관 무료 대출 팁)
주의: 특수문자나 이모지를 제목 앞에 넣지 말고, 순수 텍스트 1줄로만 작성)
=====================================================

=== 네이버 블로그 본문 (본문 입력창에 복사하세요) ===

(도입부: 공감형 육아 에피소드 → 잠투정/육아 고민 공감 → 동네 도서관에서 빌려 읽혀보고 너무 좋았던 {tag} 그림책들을 바로 소개하는 흐름으로 자연스럽게 작성)

(본문: 제공된 도서 {book_count}권을 차례대로 아래 포맷으로 상세 소개 - 마크다운 기호 금지)

📖 [순번]. 도서명 - 저자 / 출판사 (추천 연령: X~X세)

[사진 첨부 (추천): 카드뉴스 [순번]번 - card_image_path]

[직접 읽어준 줄거리 & 우리 아이 반응]
(줄거리 요약 + 아이의 생생한 반응을 합쳐서 4~5문장으로. 생동감 있게 묘사할 것)

[이 책이 좋았던 이유]
(정서적 안정, 발달 이점을 2~3문장으로 담백하게 설명)


(아웃트로: 책자리 서비스 소개 - 중요! 아래 포지셔닝을 정확히 지킬 것)
사실 저는 아이들 책 찾기가 너무 불편해서 직접 '책자리(checkjari.com)'라는 서비스를 만들었어요.
우리 동네 도서관에 어떤 책이 있는지, 지금 대출이 가능한지를 한 번에 확인할 수 있는 서비스인데요.
가입 없이 3초 만에 도서관을 설정하면, 오늘 소개한 책의 청구기호와 실시간 대출 가능 여부를 바로 확인할 수 있어요.
도서관 가시기 전에 꼭 한번 확인해 보세요!

👉 우리동네 도서관 실시간 대출 현황 & 전체 큐레이션 목록 확인하기
{main_curation_url}

오늘 글이 도움 되셨다면 공감과 이웃추가 꾹 눌러주세요! 감사합니다.

=====================================================

=== 네이버 블로그 태그 (태그 입력창에 복사하세요) ===
(쉼표 없이 공백으로 구분된 해시태그 10개. 메인 키워드 + 연령 + 상황 키워드 조합)
=====================================================
"""

    def clean_for_naver_editor(text: str, tag_name: str, saved_cards: List[str]) -> str:
        """마크다운 문법을 네이버 스마트에디터 ONE에 복사하기 좋은 순수 텍스트로 정제합니다."""
        import re
        # 1. 헤딩 ### 제거
        text = re.sub(r'#+\s*', '', text)
        
        # 2. 사진 첨부 태그를 1~5번 순서대로 정확한 카드뉴스 파일 경로로 치환
        card_counter = 0
        def replace_card_slot(match):
            nonlocal card_counter
            card_counter += 1
            card_num = min(card_counter, 5)
            card_file = f"card_{card_num}.png"
            full_path = f"/Users/1004823/Desktop/kids_library/backend/output/blog_posts/images/{tag_name}/{card_file}"
            return f"\n[사진 첨부 (추천): 카드뉴스 {card_num}번 - {full_path}]\n"
            
        text = re.sub(r'\[사진 첨부.*?\]', replace_card_slot, text)
        
        # 3. *(사진: ...)* 캡션 정리
        text = re.sub(r'\*\((.*?)\)\*', r'(\1)', text)
        
        # 4. 마크다운 링크 문법 변환: [텍스트](url) -> 텍스트\nurl
        text = re.sub(r'\[(.*?)\]\((https?://.*?)\)', r'\1\n\2', text)
        
        # 5. 마크다운 볼드 **텍스트** -> [텍스트]
        text = re.sub(r'\*\*(.*?)\*\*', r'[\1]', text)
        
        # 6. 마크다운 구분선 --- 제거
        text = re.sub(r'\n---\n', r'\n\n', text)
        
        # 7. 기괴한 [[텍스트]] 중복 괄호 정돈
        text = text.replace('[[', '[').replace(']]', ']')
        
        return text.strip()

    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_for_naver_editor(response.text, tag, card_paths)
        return cleaned_text
    except Exception as e:
        print(f"❌ Gemini API를 통한 글 생성 중 오류 발생: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="네이버 블로그용 큐레이션 원고 생성기")
    parser.add_argument("--tag", "-t", required=False, type=str, default=None, help="검색할 큐레이션 태그명 (생략 시 오늘 요일의 주간 큐레이션 자동 선택)")
    args = parser.parse_args()

    tag = args.tag
    if not tag:
        # KST 기준 현재 요일에 매칭되는 주간 큐레이션 인덱스를 자동 계산
        tz_kst = datetime.timezone(datetime.timedelta(hours=9))
        now_kst = datetime.datetime.now(tz_kst)
        today_date = now_kst.date()
        weekday = now_kst.weekday()  # 0: 월, 2: 수, 4: 금
        
        # 월/수/금 인덱스 매핑 (0, 1, 2)
        if weekday == 0:
            target_idx = 0
        elif weekday == 2:
            target_idx = 1
        elif weekday == 4:
            target_idx = 2
        else:
            # 월/수/금 외의 요일에는 기본값으로 월요일 인덱스 적용
            target_idx = 0
            
        curations = get_weekly_curations(today_date)
        if curations and len(curations) > target_idx:
            tag = curations[target_idx]["tag"]
            print(f"📅 [요일 감지] 오늘 요일 인덱스: {weekday} -> 자동 선택된 큐레이션 태그: '{tag}'")
        else:
            print("❌ 오늘 요일에 해당하는 주간 큐레이션 데이터를 로드할 수 없습니다.")
            sys.exit(1)

    print(f"🔍 [네이버 블로그 원고 생성] 큐레이션 태그 '{tag}' 검색 중...")
    
    # 1. 책 데이터 로드 (최신 스레드 피드 연동 시도 후, 없을 시 select_curation_books 폴백)
    books = get_books_from_latest_threads_feed(tag)
    if not books:
        print(f"ℹ️ 최근 스레드 피드가 없거나 도서 조회가 실패하여 DB 쿼리 폴백을 사용합니다.")
        books = select_curation_books(tag)
        
    if not books:
        print(f"❌ '{tag}' 태그에 해당하는 도서 데이터를 Supabase에서 찾을 수 없습니다.")
        sys.exit(1)

    # 5권 미만이면 DB에서 동일 태그 도서로 보충
    if len(books) < 5:
        existing_ids = {b["id"] for b in books}
        extra_books = select_curation_books(tag)
        for b in extra_books:
            if b["id"] not in existing_ids:
                books.append(b)
                existing_ids.add(b["id"])
            if len(books) >= 5:
                break
        print(f"📚 [보충 완료] 스레드 도서 부족분을 DB에서 보충하여 총 {len(books)}권으로 확장했습니다.")
        
    print(f"📚 최종 도서 {len(books)}권을 매핑했습니다. 카드뉴스 생성 및 원고 생성을 진행합니다.")

    # 2. 카드뉴스 이미지 일괄 생성 (1080x1080 고화질 독창적 이미지)
    card_paths = create_card_news_images(tag, books)

    # 3. 원고 생성
    blog_content = generate_blog_content(tag, books, card_paths)

    # 4. 출력 디렉토리에 저장 (backend/output/blog_posts/ 에 안전하게 동적 생성)
    output_dir = Path(__file__).parent / "output" / "blog_posts"
    output_dir.mkdir(parents=True, exist_ok=True)
        
    output_file = output_dir / f"naver_blog_post_{tag}.md"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(blog_content)
        print(f"✅ 원고 생성이 성공적으로 완료되었습니다!")
        print(f"👉 생성된 파일 경로: {output_file.absolute()}")
        print(f"🖼️ 생성된 카드뉴스 폴더: {Path(__file__).parent / 'output' / 'blog_posts' / 'images' / tag}")
    except Exception as e:
        print(f"❌ 결과 파일 쓰기 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
