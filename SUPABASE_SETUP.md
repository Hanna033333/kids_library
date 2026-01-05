# Supabase 최적화 구현 가이드

## 1단계: Supabase 환경 변수 확인

Supabase Dashboard에서 다음 정보를 복사하세요:

1. **Project URL**: Settings → API → Project URL
2. **Anon (public) Key**: Settings → API → Project API keys → anon public

## 2단계: 환경 변수 설정

### 로컬 개발
`frontend/.env.local` 파일 생성:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=https://kids-library-7gj8.onrender.com
```

### Vercel 배포
1. Vercel Dashboard → 프로젝트 선택
2. Settings → Environment Variables
3. 위 3개 변수 추가 (Production, Preview, Development 모두 체크)

## 3단계: RLS 보안 설정

`supabase_rls_setup.sql` 파일의 SQL을 Supabase Dashboard → SQL Editor에서 실행

## 4단계: 패키지 설치 ✅ (완료됨)

~~이미 설치 완료되었습니다. 건너뛰세요.~~

```bash
# 이미 실행됨
cd frontend
npm install @supabase/supabase-js
```

## 5단계: 로컬 테스트

```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속 후:
1. 개발자 도구 → Network 탭 확인
2. Supabase URL로 요청 가는지 확인
3. 책 목록이 즉시 표시되는지 확인

## 6단계: 보안 테스트

브라우저 콘솔에서 `supabase_rls_setup.sql`의 테스트 코드 실행

## 7단계: Vercel 배포

```bash
git add .
git commit -m "feat: Add Supabase direct query optimization"
git push origin main
```

Vercel이 자동으로 배포합니다.

## 8단계: 성능 확인

1. 첫 방문: 0.3초 이내 화면 표시 확인
2. Network 탭: Render 백엔드 호출 없는지 확인
3. Lighthouse: Performance 점수 90+ 확인
