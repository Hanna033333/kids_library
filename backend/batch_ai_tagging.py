import os
import json
import time
from typing import List, Dict, Any
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 상수 정의
MODEL_NAME = "gemini-3-flash-preview"
BATCH_SIZE = 10

# 20개 표준 카테고리 정의
TAXONOMY = [
    {"id": 1, "subtitle": "오늘 밤도 꿀잠", "title": "포근한 잠자리 책", "tag": "#잠자리"},
    {"id": 2, "subtitle": "감정이 서툰 아이를 위한", "title": "마음 처방전", "tag": "#감정조절"},
    {"id": 3, "subtitle": "기 죽지 않는 아이로", "title": "자존감 그림책", "tag": "#자존감"},
    {"id": 4, "subtitle": '"친구랑 놀고 싶어!"', "title": "사회성 기르기", "tag": "#사회성"},
    {"id": 5, "subtitle": "내 몸이 궁금한 꼬마 박사님", "title": "신비한 우리 몸", "tag": "#인체"},
    {"id": 6, "subtitle": "상상력이 팡팡 터지는", "title": "판타지 세계", "tag": "#판타지"},
    {"id": 7, "subtitle": "초록 지구를 지키는", "title": "환경 학교", "tag": "#환경보호"},
    {"id": 8, "subtitle": "생명의 소중함을 배우는", "title": "동물 친구들", "tag": "#생명존중"},
    {"id": 9, "subtitle": "사랑이 퐁퐁 샘솟는", "title": "가족 이야기", "tag": "#가족사랑"},
    {"id": 10, "subtitle": '"같이 하면 더 즐거워"', "title": "나눔과 배려", "tag": "#배려"},
    {"id": 11, "subtitle": "겁 많은 아이도 용감하게", "title": "두근두근 모험", "tag": "#모험"},
    {"id": 12, "subtitle": "지혜와 해학이 담긴", "title": "재밌는 옛이야기", "tag": "#전래동화"},
    {"id": 13, "subtitle": "감수성을 깨우는", "title": "꼬마 예술가", "tag": "#예술감성"},
    {"id": 14, "subtitle": "숲속 친구들의 일상", "title": "신비한 자연 관찰", "tag": "#자연관찰"},
    {"id": 15, "subtitle": "과거로 떠나는 시간 여행", "title": "지혜로운 역사", "tag": "#역사이야기"},
    {"id": 16, "subtitle": "원리를 깨우치는 재미", "title": "꼬마 과학자", "tag": "#과학원리"},
    {"id": 17, "subtitle": "다름을 존중하는 아이", "title": "세계 시민 학교", "tag": "#다양성"},
    {"id": 18, "subtitle": "등원 거부가 사라지는", "title": "즐거운 유치원", "tag": "#적응"},
    {"id": 19, "subtitle": "우리 문화의 자부심", "title": "전통과 유산", "tag": "#우리문화"},
    {"id": 20, "subtitle": "시원한 수박과 바다 여행", "title": "여름의 추억", "tag": "#계절"}
]

class CurationBatcher:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def fetch_target_books(self, limit: int = 10):
        """태깅이 필요한 도서를 가져옵니다."""
        # confidence_score가 0이거나 미달인 도서 우선 처리
        res = self.supabase.table("childbook_items")\
            .select("id, title, author, description")\
            .filter("confidence_score", "eq", 0)\
            .not_.is_("description", "null")\
            .limit(limit).execute()
        return res.data

    def build_prompt(self, books: List[Dict]):
        """Gemini를 위한 프리미엄 큐레이션 분석 프롬프트를 생성합니다."""
        taxonomy_str = "\n".join([f"- {t['tag']}: {t['subtitle']} ({t['title']})" for t in TAXONOMY])
        
        books_str = ""
        for i, b in enumerate(books):
            books_str += f"[{i+1}] ID: {b['id']}, 제목: {b['title']}, 작가: {b['author']}\n내용: {b['description'][:400]}\n\n"
            
        prompt = f"""
당신은 20년 경력의 베테랑 어린이 도서 사서이자, 부모들의 마음을 읽는 육아 전문가입니다.
제공된 {len(books)}권의 도서를 깊이 있게 분석하여, 아이의 성장 단계와 정서에 꼭 맞는 상황별 태그(1~3개)와 '사서의 추천 코멘트'를 작성해주세요.

[표준 카테고리 태그 리스트]
{taxonomy_str}

[코멘트 작성 가이드 (Critical)]
1. 단순히 책 내용을 요약하지 마세요. (예: "이 책은 모험 이야기입니다" -> X)
2. 부모님에게 말을 건네는 듯한 다정한 톤으로 작성하세요. (예: "~한 아이에게 이 책은 아주 좋은 선물이 될 거예요", "~하며 읽어주면 아이의 마음이 쑥쑥 자랄 거예요" -> O)
3. 해당 책이 아이의 정서, 올바른 습관, 또는 부모와의 정서적 교감에 어떤 구체적인 도움을 주는지 한 문장(60자 내외)으로 표현하세요.
4. 문학적인 풍부함과 전문가의 통찰이 느껴져야 합니다.

[작성 규칙]
1. 반드시 위 리스트에 있는 태그(#)만 사용하세요.
2. 각 도서별로 1~3개의 태그를 선택하세요.
3. 분석의 정확도와 매칭 품질을 'confidence_score' (0-100)로 표시하세요.

[출력 형식 (JSON 배열로만 응답)]
[
  {{
    "id": 123,
    "tags": ["#잠자리", "#가족사랑"],
    "curation_note": "아이를 품에 안고 천천히 읽어주세요. 부모님의 따스한 목소리가 아이의 밤을 포근한 꿈으로 채워줄 거예요.",
    "confidence_score": 98
  }},
  ...
]

[분석 대상 도서]
{books_str}
"""
        return prompt

    def run_batch(self, limit: int = 10):
        """배치 작업을 실행합니다."""
        books = self.fetch_target_books(limit)
        if not books:
            print("태깅할 대상 도서가 없습니다.")
            return

        print(f"--- 🤖 AI 분석 시작 (총 {len(books)}권) ---")
        
        # BATCH_SIZE 단위로 쪼개서 처리
        for i in range(0, len(books), BATCH_SIZE):
            chunk = books[i:i + BATCH_SIZE]
            print(f"\n[Batch {i//BATCH_SIZE + 1}] {len(chunk)}권 처리 중...")
            prompt = self.build_prompt(chunk)
            
            try:
                # Add delay to avoid rate limits
                if i > 0:
                    time.sleep(2)
                    
                response = self.model.generate_content(prompt)
                
                text = response.text.strip()
                # Handle possible markdown wrapping
                if "```json" in text:
                    start_idx = text.find("```json") + 7
                    end_idx = text.rfind("```")
                    text = text[start_idx:end_idx].strip()
                elif text.startswith("```"):
                    text = text[3:-3].strip()
                
                results = json.loads(text)
                
                # DB 업데이트
                for res in results:
                    tag_str = ",".join(res.get('tags', []))
                    
                    self.supabase.table("childbook_items").update({
                        "curation_tag": tag_str,
                        "curation_note": res.get('curation_note', ''),
                        "confidence_score": res.get('confidence_score', 0)
                    }).eq("id", res['id']).execute()
                    
                    print(f"✅ 완료: {res['id']} | 태그: {tag_str} | 점수: {res.get('confidence_score')}")
                    
            except Exception as e:
                print(f"❌ 에러 발생 (Batch {i//BATCH_SIZE + 1}): {e}")
                if 'response' in locals():
                    print(f"Response raw: {response.text}")

if __name__ == "__main__":
    import sys
    limit = 100
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
            
    batcher = CurationBatcher()
    batcher.run_batch(limit=limit)
