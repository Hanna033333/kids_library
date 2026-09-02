

# [배포 규칙] Git Push 및 배포 필수 프로세스

## 🚨 절대 원칙 (예외 없음)

**`git push` 명령을 실행하기 전, 반드시 아래 워크플로우를 읽고 모든 단계를 완료해야 한다.**
이 규칙을 건너뛰는 것은 어떠한 경우에도 허용되지 않는다.

---

## 🔒 브랜치별 필수 워크플로우

### Preview 배포 (dev 브랜치)
- **대상**: 기능 개발, 버그 수정, 텍스트 변경 등 모든 코드 변경
- **필수 실행**: `.agent/workflows/deploy_preview.md` 전 단계 완료 후 push
- **push 대상**: `dev` 브랜치 (절대 `main` 아님)

### Production 배포 (main 브랜치)
- **대상**: dev에서 충분히 검증이 완료된 변경사항
- **필수 실행**: `.agent/workflows/deploy_prod.md` 전 단계 완료 후 push
- **push 대상**: `main` 브랜치
- **추가 조건**: 반드시 사용자에게 승인을 받은 후에만 main에 push (단, 사용자가 `/deploy_prod` 또는 `/deploy_preview` 커맨드를 직접 호출한 경우 검증 100% Pass 즉시 자동 배포 실행)
- **백엔드 배포 필수**: `backend/` 소스코드 수정이 포함된 경우, `git push` 후 반드시 `./deploy_to_aws.sh`를 실행하여 AWS Lightsail 백엔드를 동기화하고 `fastapi.service`를 재시작해야 함.

---

## ✅ 배포 전 체크리스트 (매번 실행)

1. **워크플로우 파일 읽기** (view_file 도구로 확인)
   - preview: `.agent/workflows/deploy_preview.md`
   - production: `.agent/workflows/deploy_prod.md`

2. **Phase 1: 로컬 빌드 검증**
   ```bash
   cd frontend && npm run lint
   cd frontend && npm run build
   ```

3. **Phase 2: 보안 확인**
   - `.env.local` / `.env` 가 staging에 없는지 확인

4. **Phase 3: CORS 정규식 확인** (backend/main.py)

5. **큐레이션 도서 수 검증 (taxonomy/weekly_schedule 변경 시)**
   - taxonomy 또는 weekly_schedule을 변경한 경우 아래 스크립트를 실행하여 모든 태그 7권 이상 확인:
   ```bash
   python3 backend/scripts/check_curation_health.py
   ```
   - ❌ 빨간 항목(7권 미만)이 있으면 도서 추가 완료 후 push

6. **브랜치 확인 후 push**
   ```bash
   git branch  # 현재 브랜치 반드시 확인
   git push origin dev  # dev는 반드시 dev로
   ```
7. **모바일 성능 및 가독성 사전 점검**:
   - 모바일 최적화를 위해 Next.js 빌드 산출물 중 이미지 크기와 JS 번들 크기가 과도하게 커지지 않았는지 확인한다.
   - 로컬 테스트 환경에서 Chrome DevTools 모바일 에뮬레이터를 켜고, UI 깨짐이나 수평 스크롤이 강제로 발생하는 컴포넌트가 없는지 사전 확인한다.

---

## ❌ 절대 금지 사항

- 워크플로우 파일을 읽지 않고 push 금지
- 사용자 승인 없이 `main` 브랜치로 직접 push 금지
- "간단한 변경이라서" 라는 이유로 검증 단계 생략 금지
- 빌드 에러 미확인 상태로 push 금지
- **`git diff` 없이 `git add .` 실행 절대 금지** (아래 규칙 참고)

---

## 🚨 `git add .` 전 `git diff` 의무 검토 규칙 (재발 방지 — 절대 준수)

**사고 사례**: 이전 세션의 Claude가 `MyPageClient.tsx`의 `useEffect` 의존성 배열을 `[user]` → `[user?.id]`로 변경한 뒤 커밋하지 않고 종료했다. 다음 세션에서 `/deploy-preview` 실행 시 `git add .`가 이 미검토 변경사항을 통째로 커밋하면서 "내 책장" 이미지가 무한 로딩 상태로 깨지는 회귀가 발생했다.

**규칙**:
1. **`git add .` 전 반드시 `git diff`를 실행**하여 변경 내용을 육안으로 전부 확인한다.
2. **이 대화 세션에서 직접 수정하지 않은 변경사항**이 diff에 포함되어 있으면, 해당 파일을 `git restore <file>`로 되돌린 뒤 커밋한다.
3. 특히 `useEffect` 의존성 배열, hook 순서, 컴포넌트 구조 등 **동작에 민감한 코드가 포함된 변경사항은 반드시 사용자에게 보고 후 확인을 받는다**.
4. `git status`만으로는 부족하다 — 어떤 파일이 바뀌었는지는 알 수 있지만, **무엇이 어떻게 바뀌었는지는 `git diff`로만 확인 가능**하다.

