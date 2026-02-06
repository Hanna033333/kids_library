from update_book_cover import update_book_cover
import time

def reload_target_images():
    """책 ID 10358, 10477의 표지 이미지를 재로드합니다."""
    target_ids = [11412]
    
    print(f"총 {len(target_ids)}권의 책 이미지를 업데이트합니다...")
    
    for book_id in target_ids:
        print(f"\nProcessing ID: {book_id}")
        update_book_cover(book_id)
        time.sleep(1) # API 호출 제한 고려

if __name__ == "__main__":
    reload_target_images()
