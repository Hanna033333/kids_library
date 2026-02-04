"""
간단한 API 사용량 추정
"""
from datetime import datetime

print("=" * 60)
print("API 호출 한도 초과 분석")
print("=" * 60)
print(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

print("📊 Data4Library API 제한:")
print("   - 일일 한도: 500건")
print("   - 리셋 시간: 자정 (추정)")
print()

print("🔍 주요 API 호출 경로:")
print()
print("1. 프론트엔드 (Vercel)")
print("   - 사용자가 책 목록 페이지 접속")
print("   - /api/books 엔드포인트 호출")
print("   - 백엔드 FastAPI로 대출 정보 요청")
print("   - 캐시: 30분 TTL")
print()
print("2. 백엔드 배치 스크립트")
print("   - update_volumes_to_db.py")
print("   - bulk_scan_volume.py")
print("   - 한 번에 수백 건 호출 가능")
print()

print("💡 추정 시나리오:")
print()
print("시나리오 A: 사용자 트래픽")
print("   - 오늘 방문자가 많았음")
print("   - 캐시 미스가 많이 발생")
print("   - 점진적으로 500건 도달")
print()
print("시나리오 B: 배치 실행")
print("   - 누군가 배치 스크립트 실행")
print("   - 단시간에 500건 소진")
print("   - 더 가능성 높음")
print()

print("🎯 정확한 시점 확인 방법:")
print("   1. Render 대시보드 → Logs 확인")
print("   2. 'bookExist' 검색")
print("   3. '500건 이상' 에러 메시지 첫 발생 시간")
print()
print("=" * 60)
