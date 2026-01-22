---
description: 개발(Dev) 사이트 상태 및 콘텐츠 정책 준수 여부 검증
---
1. 백엔드 상태 진단 스크립트 실행 (Dev 환경)
> [!NOTE]
> DB 연결을 위해 로컬 환경변수가 필요합니다.
// turbo
python backend/health_check.py dev
