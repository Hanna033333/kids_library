"""
로컬에서 실행한 스크립트 중 API를 많이 호출한 것 찾기
"""
import os
from pathlib import Path
from datetime import datetime, timedelta

print("=" * 60)
print("🔍 최근 실행된 API 호출 스크립트 추적")
print("=" * 60)
print()

# API를 대량 호출하는 스크립트들
heavy_scripts = {
    "update_volumes_to_db.py": "전체 책 대출 정보 업데이트 (수백 건)",
    "bulk_scan_volume.py": "대량 ISBN 조회 (수백 건)",
    "add_volume_info_v3.py": "권차 정보 추가 (수백 건)",
    "verify_no_callno.py": "청구기호 없는 책 검증",
    "export_not_owned_books.py": "미소장 도서 추출",
    "update_not_owned_isbn.py": "미소장 도서 ISBN 재조회"
}

print("📊 대량 API 호출 스크립트 수정 시간:")
print()

today = datetime.now()
recent_executions = []

for script, description in heavy_scripts.items():
    script_path = Path(script)
    if script_path.exists():
        mtime = datetime.fromtimestamp(script_path.stat().st_mtime)
        days_ago = (today - mtime).days
        hours_ago = (today - mtime).total_seconds() / 3600
        
        # 최근 7일 이내 수정된 것만
        if days_ago <= 7:
            recent_executions.append((script, description, mtime, hours_ago))

# 시간순 정렬
recent_executions.sort(key=lambda x: x[2], reverse=True)

if recent_executions:
    for script, desc, mtime, hours_ago in recent_executions:
        if hours_ago < 24:
            marker = "🔴 오늘"
            time_str = f"{int(hours_ago)}시간 전"
        elif hours_ago < 48:
            marker = "🟡 어제"
            time_str = "어제"
        else:
            marker = "⚪"
            time_str = f"{int(hours_ago/24)}일 전"
        
        print(f"{marker} {script}")
        print(f"   설명: {desc}")
        print(f"   수정: {time_str} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        print()
else:
    print("❌ 최근 7일 내 수정된 스크립트 없음")
    print()

print("=" * 60)
print("💡 결론:")
print()
print("1. 위 스크립트 중 오늘/어제 수정된 것이 있다면")
print("   → 해당 스크립트를 실행했을 가능성 높음")
print()
print("2. 모두 오래 전이라면")
print("   → API 한도가 이미 며칠 전부터 막혀있었을 수도")
print("   → 사용자들이 '미소장'을 계속 봤을 가능성")
print()
print("3. 정확한 확인 방법:")
print("   → 실제로 언제부터 '미소장'이 보였는지 기억해보기")
print("   → 오늘 갑자기 발견했다면 오늘 한도 초과")
print("   → 며칠 전부터였다면 이미 오래 전 초과")
print("=" * 60)
