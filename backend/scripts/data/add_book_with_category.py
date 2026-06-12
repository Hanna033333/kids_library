"""
신규 도서 추가 시 AI 기반 카테고리 자동 분류 헬퍼 함수

이 모듈은 신규 도서를 DB에 추가할 때 자동으로 적절한 카테고리를 할당합니다.
"""
import asyncio
import sys
import os

# 현재 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Optional
from services.categorize_books import (
    get_book_description,
    categorize_book_with_content,
    VALID_CATEGORIES
)
from supabase_client import supabase


async def add_book_with_auto_category(book_data: Dict) -> Dict:
    """
    신규 도서를 DB에 추가하면서 AI로 카테고리를 자동 분류합니다.
    
    Args:
        book_data: 도서 정보 딕셔너리
            - title (필수): 도서 제목
            - author: 저자
            - publisher: 출판사
            - isbn: ISBN
            - category: 기존 카테고리 (없거나 유효하지 않으면 AI로 분류)
            - 기타 필드들...
    
    Returns:
        추가된 도서 정보 (category 포함)
    """
    title = book_data.get('title')
    if not title:
        raise ValueError("도서 제목(title)은 필수입니다.")
    
    # 1. 기존 카테고리 확인
    existing_category = book_data.get('category', '').strip()
    
    # 2. 카테고리가 없거나 유효하지 않으면 AI로 분류
    if not existing_category or existing_category not in VALID_CATEGORIES:
        print(f"📖 '{title}': 카테고리 자동 분류 시작...")
        
        # 2-1. ISBN이 있으면 알라딘 API로 책 소개 가져오기
        description = None
        isbn = book_data.get('isbn')
        
        if isbn:
            print(f"   🔍 알라딘 API로 책 소개 조회 중...")
            description = await get_book_description(isbn)
            
            if description:
                # DB에 description도 함께 저장
                book_data['description'] = description
                print(f"   ✅ 책 소개 조회 완료")
            else:
                print(f"   ⚠️ 책 소개를 가져올 수 없습니다.")
        
        # 2-2. Gemini로 카테고리 분류
        print(f"   🤖 Gemini로 카테고리 분류 중...")
        auto_category = categorize_book_with_content(
            title=title,
            author=book_data.get('author'),
            publisher=book_data.get('publisher'),
            description=description
        )
        
        book_data['category'] = auto_category
        print(f"   ✨ 카테고리 자동 분류 완료: '{auto_category}'")
    else:
        print(f"📖 '{title}': 기존 카테고리 '{existing_category}' 사용")
    
    # 3. DB에 저장
    try:
        response = supabase.table('childbook_items').insert(book_data).execute()
        
        if response.data:
            saved_book = response.data[0]
            print(f"✅ '{title}' DB 저장 완료 (카테고리: {saved_book.get('category')})")
            return saved_book
        else:
            raise Exception("DB 저장 실패: 응답 데이터 없음")
            
    except Exception as e:
        print(f"❌ '{title}' DB 저장 실패: {e}")
        raise


async def update_book_category(book_id: int, force_recategorize: bool = False) -> Optional[str]:
    """
    기존 도서의 카테고리를 AI로 재분류합니다.
    
    Args:
        book_id: 도서 ID
        force_recategorize: True이면 기존 카테고리가 있어도 재분류
    
    Returns:
        새로운 카테고리 또는 None
    """
    # 1. 도서 정보 조회
    response = supabase.table('childbook_items').select('*').eq('id', book_id).execute()
    
    if not response.data:
        print(f"❌ ID {book_id} 도서를 찾을 수 없습니다.")
        return None
    
    book = response.data[0]
    title = book.get('title')
    existing_category = book.get('category', '').strip()
    
    # 2. 재분류 필요 여부 확인
    if not force_recategorize and existing_category in VALID_CATEGORIES:
        print(f"📖 '{title}': 유효한 카테고리 '{existing_category}' 이미 존재")
        return existing_category
    
    print(f"📖 '{title}': 카테고리 재분류 시작...")
    
    # 3. 책 소개 가져오기 (DB에 없으면 알라딘 API 호출)
    description = book.get('description')
    isbn = book.get('isbn')
    
    if not description and isbn:
        print(f"   🔍 알라딘 API로 책 소개 조회 중...")
        description = await get_book_description(isbn)
        
        if description:
            # DB에 description 저장
            supabase.table('childbook_items').update({
                'description': description
            }).eq('id', book_id).execute()
            print(f"   ✅ 책 소개 조회 및 저장 완료")
    
    # 4. Gemini로 카테고리 분류
    print(f"   🤖 Gemini로 카테고리 분류 중...")
    new_category = categorize_book_with_content(
        title=title,
        author=book.get('author'),
        publisher=book.get('publisher'),
        description=description
    )
    
    # 5. DB 업데이트
    if new_category != existing_category:
        supabase.table('childbook_items').update({
            'category': new_category
        }).eq('id', book_id).execute()
        print(f"   ✅ 카테고리 업데이트: '{existing_category}' → '{new_category}'")
    else:
        print(f"   ℹ️ 카테고리 변경 없음: '{new_category}'")
    
    return new_category
