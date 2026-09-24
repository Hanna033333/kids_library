"""
AI 기반 책자리 서비스 업데이트 공지사항 자동 생성 및 노션(Notion) 발행 스크립트

워크플로우:
  1. 업데이트 내용 입력
  2. Gemini AI 초안 생성
  3. 사용자 검수 (CLI 또는 에이전트 검수)
  4. 승인(OK) 시 노션 발행 & 프론트엔드 최신 공지 동기화
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

# 환경변수 로딩
backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env")

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_PARENT_PAGE_ID = "2e4939f0-03ba-807d-9580-c056baacf0fa"  # 책자리 메인 노션 페이지 ID

# 프론트엔드 공유 공지 JSON 경로
FRONTEND_NOTICE_JSON = backend_dir.parent / "frontend" / "shared" / "latest_notice.json"


def generate_notice_content_with_gemini(update_summary: str) -> dict:
    """Gemini API를 활용해 3040 부모님 대상의 친절하고 명확한 공지사항 초안을 생성합니다."""
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 .env에 설정되어 있지 않습니다.")

    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = genai.GenerativeModel("gemini-1.5-flash")

    today_str = datetime.now().strftime("%y.%m.%d")
    
    prompt = f"""
당신은 어린이 도서 큐레이션 및 도서관 대출 안내 서비스 '책자리(Checkjari)'의 서비스 기획자/운영자입니다.
서비스의 새로운 기능 업데이트 내용을 전달받아, 책자리를 이용하는 3040 부모님들이 읽기 편하고 직관적인 노션용 공지사항을 작성해주세요.

[업데이트 핵심 내용]
{update_summary}

[작성 가이드라인]
1. 톤앤매너: 정중하면서도 따뜻하고 다정한 존댓말 (~해요, ~합니다). 육아에 바쁜 부모님이 10초 만에 이해할 수 있도록 명확하게.
2. 제목(title): 15자 내외의 간결하고 매력적인 제목. (예: "도서관 5곳 추가 및 청구기호 연동 안내 ({today_str})")
3. 요약(summary): 이번 업데이트의 핵심 가치를 1~2줄로 요약한 문장.
4. 주요 개선사항(improvements): 2~4개의 항목으로 구체적인 변경점과 사용자 혜택 설명.
5. 이용 방법(how_to_use): 부모님이 앱/웹에서 어떻게 확인하고 쓰면 되는지 1~3단계 간단 안내.
6. 마무리 인사(footer): 이용 감사 및 따뜻한 한 줄 인사.

반드시 아래 JSON 형식으로만 응답하세요 (Markdown 코드 블록 없이 순수 JSON만 반환):
{{
  "title": "공지 제목({today_str})",
  "summary": "핵심 요약 문구",
  "improvements": [
    "항목 1 설명",
    "항목 2 설명"
  ],
  "how_to_use": [
    "이용 팁 1",
    "이용 팁 2"
  ],
  "footer": "마무리 안내 문구"
}}
"""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    # JSON 파싱 정제
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except Exception as e:
        print(f"[Warning] JSON 파싱 실패, 기본 템플릿 폴백: {e}")
        return {
            "title": f"서비스 기능 업데이트 안내({today_str})",
            "summary": update_summary,
            "improvements": [update_summary],
            "how_to_use": ["책자리 웹사이트에서 새로워진 기능을 바로 이용해 보세요."],
            "footer": "더 편리한 책자리가 되도록 항상 노력하겠습니다. 감사합니다."
        }


def create_notion_page(notice_data: dict) -> tuple:
    """Notion API를 호출하여 책자리 페이지 하위에 새 공지사항 페이지를 생성합니다."""
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY가 .env에 설정되어 있지 않습니다.")

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    blocks = [
        # 1. 상단 요약 콜아웃
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": notice_data["summary"]}}],
                "icon": {"emoji": "💡"},
                "color": "yellow_background"
            }
        },
        # 2. 구분선
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        }
    ]

    # 도서관 목록이 명시되어 있는 경우 전용 섹션 생성
    if "libraries" in notice_data and notice_data["libraries"]:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": f"✨ 신규 추가된 도서관 목록 ({len(notice_data['libraries'])}곳)"}}]
            }
        })
        for lib in notice_data["libraries"]:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": lib}, "annotations": {"bold": True}}]
                }
            })
    else:
        # 일반 주요 업데이트 내용
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "✨ 어떤 점이 새로워졌나요?"}}]
            }
        })
        for item in notice_data.get("improvements", []):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }
            })

    # 도서관 신청 링크 섹션
    if "request_link" in notice_data and notice_data["request_link"]:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🙋 자주 가는 도서관이 없으신가요?"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "여기에 없는 도서관은 신청해 주시면 확인 후 빠르게 추가해 드릴게요!\n아래 링크를 통해 편하게 신청해 주세요.\n\n"}},
                    {
                        "type": "text", 
                        "text": {
                            "content": "👉 [도서관 추가 신청하기]", 
                            "link": {"url": notice_data["request_link"]}
                        },
                        "annotations": {"bold": True, "color": "orange"}
                    }
                ]
            }
        })

    # 4. 이용 방법
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📖 이렇게 이용해 보세요!"}}]
        }
    })

    for step in notice_data.get("how_to_use", []):
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": step}}]
            }
        })

    # 5. 마무리
    blocks.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": notice_data.get("footer", "더 편리한 책자리가 되겠습니다. 감사합니다. ✨")},
                    "annotations": {"italic": True, "color": "gray"}
                }
            ]
        }
    })

    payload = {
        "parent": {
            "page_id": NOTION_PARENT_PAGE_ID
        },
        "icon": {
            "emoji": "📢"
        },
        "properties": {
            "title": [
                {
                    "text": {
                        "content": notice_data["title"]
                    }
                }
            ]
        },
        "children": blocks
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=headers, json=payload)
    
    if res.status_code != 200:
        raise RuntimeError(f"Notion API 에러 ({res.status_code}): {res.text}")

    result_json = res.json()
    page_id = result_json["id"]
    page_url = result_json.get("url", f"https://notion.so/{page_id.replace('-', '')}")
    
    return page_url, page_id


def save_latest_notice_to_frontend(title: str, url: str):
    """프론트엔드 latest_notice.json 파일에 동기화 저장합니다."""
    FRONTEND_NOTICE_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    notice_info = {
        "title": title,
        "url": url,
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_label": datetime.now().strftime("%m/%d")
    }
    
    with open(FRONTEND_NOTICE_JSON, "w", encoding="utf-8") as f:
        json.dump(notice_info, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 프론트엔드 공지 파일 동기화 완료: {FRONTEND_NOTICE_JSON}")


def publish_notice_direct(notice_data: dict) -> tuple:
    """검수 완료된 공지사항 데이터를 노션에 발행하고 프론트엔드에 연결합니다."""
    page_url, page_id = create_notion_page(notice_data)
    save_latest_notice_to_frontend(notice_data["title"], page_url)
    return page_url, page_id


def main():
    parser = argparse.ArgumentParser(description="책자리 AI 노션 공지사항 검수 및 자동 발행기")
    parser.add_argument("--update", "-u", type=str, help="업데이트된 기능 내용 요약")
    parser.add_argument("--draft-only", action="store_true", help="발행 없이 초안 JSON만 생성")
    parser.add_argument("--publish-json", type=str, help="검수 완료된 JSON 파일을 받아 바로 발행")
    args = parser.parse_args()

    # 1. 검수 완료된 JSON 파일 직접 발행 모드
    if args.publish_json:
        with open(args.publish_json, "r", encoding="utf-8") as f:
            notice_data = json.load(f)
        page_url, _ = publish_notice_direct(notice_data)
        print(f"\n🎉 발행 성공! URL: {page_url}")
        return

    update_text = args.update
    if not update_text:
        print("=" * 60)
        print("📢 책자리 서비스 업데이트 공지사항 AI 작성 및 검수기")
        print("=" * 60)
        update_text = input("이번에 업데이트된 기능/내용을 입력해주세요:\n> ").strip()

    if not update_text:
        print("❌ 업데이트 내용이 입력되지 않아 종료합니다.")
        sys.exit(1)

    print("\n🤖 [1/3] Gemini AI가 공지사항 초안을 작성 중입니다...")
    notice_data = generate_notice_content_with_gemini(update_text)

    if args.draft_only:
        print(json.dumps(notice_data, ensure_ascii=False, indent=2))
        return

    # CLI 대화형 검수 UI
    print("\n" + "=" * 60)
    print("📋 [2/3] 작성된 공지사항 초안 (검수용)")
    print("=" * 60)
    print(f"📌 [제목]: {notice_data['title']}\n")
    print(f"💡 [요약]: {notice_data['summary']}\n")
    print("✨ [어떤 점이 새로워졌나요?]")
    for item in notice_data.get("improvements", []):
        print(f"  • {item}")
    print("\n📖 [이렇게 이용해 보세요!]")
    for step in notice_data.get("how_to_use", []):
        print(f"  • {step}")
    print(f"\n💌 [마무리]: {notice_data.get('footer', '')}")
    print("=" * 60)

    confirm = input("\n👉 이 내용으로 노션에 발행하고 서비스에 연결할까요? (Y/n): ").strip().lower()
    if confirm not in ["", "y", "yes"]:
        print("❌ 발행이 취소되었습니다. 내용을 수정한 후 다시 실행해 주세요.")
        sys.exit(0)

    print("\n📤 [3/3] 노션 발행 및 프론트엔드 동기화 진행 중...")
    page_url, _ = publish_notice_direct(notice_data)

    print("\n" + "=" * 60)
    print("✨ 모든 작업이 완료되었습니다!")
    print(f"1. 노션 공지 페이지: {page_url}")
    print(f"2. 서비스 노출 제목: {notice_data['title']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
