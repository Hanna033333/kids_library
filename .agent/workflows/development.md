---
description: 책방구 개발 시 기본 참고 문서
---

# 책방구 개발 워크플로우

책방구 프로젝트를 개발할 때는 항상 다음 문서를 참고하세요:

## 1. 프로젝트 계획서 확인
먼저 `project_plan.md`를 확인하여 프로젝트의 전체 구조와 원칙을 파악합니다.

**주요 확인 사항:**
- 프로젝트 목표 및 범위 (Scope)
- 기술 스택 (Frontend: Next.js, Backend: FastAPI)
- API 설계 및 엔드포인트
- 데이터베이스 구조 (Supabase)
- 성능 최적화 전략
- 운영 원칙 ("데이터는 완벽하지 않아도 공개", "고칠 수 있는 구조 우선")

## 2. 개발 원칙
- **데이터 정확도보다 접근성 우선**
- **기능 추가보다 "헷갈리지 않음" 우선**
- **자동화보다 검증 가능한 흐름 유지**

## 3. 주요 디렉토리 구조
```
kids library/
├── frontend/          # Next.js 프론트엔드
├── backend/           # FastAPI 백엔드
└── project_plan.md    # 프로젝트 계획서 (항상 참고)
```

## 4. 개발 시작 전 체크리스트
- [ ] `project_plan.md`에서 관련 섹션 확인
- [ ] 변경사항이 프로젝트 범위(Scope)에 포함되는지 확인
- [ ] API 설계 원칙 준수 여부 확인
- [ ] 성능 최적화 전략 고려 (캐싱, 무한 스크롤 등)

## 5. project_plan.md 자동 업데이트 규칙

개발 중 다음과 같은 변경사항이 발생하면 **자동으로 `project_plan.md`를 업데이트**합니다:

### 업데이트가 필요한 경우:
- ✅ **새로운 API 엔드포인트 추가/수정/삭제**
  - 섹션 6 (API 설계) 업데이트
- ✅ **데이터베이스 스키마 변경** (테이블, 컬럼 추가/수정)
  - 섹션 7-3 (주요 테이블 구조) 업데이트
- ✅ **기술 스택 변경** (새로운 라이브러리, 프레임워크 추가)
  - 섹션 5 (기술 스택) 업데이트
- ✅ **기능 범위(Scope) 변경** (새 기능 추가/제거)
  - 섹션 2 (현재 포함 범위) 업데이트
- ✅ **성능 최적화 전략 변경** (캐싱 정책, 로딩 방식 등)
  - 섹션 8 (성능 최적화 전략) 업데이트
- ✅ **외부 API 추가/변경**
  - 섹션 5 (기술 스택 - External APIs) 업데이트
- ✅ **운영 원칙 또는 데이터 정책 변경**
  - 섹션 4 (운영 원칙) 또는 섹션 7 (데이터 시스템 구조) 업데이트
- ✅ **알려진 제약사항 또는 이슈 발견**
  - 섹션 9 (알려진 제약사항 및 이슈) 업데이트

### 업데이트 프로세스:
1. 변경사항 구현 완료 후
2. `project_plan.md`의 관련 섹션 자동 업데이트
3. 변경 내용을 사용자에게 간단히 요약 보고

### 업데이트가 불필요한 경우:
- ❌ 단순 버그 수정
- ❌ UI 스타일 미세 조정
- ❌ 코드 리팩토링 (기능 변경 없음)
- ❌ 문서 오타 수정

## 6. 호스팅 환경

### Frontend (Vercel)
| 환경 | URL | 브랜치 |
|------|-----|--------|
| **Preview (개발)** | `https://kids-library-git-dev-hannas-projects-f9ed017f.vercel.app` | `dev` |
| **Production** | `https://checkjari.com` | `main` |

### Backend (Render)
| 환경 | URL |
|------|-----|
| **Production** | `https://kids-library-7gj8.onrender.com` |

### 환경변수
- `NEXT_PUBLIC_API_URL`: Backend API URL (기본: `http://127.0.0.1:8000`)
- 자세한 내용은 [supabase_env.md](./supabase_env.md) 참고

### 기타 참고
- **캐싱**: 대출 상태 API는 5분 캐시
- **페이지네이션**: 무한 스크롤, 24권씩 로딩
<<<<<<< Updated upstream:.agent/workflows/development.md
=======

## 7. 배포 원칙

### 배포 순서
1. **개발(Preview) 배포** → `dev` 브랜치 push
2. **검증** → Preview URL에서 이슈 없는지 확인
3. **프로덕션 배포** → 검증 완료 후 `main` 브랜치 push

### 배포 명령어
```bash
# 개발 배포 (dev 브랜치)
git checkout dev
git merge main
git push origin dev

# 프로덕션 배포 (검증 후)
git checkout main
git push origin main
```

> [!IMPORTANT]
> **절대 main에 바로 push하지 않기!** Preview에서 검증 후 Production 배포.

## 8. Supabase 환경변수 가이드
DB 업데이트 스크립트 작성 시 환경변수 설정은 [supabase_env.md](./supabase_env.md)를 참고하세요.
>>>>>>> Stashed changes:.agent/skills/development/development.md
