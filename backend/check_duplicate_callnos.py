#!/usr/bin/env python
"""
중복된 청구기호 찾기 및 확인
"""

from collections import defaultdict
from supabase_client import supabase


def find_duplicate_callnos():
    """
    중복된 청구기호를 가진 책들 찾기
    
    Returns:
        {callno: [books]} 형태의 딕셔너리
    """
    print("🔍 중복된 청구기호 검색 중...")
    
    # 모든 childbook_items 조회
    response = supabase.table("childbook_items").select("id, isbn, title, pangyo_callno").execute()
    books = response.data
    
    # 청구기호별로 그룹화
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip():
            callno_groups[callno].append(book)
    
    # 중복된 청구기호만 필터링
    duplicates = {
        callno: books_list 
        for callno, books_list in callno_groups.items() 
        if len(books_list) > 1
    }
    
    print(f"\n✅ {len(duplicates)}개의 중복된 청구기호 발견")
    print(f"📊 총 {sum(len(books) for books in duplicates.values())}권의 책이 중복\n")
    
    # 상위 20개 출력
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("📖 중복이 가장 많은 청구기호 (상위 20개):")
    print("="*80)
    for i, (callno, books_list) in enumerate(sorted_duplicates[:20], 1):
        print(f"{i:2d}. {callno:30s} - {len(books_list):2d}권")
        for book in books_list[:3]:  # 처음 3권만 출력
            title = book.get("title", "")[:40]
            isbn = book.get("isbn", "없음")
            print(f"     └ [{isbn}] {title}")
        if len(books_list) > 3:
            print(f"     └ ... 외 {len(books_list) - 3}권")
    
    # ISBN이 있는 책들 통계
    books_with_isbn = sum(
        1 for books in duplicates.values() 
        for book in books 
        if book.get("isbn")
    )
    
    print(f"\n📈 통계:")
    print(f"  - 중복 청구기호: {len(duplicates)}개")
    print(f"  - 중복된 책: {sum(len(books) for books in duplicates.values())}권")
    print(f"  - ISBN이 있는 책: {books_with_isbn}권")
    
    return duplicates


if __name__ == "__main__":
    print("\n" + "="*80)
    print("📚 중복 청구기호 분석")
    print("="*80 + "\n")
    
    duplicates = find_duplicate_callnos()
    
    print("\n" + "="*80)
    print("✅ 분석 완료")
    print("="*80 + "\n")
