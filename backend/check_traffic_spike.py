"""
오늘 오후 2~3시 트래픽 분석 (GA4)
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta

# GA4 MCP 사용
print("=" * 60)
print("📊 오늘 오후 2~3시 트래픽 분석")
print("=" * 60)
print(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Property ID
PROPERTY_ID = "468159256"

print("🔍 분석 대상:")
print("   - 시간대: 오늘 14:00 ~ 15:00")
print("   - 지표: 활성 사용자, 페이지뷰, 이벤트")
print()

print("💡 GA4 MCP 도구를 사용하여 실시간 데이터 조회 필요")
print("   → mcp_analytics-mcp_run_realtime_report")
print()
print("=" * 60)
