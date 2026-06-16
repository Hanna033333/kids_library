

# [배포 규칙] Git Push 및 배포 필수 프로세스

## 🚨 절대 원칙 (예외 없음)

**`git push` 명령을 실행하기 전, 반드시 아래 워크플로우를 읽고 모든 단계를 완료해야 한다.**
이 규칙을 건너뛰는 것은 어떠한 경우에도 허용되지 않는다.

---

## 🔒 브랜치별 필수 워크플로우

### Preview 배포 (preview 브랜치)
- **대상**: 기능 개발, 버그 수정, 텍스트 변경 등 모든 코드 변경
- **필수 실행**: `.agent/workflows/deploy_preview.md` 전 단계 완료 후 push
- **push 대상**: `preview` 브랜치 (절대 `main` 아님)

### Production 배포 (main 브랜치)
- **대상**: dev에서 충분히 검증이 완료된 변경사항
- **필수 실행**: `.agent/workflows/deploy_prod.md` 전 단계 완료 후 push
- **push 대상**: `main` 브랜치
- **추가 조건**: 반드시 사용자에게 승인을 받은 후에만 main에 push

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

5. **브랜치 확인 후 push**
   ```bash
   git branch  # 현재 브랜치 반드시 확인
   git push origin preview  # preview는 반드시 preview로
   ```

---

## ❌ 절대 금지 사항

- 워크플로우 파일을 읽지 않고 push 금지
- 사용자 승인 없이 `main` 브랜치로 직접 push 금지
- "간단한 변경이라서" 라는 이유로 검증 단계 생략 금지
- 빌드 에러 미확인 상태로 push 금지

