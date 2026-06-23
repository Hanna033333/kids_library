import sys
import os
import asyncio
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import urllib.parse
from api.threads import select_five_books
from services.ai_content import generate_ai_threads_content
from services.card_generator import generate_card_news
from services.threads_publisher import upload_image_to_supabase, publish_carousel_to_threads, publish_reply_to_threads

async def test_e2e_pipeline():
    print("🚀 [E2E 파이프라인 테스트] 시작 (Storage 업로드 및 Gemini 연동 검증)")
    
    try:
        # 1. 책 5권 엄선
        print("\n📚 [Step 1] 도서 5권 선정 중...")
        books = select_five_books(curation_tag="가족사랑")
        print(f"✅ 도서 선정 완료 (총 {len(books)}권): {[b.get('title') for b in books]}")
        
        if len(books) < 5:
            print("⚠️ 도서 개수가 부족하여 임시로 더 많이 조회하거나 폴백을 사용합니다.")
            
        # 2. Gemini AI 요약문구 생성
        curation_title = "아이의 감정 조절을 돕는 그림책"
        print(f"\n🧠 [Step 2] Gemini AI 콘텐츠 생성 중 (주제: '{curation_title}')...")
        ai_content = generate_ai_threads_content(curation_title, "가족사랑", books)
        
        caption = ai_content.get("caption")
        card_descriptions = ai_content.get("card_descriptions", [])
        
        print("✅ Gemini 생성 결과:")
        print(f" - 캡션 본문: {caption}")
        for idx, card_data in enumerate(card_descriptions):
            print(f" - 카드 {idx+1} 설명: {card_data}")
            
        # 3. 카드뉴스 이미지 생성 및 Supabase Storage 업로드
        print("\n🎨 [Step 3] Pillow 카드뉴스 이미지 빌드 및 Supabase Storage 업로드 중...")
        public_image_urls = []
        
        for idx, book in enumerate(books):
            card_data = card_descriptions[idx] if idx < len(card_descriptions) else "따뜻한 그림책 추천입니다."
            desc = card_data if isinstance(card_data, str) else card_data.get("description", "따뜻한 그림책 추천입니다.")
                
            title = book.get("title", "제목")
            author = book.get("author", "저자")
            publisher = book.get("publisher", "출판사")
            cover_url = book.get("image_url")
            
            print(f"  - [{idx+1}/5] '{title}' 카드뉴스 렌더링 중...")
            
            # 카드뉴스 빌드
            card_img = generate_card_news(
                title=title,
                author=author,
                publisher=publisher,
                cover_url=cover_url,
                description=desc,
                curation_title=curation_title
            )
            
            # 파일 업로드 (E2E 테스트용 고유 폴더에 적재)
            file_name = f"threads_test/{uuid.uuid4()}.png"
            
            # Supabase 업로드
            public_url = await upload_image_to_supabase(card_img, file_name)
            public_image_urls.append(public_url)
            
        print("\n✅ [E2E 파이프라인 테스트] 이미지 생성 및 업로드 완료!")
        print(f"🔗 생성 및 업로드된 카드뉴스 이미지 목록 (총 {len(public_image_urls)}장):")
        for idx, url in enumerate(public_image_urls):
            print(f"   [{idx+1}] {url}")
            
        # 4. 스레드 실제 발행 테스트
        print("\n📣 [Step 4] 스레드 계정에 실제 캐러셀 카드뉴스 발행 중...")
        post_id = await publish_carousel_to_threads(text=caption, image_urls=public_image_urls)
        print(f"🎉 [Step 4] 스레드 실제 발행 성공! 포스트 ID: {post_id}")
        
        # 5. 스레드 첫 댓글 발행 테스트
        print("\n💬 [Step 5] 첫 댓글로 단축 링크 발행 중...")
        from api.threads import get_slug_by_tag
        slug = get_slug_by_tag("가족사랑")
        reply_text = f"🔗 https://checkjari.com/c/{slug}"
        reply_id = await publish_reply_to_threads(parent_post_id=post_id, reply_text=reply_text)
        print(f"🎉 [Step 5] 첫 댓글 발행 성공! 댓글 ID: {reply_id}")
        
    except Exception as e:
        print(f"\n❌ E2E 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_e2e_pipeline())
