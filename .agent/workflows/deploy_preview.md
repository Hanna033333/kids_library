---
description: 개발 변경사항의 로컬 빌드 및 프리뷰(Preview) 배포 전구간 자동 검증 워크플로우
---

# 🚀 /deploy-preview 배포 자동 검증 워크플로우

이 워크플로우는 사용자가 `/deploy-preview`를 호출했을 때, 로컬 개발 환경의 변경 사항이 Vercel 및 Render Preview 환경에 에러 없이 안전하게 배포되도록 사전 검증을 일괄 처리하고 배포를 진행하는 표준 지침입니다.

---

## 🛠️ [Phase 1] 로컬 사전 무결성 검증 (Build Check)

배포 전 프론트엔드 소스에 빌드 브레이킹 요소나 타입 에러가 없는지 로컬에서 신속히 검사합니다.

1. **Next.js 정적 타입 및 린트 검사**
   ```bash
   cd frontend && npm run lint
   ```
   * **검사 기준**: 문법 에러 및 미사용 변수 등으로 인한 컴파일 중단 요소를 사전에 차단합니다.

2. **로컬 프로덕션 빌드 테스트**
   ```bash
   cd frontend && npm run build
   ```
   * **검사 기준**: Next.js가 정상적으로 정적 HTML 및 SSR 페이지를 최적화하여 빌드해내는지 검증합니다.

---

## 🔒 [Phase 2] 보안 및 환경변수 정합성 검사 (Security Check)

보안 가이드라인을 준수하여 중요 크레덴셜 정보가 퍼블릭 Git 리포지토리에 유출되는 것을 차단합니다.

1. **민감 환경변수 파일 제외 여부 확인**
   - `.env.local` 또는 `.env`가 Git Staging 영역에 추가되어 있지 않은지 엄격히 확인합니다.
   - `.gitignore`에 `.env*` 패턴이 올바르게 잡혀있는지 체크합니다.

2. **클라이언트 사이드 환경변수 접두사 검증**
   - 프론트엔드(Next.js)에서 사용하는 모든 환경변수가 `NEXT_PUBLIC_` 접두사를 올바르게 취하고 있는지 점검합니다. (예: `NEXT_PUBLIC_SUPABASE_URL`)

---

## 🌐 [Phase 3] CORS 프리뷰 도메인 정규식 패턴 검사

Vercel Preview 환경이 배포될 때마다 도메인이 유동적으로 생성되므로, 백엔드 API 서버가 이를 차단하지 않도록 CORS 정규식 세팅을 준수하고 있는지 교차 검수합니다.

* **기준 코드 (`backend/main.py`)**:
  ```python
  allow_origin_regex=r"https://.*kids-library.*\.vercel\.app"
  ```
  * 위 정규식 구조가 백엔드 `CORSMiddleware`에 올바르게 적용되어 있는지 검사합니다.

---

## 🚀 [Phase 4] 깃허브 푸시 및 프리뷰 트리거 (Triggers)

위의 1~3단계 검증이 100% 통과되면, 변경 사항을 Git Staging에 올리고 프리뷰 브랜치로 푸시하도록 안내합니다.

```bash
# 변경 사항 확인 및 브랜치 체크
git status

# 커밋 및 원격 리포지토리 preview 브랜치로 푸시
git add .
git commit -m "feat: 프리뷰 검증 완료 및 배포 트리거"
git push origin preview
```

> [!TIP]
> 배포 성공 후 생성되는 Vercel Preview URL로 접속하여 프론트엔드와 백엔드의 실시간 연동성 및 모바일 한 손 조작성(Bottom navigation, 고대비 UI)이 훼손되지 않았는지 최종 점검하세요.
