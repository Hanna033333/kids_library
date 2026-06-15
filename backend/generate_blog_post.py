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

# backend 디렉토리를 path에 추가하여 supabase_client 로딩 지원
sys.path.append(str(Path(__file__).parent))

try:
    from supabase_client import supabase
except ImportError as e:
    print(f"❌ supabase_client 임포트 실패: {e}")
    sys.exit(1)

from core.taxonomy import get_weekly_curations, ALL_TAXONOMY

def get_slug_by_tag(tag: str) -> str:
    for item in ALL_TAXONOMY:
        if item.get("tag") == tag:
            return item.get("slug", tag)
    return tag
import google.generativeai as genai

# 1. 큐레이션 도서 조회
def select_curation_books(curation_tag: str) -> List[dict]:
    """도서 데이터베이스에서 조건에 맞는 책 5권을 조회합니다. (is_hidden=False, 이미지 필수)"""
    query = supabase.table("childbook_items").select("*")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")
    query = query.ilike("curation_tag", f"%{curation_tag}%")
    query = query.order("title")
    
    result = query.execute()
    books = result.data if result.data else []
    
    # 5권보다 부족할 때 보충 (기존 select_five_books 스펙과 동일)
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

# 2. 블로그용 원고 생성
def generate_blog_content(tag: str, books: List[dict]) -> str:
    """Gemini API를 사용하여 네이버 블로그에 최적화된 마크다운 포맷의 글을 생성합니다."""
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

    # 도서 리스트를 프롬프트용 포맷으로 가공
    books_info = []
    tag_slug = get_slug_by_tag(tag)
    for idx, b in enumerate(books):
        book_id = b.get("id")
        # UTM 파라미터 구성
        utm_url = f"https://checkjari.com/book/{book_id}?utm_source=naver_blog&utm_medium=referral&utm_campaign=weekly_{tag_slug}"
        books_info.append({
            "index": idx + 1,
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "image_url": b.get("image_url") or "",
            "description": b.get("description") or b.get("curation_note") or "",
            "utm_url": utm_url
        })

    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 마케팅 및 콘텐츠 에디터입니다.
아래 제공된 도서 정보와 큐레이션 테마('{tag}') 정보를 활용하여 네이버 블로그에 발행할 최적화된 마케팅 정보글 포스팅을 한글로 작성해 주세요.

[포스팅 타겟 독자]
- 자녀에게 어떤 책을 읽혀야 할지 고민하는 학부모 (0~13세 자녀 둔 부모)

[도서 리스트 및 책자리 연결 링크 정보]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 가이드라인 - 중요]
1. 제목 (Title):
   - 클릭을 유도하고 검색 유입에 최적화된 키워드(예: '{tag} 그림책 추천', '연령별 추천도서' 등)를 포함하여 매력적이고 자연스럽게 작성해 주세요.
   
2. 도입부 (Intro):
   - 부모들이 일상에서 겪는 '{tag}'과 관련된 실제 양육 고민이나 에피소드(예: 잠자리 떼쓰기 등)에 깊이 공감하고 위로하는 다정한 존댓말 톤앤매너로 시작하세요.

3. 본문 (Body):
   - 큐레이션에 소개된 각 도서(최대 5권)를 하나씩 자세히 소개합니다.
   - 구성 항목:
     - 📖 도서명 (출판사)
     - 🖼️ [도서 표지 이미지] (여기에 제공된 각 도서의 image_url을 활용하여, HMTL <img> tag 혹은 마크다운 이미지 문법인 `![도서명 표지](image_url)` 형식으로 반드시 본문에 직접 삽입해 주세요. 포스팅 뷰에서 표지 이미지가 화면에 실제로 나타나야 합니다.)
     - 💡 책 내용 줄거리 요약 (부드럽고 이해하기 쉬운 분량)
     - 🌟 이 책을 추천하는 책자리만의 관점 (정서적/발달 단계적 이점 등)
     - 🔗 [실시간 도서관 대출 현황 및 상세 정보 확인하기] (이 링크에 제공된 각 도서의 utm_url을 그대로 마크다운 링크로 삽입하세요)
   - 각 도서 사이에는 적절한 구분선(--- 또는 Divider)을 두어 시각적인 피로감을 낮추세요.

4. 아웃트로 (Outro):
   - 포스팅 마무리 단계에서 책자리 서비스의 장점을 홍보합니다:
     "책자리 사이트에 가입이나 로그인 없이 3초 만에 내 도서관을 설정하면, 오늘 소개해드린 책이 우리동네 도서관 어린이실 어디에 꽂혀 있는지 청구기호와 실시간 대출 가능 여부를 바로 확인할 수 있습니다."
   - 해당 큐레이션 테마의 전체 도서 리스트를 보러 갈 수 있는 링크를 반드시 아래 문구를 앵커 텍스트로 삼아 본문에 포함해 주세요:
     "👉 [더 많은 독서 목록을 보고 싶으시면 여기를 클릭하세요](https://checkjari.com/collections/curation/{tag_slug}?utm_source=naver_blog&utm_medium=referral&utm_campaign=weekly_{tag_slug})"
   - 학부모들의 북마크(저장)와 공유를 자연스럽게 권장하는 멘트를 포함하세요.

5. 해시태그 (Hashtags):
   - 네이버 블로그 검색 태그용 해시태그 10개 내외를 나열해 주세요 (예: #어린이책추천 #책자리 #도서관청구기호 ...).

6. 모바일 가독성 줄바꿈 스타일 (★최중요★):
   - 스마트폰 모바일 화면에서의 가독성을 극대화하기 위해, 텍스트 작성 시 절대 3줄 이상 긴 문단을 유지하지 마세요.
   - 의미나 흐름이 끊기는 짧은 문구(구/절) 또는 1~2개의 짧은 문장 단위로 반드시 엔터(줄바꿈)와 빈 줄(문단 나눔)을 넉넉히 적용해야 합니다.
   - [예시 줄바꿈 구조 준수]:
     아이와 함께 우리 문화를 이야기하다 보면,
     '엄마, 옛날에는 왜 이랬던 거예요?'
     같은 질문에 막막할 때가 많으시죠?
     
     복잡한 역사나 지루한 설명 대신,
     아이의 눈높이에 맞춰
     우리 문화를 쉽고 재미있게 알려줄 수 방법이 없을까
     고민하는 부모님들을 위해
     특별한 큐레이션을 준비했어요.
     
     우리 아이의 마음속에 우리 문화의 씨앗을 심어줄
     그림책부터 역사 이야기까지,
     다채로운 '우리 문화' 도서들을 소개해 드릴게요.

반환할 포스팅 전체 텍스트는 바로 복사하여 블로그 스마트에디터 ONE에 붙여넣기할 수 있는 깔끔한 마크다운 양식이어야 합니다.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
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
    
    # 1. 책 데이터 로드
    books = select_curation_books(tag)
    if not books:
        print(f"❌ '{tag}' 태그에 해당하는 도서 데이터를 Supabase에서 찾을 수 없습니다.")
        sys.exit(1)
        
    print(f"📚 해당 태그 도서 {len(books)}권을 찾았습니다. 원고 생성을 진행합니다.")

    # 2. 원고 생성
    blog_content = generate_blog_content(tag, books)

    # 3. 아티팩트 경로에 저장
    # Antigravity가 이 파일의 존재를 감지하고 띄울 수 있도록 아티팩트 디렉토리에 저장합니다.
    possible_dirs = [
        Path("/Users/1004823/.gemini/antigravity-ide/brain/a290fb72-aa04-4d36-8b25-6d1abd1d9a58"),
        Path("/Users/1004823/.gemini/antigravity-ide/brain/2deb7665-edf7-4024-9ab6-c2682fcdf678")
    ]
    artifact_dir = None
    for d in possible_dirs:
        if d.exists():
            artifact_dir = d
            break
            
    if not artifact_dir:
        # 폴백으로 로컬 backend 경로에 저장
        artifact_dir = Path(__file__).parent
        
    output_file = artifact_dir / "naver_blog_post.md"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(blog_content)
        print(f"✅ 원고 생성이 성공적으로 완료되었습니다!")
        print(f"👉 생성된 파일 경로: {output_file.absolute()}")
    except Exception as e:
        print(f"❌ 결과 파일 쓰기 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
