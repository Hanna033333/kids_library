import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.card_generator import generate_card_news

def test_rendering():
    print("🎨 카드뉴스 렌더링 로컬 테스트 시작...")
    
    # 테스터 입력 데이터 (사용자 예시 시안 기준)
    title = "무슨 생각하니?"
    author = "로랑 모토"
    publisher = "로그프레스"
    
    # 로컬 디렉토리의 magic-book.png 이미지를 사용합니다.
    cover_url = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "magic-book.png")
    
    description = (
        "프랑스 그림책 작가 로랑 모로의 작품으로, "
        "사람들의 표정에 덧대어진 종이를 펼치면 그 속에 감추어진 생각을 살펴볼 수 있다. "
        "여러 사람들의 생각들을 통해 보는 이의 호기심을 자극하고 상상력을 높여준다."
    )
    
    curation_title = "아이의 생각을 넓혀주는 감정 그림책"
    
    try:
        # 카드뉴스 렌더링 호출
        card_img = generate_card_news(
            title=title,
            author=author,
            publisher=publisher,
            cover_url=cover_url,
            description=description,
            curation_title=curation_title
        )
        
        # 파일 저장
        output_path = "test_card_news_output.png"
        card_img.save(output_path)
        print(f"✅ 테스트 카드뉴스 렌더링 완료 및 저장 성공: {os.path.abspath(output_path)}")
        
    except Exception as e:
        print(f"❌ 렌더링 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rendering()
