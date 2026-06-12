"""
초고속 배포용 일괄 재분류 스크립트 (Gemini 2.5 flash 일괄 프롬프트 활용)
"""
import asyncio
import os
import sys
import json
import google.generativeai as genai
from supabase_client import supabase

if sys.platform.startswith('win'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

VALID_CATEGORIES = [
    "동화", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "지리"
]

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def process_batch(batch):
    prompt = "당신은 어린이 도서 전문 사서입니다. 다음 도서들의 정보(ID, 제목, 저자 등)를 보고 알맞은 카테고리 단어 하나로 매핑해 주세요.\n\n"
    prompt += "## 카테고리 정의:\n"
    prompt += ", ".join(VALID_CATEGORIES) + "\n"
    prompt += "('외국', '학부모'는 절대 사용 불가. 외국 동화는 '동화', 부모 교육용은 '사회' 등으로 분류할 것)\n\n"
    
    prompt += "## 도서 목록:\n"
    for b in batch:
        prompt += f"- ID: {b['id']}, 제목: {b['title']}, 저자: {b.get('author','')} \n"
        
    prompt += "\n## 결과 응답 형식 (반드시 아래 JSON 형태만 리턴, 설명 생략):\n"
    prompt += "[\n  {\"id\": 1, \"category\": \"동화\"},\n  {\"id\": 2, \"category\": \"사회\"}\n]\n"
    
    try:
        res = model.generate_content(prompt)
        text = res.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        results = json.loads(text.strip())
        return results
    except Exception as e:
        print(f"Batch Error: {e}")
        # 실패 시 전부 동화로 임시 매핑
        return [{"id": b["id"], "category": "동화"} for b in batch]

async def main():
    print("🚀 잔여 도서 초고속 재분류 시작...")
    # 아직 이동되지 않은 외국, 외국도서, 학부모
    targets = ['외국', '외국도서', '학부모']
    result = supabase.table('childbook_items').select('id,title,author,category').in_('category', targets).execute()
    books = result.data
    
    if not books:
        print("✅ 처리할 대상이 없습니다.")
        return
        
    print(f"총 {len(books)}권 남음. 40권씩 일괄 처리...")
    batches = list(chunk_list(books, 40))
    
    for i, batch in enumerate(batches, 1):
        print(f"배치 {i}/{len(batches)} 처리중...")
        mapping = await process_batch(batch)
        
        # DB 업데이트
        for m in mapping:
            cat = m.get("category", "동화")
            if cat not in VALID_CATEGORIES:
                cat = "동화"
                
            book_id = m.get("id")
            if book_id:
                supabase.table('childbook_items').update({'category': cat}).eq('id', book_id).execute()
                
        print(f"✅ 배치 {i} DB 반영 완료")
        await asyncio.sleep(2) # rate limit 방지
        
    print("🎉 모든 데이터 초고속 업데이트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
