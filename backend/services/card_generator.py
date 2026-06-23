import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 로컬 폰트 경로 및 기본 색상 정의
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT_REGULAR = os.path.join(ASSETS_DIR, "SUIT-Regular.ttf")
FONT_BOLD = os.path.join(ASSETS_DIR, "SUIT-Bold.ttf")

# 로고 파일 경로
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "public", "logo.png")

# 색상 토큰 (책자리 프리미엄 UI-KIT 가이드 준수)
COLOR_PRIMARY = (245, 158, 11)        # 책자리 메인 브랜드 컬러 (#F59E0B)
COLOR_TEXT_PRIMARY = (17, 24, 39)    # 어두운 타이틀 (#111827)
COLOR_TEXT_MUTED = (75, 85, 99)      # 회색 본문 텍스트 (#4B5563)
COLOR_TEXT_SECONDARY = (107, 114, 128) # 보조 텍스트 (#6B7280)
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GRAY = (229, 231, 235)   # 구분선용 연회색 (#E5E7EB)

def download_image(url: str) -> Image.Image:
    """도서 표지 이미지 다운로드 (로컬 경로 및 HTTP 지원)"""
    try:
        if url.startswith("http://") or url.startswith("https://"):
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            if os.path.exists(url):
                return Image.open(url)
            raise FileNotFoundError(f"Local image file not found: {url}")
    except Exception as e:
        print(f"Error loading image from {url}: {e}")
        # 기본 대체 이미지 반환 (연노란 톤 바탕에 텍스트)
        img = Image.new("RGB", (400, 500), color=(250, 248, 225))
        draw = ImageDraw.Draw(img)
        draw.text((150, 240), "[No Image]", fill=COLOR_TEXT_MUTED)
        return img

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """텍스트가 최대 가로 길이를 넘지 않도록 글자 단위(Character-wrap)로 꼼꼼하게 줄바꿈 처리"""
    lines = []
    original_paragraphs = text.split('\n')
    
    for paragraph in original_paragraphs:
        if not paragraph:
            lines.append("")
            continue
            
        current_line = ""
        for char in paragraph:
            # 줄 시작 부분의 공백은 무시하여 비주얼 정렬 유지
            if not current_line and char == " ":
                continue
                
            test_line = current_line + char
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
            else:
                width = font.getsize(test_line)[0]
                
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
            
    return lines


def generate_card_news(
    title: str,
    author: str,
    publisher: str,
    cover_url: str,
    description: str,
    curation_title: str
) -> Image.Image:
    """
    1080x1080 정방형 카드뉴스 생성 (고급 오버랩 레이아웃)
    - 배경: 책자리 메인 브랜드 컬러 (#5F46FF)
    - 중앙 상단: 흰색 사각형 이너 카드 (텍스트 정보 배치)
    - 하단: 흰색 카드를 오버랩하여 아래로 돌출 배치되는 책 표지 이미지
    """
    # 1. 캔버스 생성 (메인 컬러 배경)
    card = Image.new("RGB", (1080, 1080), color=COLOR_PRIMARY)
    draw = ImageDraw.Draw(card)
    
    # 2. 중앙 상단 흰색 카드 영역 그리기 (가로 840px, 세로 640px)
    card_w, card_h = 840, 640
    cx1 = (1080 - card_w) // 2
    cy1 = 120
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h
    
    # 직각 모서리의 흰색 사각형 그리기 (요구사항 반영: radius 제거)
    draw.rectangle([cx1, cy1, cx2, cy2], fill=COLOR_WHITE)
    
    # 3. 우측 상단 책자리 로고 배치 (메인 컬러 배경 위에 투명 오버레이)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH)
            logo_w = 96
            logo_h = int(logo.height * (logo_w / logo.width))
            logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            # 흰색 카드 우측 상단 안쪽에 배치 (투명 알파 채널 적용, 안쪽 여백 30px)
            lx = cx2 - logo_w - 30
            ly = cy1 + 30
            if logo_resized.mode in ('RGBA', 'LA') or (logo_resized.mode == 'P' and 'transparency' in logo_resized.info):
                card.paste(logo_resized, (lx, ly), logo_resized)
            else:
                card.paste(logo_resized, (lx, ly))
        except Exception as e:
            print(f"Error loading logo: {e}")
            
    # 4. 폰트 로드 및 동적 제목 폰트 크기 조절
    title_size = 58
    if len(title) > 12:
        title_size = 44
        
    try:
        font_title = ImageFont.truetype(FONT_BOLD, title_size)
        font_info = ImageFont.truetype(FONT_REGULAR, 30)
        font_desc = ImageFont.truetype(FONT_REGULAR, 38)
    except IOError as e:
        print(f"Warning: Custom fonts not found. Using default. Error: {e}")
        font_title = ImageFont.load_default()
        font_info = ImageFont.load_default()
        font_desc = ImageFont.load_default()
 
    # 5. 흰색 카드 내부 - 얇은 탑 데코레이션 선 (구분선 - 위치를 소폭 위로 조절하여 여백 확보)
    line_w = 50
    lx1 = (1080 - line_w) // 2
    ly = cy1 + 60
    draw.line([lx1, ly, lx1 + line_w, ly], fill=COLOR_PRIMARY, width=6)
  
    # 6. 책 제목 렌더링 (중앙 정렬, 검은색)
    title_text = title
    if hasattr(font_title, 'getbbox'):
        title_bbox = font_title.getbbox(title_text)
        title_w = title_bbox[2] - title_bbox[0]
    else:
        title_w = font_title.getsize(title_text)[0]
        
    title_y = ly + 25
    title_x = (1080 - title_w) // 2
    draw.text((title_x, title_y), title_text, fill=COLOR_TEXT_PRIMARY, font=font_title)
    
    # 7. 출판사 정보만 렌더링 (디자인 간소화 및 가독성 증대)
    info_text = publisher or ""
    if hasattr(font_info, 'getbbox'):
        info_bbox = font_info.getbbox(info_text)
        info_w = info_bbox[2] - info_bbox[0]
    else:
        info_w = font_info.getsize(info_text)[0]
        
    info_y = title_y + title_size + 22
    info_x = (1080 - info_w) // 2
    draw.text((info_x, info_y), info_text, fill=COLOR_TEXT_SECONDARY, font=font_info)
    
    # 8. 설명글 렌더링 (흰색 카드 내부 배치, 아래로 내려 정렬)
    max_desc_width = 640
    desc_lines = wrap_text(description, font_desc, max_desc_width)
    
    desc_start_y = info_y + 50
    line_spacing = 22 # 행간 22 유지
    
    for i, line in enumerate(desc_lines[:3]): # 최대 3줄 렌더링
        if hasattr(font_desc, 'getbbox'):
            lw = font_desc.getbbox(line)[2] - font_desc.getbbox(line)[0]
            lh = font_desc.getbbox(line)[3] - font_desc.getbbox(line)[1]
        else:
            lw, lh = font_desc.getsize(line)
            
        lx = (1080 - lw) // 2
        ly = desc_start_y + i * (lh + line_spacing)
        draw.text((lx, ly), line, fill=COLOR_TEXT_MUTED, font=font_desc)
 
    # 9. 책 표지 이미지 배치 (2/3 크기 오버랩 구도)
    # 흰색 카드의 하단선(cy2 = 760)을 걸치면서 아래쪽 메인 컬러 배경 위로 튀어나오게 배치
    cover_img = download_image(cover_url)
    
    # 책 표지 크기: 높이 460px 조절
    max_height = 460
    scale = max_height / cover_img.height
    new_w = int(cover_img.width * scale)
    new_h = max_height
    
    cover_resized = cover_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 가로 중앙 정렬
    cover_x = (1080 - new_w) // 2
    # y = 540 부터 시작하게 하면, 540~760(220px)은 흰색 카드에 겹치고, 760~1000(240px)은 메인 컬러 배경 위로 튀어나옴
    cover_y = 540
    
    # 알파 투명도 채널 마스킹을 사용해 오버랩 페이스트
    if cover_resized.mode in ('RGBA', 'LA') or (cover_resized.mode == 'P' and 'transparency' in cover_resized.info):
        card.paste(cover_resized, (cover_x, cover_y), cover_resized.convert("RGBA"))
    else:
        card.paste(cover_resized, (cover_x, cover_y))
        
    return card
