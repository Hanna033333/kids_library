"""
API 호출 기록 확인 - 캐시 상태 및 마지막 성공 시간 확인
"""
import sys
sys.path.insert(0, '.')

from services.loan_status import LOAN_CACHE
from datetime import datetime

print("=" * 60)
print("📊 대출 정보 캐시 상태 확인")
print("=" * 60)
print()

if not LOAN_CACHE:
    print("❌ 캐시가 비어있습니다.")
    print("   - API 호출이 한 번도 성공하지 못했거나")
    print("   - 서버가 재시작되었습니다.")
else:
    print(f"✅ 캐시된 항목: {len(LOAN_CACHE)}개")
    print()
    
    # 가장 최근 캐시 항목 찾기
    latest_time = None
    latest_isbn = None
    
    for isbn, (data, timestamp) in LOAN_CACHE.items():
        if latest_time is None or timestamp > latest_time:
            latest_time = timestamp
            latest_isbn = isbn
    
    if latest_time:
        print(f"🕐 마지막 성공 API 호출:")
        print(f"   시간: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   ISBN: {latest_isbn}")
        print(f"   경과 시간: {datetime.now() - latest_time}")
        print()
        
        # 샘플 데이터 출력
        print("📋 캐시 샘플 (최근 5개):")
        items = list(LOAN_CACHE.items())[:5]
        for isbn, (data, timestamp) in items:
            print(f"   ISBN: {isbn}")
            print(f"   상태: {data.get('status')}")
            print(f"   시간: {timestamp.strftime('%H:%M:%S')}")
            print()

print("=" * 60)
