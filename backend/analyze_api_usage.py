"""
API 호출 추정 - 오늘 실행된 스크립트 분석
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

print("=" * 60)
print("📊 오늘 실행된 가능성이 있는 스크립트 분석")
print("=" * 60)
print(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# API를 호출하는 주요 스크립트들
api_calling_scripts = [
    "update_volumes_to_db.py",
    "update_not_owned_isbn.py", 
    "export_not_owned_books.py",
    "bulk_scan_volume.py",
    "add_volume_info_v3.py",
    "verify_no_callno.py",
    "api/books.py"  # FastAPI 엔드포인트
]

today = datetime.now().date()
yesterday = today - timedelta(days=1)

print("🔍 API 호출 스크립트 수정 시간:")
print()

recent_files = []

for script in api_calling_scripts:
    script_path = Path(script)
    if script_path.exists():
        mtime = datetime.fromtimestamp(script_path.stat().st_mtime)
        
        if mtime.date() >= yesterday:
            recent_files.append((script, mtime))
            marker = "🔴" if mtime.date() == today else "🟡"
            print(f"{marker} {script}")
            print(f"   수정 시간: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

if not recent_files:
    print("❌ 최근 24시간 내 수정된 스크립트 없음")
    print()

print("=" * 60)
print("💡 분석:")
print()
print("1. FastAPI 서버 (api/books.py):")
print("   - 사용자가 책 목록을 볼 때마다 대출 정보 조회")
print("   - 30분 캐시로 중복 호출 방지")
print("   - 하루 방문자가 많으면 500건 쉽게 초과 가능")
print()
print("2. 배치 스크립트:")
print("   - update_volumes_to_db.py: 전체 책 대출 정보 업데이트")
print("   - bulk_scan_volume.py: 대량 ISBN 조회")
print("   - 한 번 실행으로 수백 건 호출 가능")
print()
print("3. 추정:")
print("   - 오늘 아침부터 사용자 트래픽 증가")
print("   - 또는 배치 스크립트 실행으로 한도 소진")
print("   - 정확한 시점은 서버 로그 필요")
print("=" * 60)
