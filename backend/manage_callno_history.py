#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
청구기호 히스토리 관리 스크립트
"""

from supabase_client import supabase
from datetime import datetime


def create_history_table():
    """
    히스토리 테이블 생성 (Python으로는 직접 생성 불가, SQL 실행 필요)
    """
    print("⚠️  히스토리 테이블은 Supabase SQL Editor에서 생성해야 합니다.")
    print("📝 migrations/add_callno_history.sql 파일을 실행하세요.\n")


def backup_current_callnos():
    """
    현재 청구기호를 히스토리에 백업
    """
    print("="*80)
    print("현재 청구기호 백업")
    print("="*80)
    
    # 모든 책의 현재 청구기호 조회
    response = supabase.table("childbook_items").select(
        "id, title, pangyo_callno, web_scraped_callno"
    ).execute()
    
    books = response.data
    
    print(f"\n총 {len(books)}권 조회 완료")
    
    # 히스토리에 백업
    backup_count = 0
    
    for book in books:
        book_id = book['id']
        pangyo_callno = book.get('pangyo_callno')
        web_scraped = book.get('web_scraped_callno')
        
        # pangyo_callno가 있으면 초기 데이터로 기록
        if pangyo_callno:
            try:
                supabase.table("callno_history").insert({
                    "book_id": book_id,
                    "old_callno": None,
                    "new_callno": pangyo_callno,
                    "change_type": "initial",
                    "notes": "Initial call number from database"
                }).execute()
                backup_count += 1
            except Exception as e:
                # 이미 존재하는 경우 무시
                pass
        
        # 웹 스크래핑으로 변경된 경우 기록
        if web_scraped and pangyo_callno and web_scraped != pangyo_callno:
            try:
                supabase.table("callno_history").insert({
                    "book_id": book_id,
                    "old_callno": pangyo_callno,
                    "new_callno": web_scraped,
                    "change_type": "web_scraping",
                    "notes": f"Updated from web scraping ({datetime.now().strftime('%Y-%m-%d')})"
                }).execute()
            except Exception as e:
                # 이미 존재하는 경우 무시
                pass
    
    print(f"✅ 백업 완료: {backup_count}건\n")


def view_history(book_id=None, limit=20):
    """
    청구기호 변경 이력 조회
    
    Args:
        book_id: 특정 책 ID (None이면 전체)
        limit: 조회할 최대 개수
    """
    print("="*80)
    print("청구기호 변경 이력")
    print("="*80)
    
    if book_id:
        # 특정 책의 이력
        response = supabase.table("callno_history").select(
            "*"
        ).eq("book_id", book_id).order("changed_at", desc=True).execute()
        
        print(f"\n책 ID {book_id}의 변경 이력:\n")
    else:
        # 전체 이력
        response = supabase.table("callno_history").select(
            "*"
        ).order("changed_at", desc=True).limit(limit).execute()
        
        print(f"\n최근 {limit}건의 변경 이력:\n")
    
    history = response.data
    
    if not history:
        print("변경 이력이 없습니다.")
        return
    
    for i, record in enumerate(history, 1):
        print(f"{i}. [ID: {record['book_id']}]")
        print(f"   변경 전: {record.get('old_callno', '없음')}")
        print(f"   변경 후: {record.get('new_callno', '없음')}")
        print(f"   변경 유형: {record.get('change_type')}")
        print(f"   변경 시간: {record.get('changed_at')}")
        print(f"   메모: {record.get('notes', '')}")
        print()


def get_book_history_summary():
    """
    청구기호 변경 통계
    """
    print("="*80)
    print("청구기호 변경 통계")
    print("="*80)
    
    # 전체 히스토리 조회
    response = supabase.table("callno_history").select("*").execute()
    history = response.data
    
    # 변경 유형별 통계
    type_counts = {}
    for record in history:
        change_type = record.get('change_type', 'unknown')
        type_counts[change_type] = type_counts.get(change_type, 0) + 1
    
    print(f"\n총 변경 기록: {len(history)}건\n")
    print("변경 유형별 통계:")
    for change_type, count in sorted(type_counts.items()):
        print(f"  - {change_type}: {count}건")
    
    print()


def main():
    """메인 실행"""
    print("\n" + "="*80)
    print("📚 청구기호 히스토리 관리")
    print("="*80 + "\n")
    
    # 테이블 존재 확인
    try:
        response = supabase.table("callno_history").select("id").limit(1).execute()
        print("✅ callno_history 테이블이 존재합니다.\n")
    except Exception as e:
        print("❌ callno_history 테이블이 없습니다.")
        print("\n다음 단계를 따라주세요:")
        print("1. Supabase SQL Editor 열기")
        print("2. migrations/add_callno_history.sql 파일 실행")
        print("3. 이 스크립트 다시 실행\n")
        return
    
    # 현재 데이터 백업
    backup_current_callnos()
    
    # 통계 출력
    get_book_history_summary()
    
    # 최근 변경 이력 출력
    view_history(limit=10)
    
    print("="*80)
    print("✅ 완료")
    print("="*80)


if __name__ == "__main__":
    main()
