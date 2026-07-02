# Google Cloud 예산 알림 설정 가이드

## 1. 예산 생성 (필수!)

1. [Google Cloud Console - Billing](https://console.cloud.google.com/billing) 접속
2. 왼쪽 메뉴에서 **"Budgets & alerts"** 클릭
3. **"CREATE BUDGET"** 클릭

### 예산 설정 예시:
- **Name**: "Gemini API Monthly Budget"
- **Projects**: 해당 프로젝트 선택
- **Services**: "Generative Language API" 선택
- **Budget amount**: 
  - **Monthly**: $5 (권장) 또는 $10
  - Type: Specified amount

### 알림 설정:
- **50%** 사용 시 이메일 알림
- **90%** 사용 시 이메일 알림
- **100%** 사용 시 이메일 알림 + Pub/Sub (선택)

## 2. 비용 예상 (참고)

### Gemini 1.5 Flash (권장 모델)
- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

### 예상 비용 계산:
- 책 1권당 평균 토큰: ~2,000 tokens (input) + ~50 tokens (output)
- 100권 처리 시: 약 $0.02 (2센트)
- 1,000권 처리 시: 약 $0.20 (20센트)

**월 $5 예산이면 약 25,000권 처리 가능** (실제로는 훨씬 적게 사용)

## 3. API 할당량 제한 설정 (선택)

1. [API Quotas](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas) 접속
2. "Requests per minute per project" 찾기
3. **Edit Quotas** 클릭
4. 원하는 한도 설정 (예: 100 RPM)

## 4. 자동 중단 설정 (고급)

Pub/Sub + Cloud Functions로 예산 초과 시 API 키 자동 비활성화 가능
(필요하면 별도 구현 가이드 제공)
