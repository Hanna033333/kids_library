# Vercel 환경 변수 설정 가이드

## 🚨 중요: 배포 전 필수 작업!

Vercel에서 환경 변수를 설정하지 않으면 빌드가 실패합니다.

---

## 1단계: Vercel Dashboard 접속

1. https://vercel.com 접속
2. 프로젝트 선택 (kids-library)

---

## 2단계: 환경 변수 추가

1. **Settings** 탭 클릭
2. 왼쪽 메뉴에서 **Environment Variables** 클릭
3. 아래 3개 변수를 **하나씩** 추가:

### 변수 1: NEXT_PUBLIC_SUPABASE_URL
- **Key**: `NEXT_PUBLIC_SUPABASE_URL`
- **Value**: `.env.local` 파일에서 복사
- **Environment**: Production, Preview, Development 모두 체크 ✅

### 변수 2: NEXT_PUBLIC_SUPABASE_ANON_KEY
- **Key**: `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Value**: `.env.local` 파일에서 복사
- **Environment**: Production, Preview, Development 모두 체크 ✅

### 변수 3: NEXT_PUBLIC_API_URL
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://kids-library-7gj8.onrender.com`
- **Environment**: Production, Preview, Development 모두 체크 ✅

---

## 3단계: 재배포 트리거

환경 변수 추가 후:

1. **Deployments** 탭으로 이동
2. 최신 배포 찾기 (방금 push한 것)
3. **Redeploy** 버튼 클릭
4. **Redeploy** 확인

---

## 4단계: 배포 확인

1. 배포 로그에서 "Building..." 확인
2. 약 2~3분 대기
3. "Ready" 상태 확인
4. 프로덕션 URL 접속하여 테스트

---

## 예상 결과

✅ 첫 방문: **0.3초** 이내 화면 표시
✅ 책 목록: 즉시 로드
✅ 대출 상태: Progressive Loading ("탁탁탁")
✅ Render 백엔드: 검색할 때만 호출

---

## 문제 발생 시

### 빌드 실패
- 환경 변수가 제대로 설정되었는지 확인
- Supabase URL/Key가 정확한지 확인

### 데이터 안 보임
- RLS 정책이 설정되었는지 확인 (`supabase_rls_setup.sql`)
- 브라우저 콘솔에서 에러 확인
