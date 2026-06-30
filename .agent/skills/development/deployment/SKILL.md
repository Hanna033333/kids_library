---
name: deployment-troubleshooting
description: Kids Library 프로젝트의 Vercel(Next.js) 및 AWS Lightsail(FastAPI) 배포 문제 해결 가이드
---

# 🚀 배포 가이드 및 트러블슈팅 (Kids Library)

이 문서는 프로젝트 배포 과정에서 반드시 확인해야 할 표준 절차와 과거 발생한 주요 이슈의 해결 방법을 기록합니다.

## 📖 표준 배포 가이드 (Happy Path)

새로운 기능을 배포할 때는 다음 절차를 준수하여 장애를 방지합니다.

### 0단계: 브랜치 격리 및 배포 통제 (Pre-deployment Isolation Check)
- [ ] **브랜치 명세 확인**: `git branch` 또는 `git status`를 호출하여 현재 로컬 브랜치명을 확실하게 검증합니다.
- [ ] **상용 차단 및 격리**: 로컬 브랜치가 `main` 또는 `master`일 때, 사용자의 동의나 수동 승인 없이는 원격 푸시를 절대로 수행하지 않습니다.
- [ ] **프리뷰 격리 수립**: 프리뷰 QA용 릴리즈는 반드시 `dev` 또는 `feature/` 접두사를 가지는 임시 분기 브랜치를 로컬에서 `git checkout -b`로 생성하여 타겟팅합니다.
- [ ] **수동 승인 필수**: 프리뷰 QA 리포트를 작성하고, 사용자에게 변경 사안 및 정렬/UX 정합성 등의 Gap 피드백을 공유하여 상용 릴리즈 서면 컨펌을 확실하게 확보합니다.

### 1단계: 로컬 검증 (Pre-check)
- [ ] 프론트엔드 빌드 테스트: `cd frontend && npm run build` (오류 없이 완료되는지 확인)
- [ ] 백엔드 신규 라이브러리 확인: `backend/requirements.txt`에 신규 추가된 라이브러리가 AWS Lightsail에서 정상 설치되는지 확인.

### 2단계: Vercel 배포 설정 (Frontend)
- **Root Directory**: 반드시 `frontend`로 설정되어 있어야 함.
- **Framework Preset**: 반드시 `Next.js`로 설정.
- **Environment Variables**: 모든 Supabase/API 변수는 `NEXT_PUBLIC_` 접두사를 사용.
- **Node.js Version**: `package.json`의 엔진 설정과 Vercel 설정을 일치시킴 (현재 18+ 권장).
- **`NEXT_PUBLIC_API_URL`**: `https://api.checkjari.com` 으로 반드시 설정되어 있어야 함 (미설정 시 로컬호스트로 폴백되어 대출 상태 조회 불가).

### 3단계: AWS Lightsail 배포 설정 (Backend)
- **백엔드 도메인**: `https://api.checkjari.com`
- **서버**: AWS Lightsail 인스턴스
- **프로세스 관리**: PM2 또는 systemd로 uvicorn 실행
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
- **환경변수**: AWS Lightsail 인스턴스 내 `.env` 파일로 관리 (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DATA4LIBRARY_KEY` 등)
- **HTTPS**: Nginx 리버스 프록시 + Let's Encrypt SSL 인증서로 처리

---

## 🛠️ 트러블슈팅 가이드 (Troubleshooting)

과거에 발생했던 주요 이슈들에 대한 해결 방법입니다.

## 1. Vercel (Frontend - Next.js)

### ❌ 404: NOT_FOUND 오류
*   **증상**: 빌드는 성공했으나 접속 시 Vercel 404 페이지가 뜸.
*   **원인**: 
    1. Vercel 대시보드 설정의 **Framework Preset**이 `Vite`로 잘못 설정되어 있어 Next.js 빌드 결과물을 인식하지 못함.
    2. 모노레포 구조에서 **Root Directory** 설정이 `./`로 되어 있어 `frontend` 폴더 내부의 소스를 찾지 못함.
*   **해결 방법**:
    1. Vercel Settings > General > **Framework Preset**을 `Next.js`로 변경.
    2. Vercel Settings > General > **Root Directory**를 `frontend`로 지정.
    3. (주의) 루트 폴더의 `vercel.json`은 가급적 삭제하고 Vercel의 Zero-Config 설정을 따르는 것이 안전함.

### ❌ 빌드 시 "vite: command not found"
*   **증상**: 빌드 로그에서 `vite build`를 실행하려다 실패함.
*   **원인**: 프로젝트는 Next.js인데 Vercel 설정이 Vite로 되어 있어 `package.json`의 스크립트 대신 Vercel의 기본 Vite 명령어를 실행함.
*   **해결 방법**: Framework Preset을 `Next.js`로 변경하면 해결됨.

### 🔑 환경 변수 인식 문제
*   **증상**: 클라이언트 사이드에서 API 호출이나 Supabase 연결이 안 됨.
*   **원인**: Next.js는 `NEXT_PUBLIC_` 접두사가 붙지 않은 환경 변수를 보안상 브라우저에 노출하지 않음.
*   **해결 방법**: 모든 클라이언트 사용 변수명을 `VITE_SUPABASE_URL` ➡️ `NEXT_PUBLIC_SUPABASE_URL` 등으로 변경.

### 🌐 Vercel 커스텀 도메인 소유권 인증 문제 (`Verification Needed` / `This domain is linked to another Vercel account.`)
*   **증상**: 상용 도메인(`checkjari.com`) 접속 시 최신 배포본이 적용되지 않고 오래된 버전(예: 5일 전 버전)이 계속 서빙되거나, Vercel 대시보드 Domains 설정에서 도메인 상태가 빨간색 경고(`Verification Needed`)로 뜸.
*   **원인**: 
    1. **네임서버(DNS) 혼용**: AWS 마이그레이션 등을 위해 도메인 관리처(가비아 등)에서 네임서버 설정에 Vercel 네임서버 외에 **AWS 네임서버를 추가 기입/혼용**하여 Vercel의 네임서버 자동 인증 위임이 깨진 경우.
    2. **도메인 강제 재등록**: 대시보드에서 도메인을 새롭게 추가(`Add Existing`)하려 할 때, Vercel 시스템 내부적으로 타계정/타프로젝트와의 소유권 충돌이 발생한 경우.
*   **해결 방법**:
    1. Vercel 도메인 탭에서 제공하는 본인 확인용 **`TXT` 레코드값**(`_vercel` / `vc-domain-verify=...`)을 복사합니다.
    2. 도메인 대행사(가비아, 후이즈 등)의 **SPF(TXT) 레코드 관리** 혹은 **고급 네임서버 설정** 메뉴로 진입합니다.
    3. 복사한 호스트명(`_vercel`)과 TXT 값(`vc-domain-verify=...`)을 입력하고 **신청/저장**합니다. (루트 도메인용 및 `www`용 둘 다 등록하는 것을 권장)
    4. 약 1~2분 대기 후 Vercel 대시보드에서 **`Refresh`**를 누르면 초록색 **`Valid Configuration`**으로 상태가 복구되며 최신 배포가 정상 전파됩니다.

---

## 2. AWS Lightsail (Backend - FastAPI)

### ❌ 빌드/설치 실패 (라이브러리 의존성)
*   **증상**: `pip install` 과정에서 C 확장 라이브러리 컴파일 오류 발생.
*   **원인**: 특정 라이브러리가 컴파일 환경을 필요로 함.
*   **해결 방법**: 컴파일이 필요 없는 대체 라이브러리로 교체하거나 `requirements.txt`에서 해당 라이브러리 제거.

### 🌐 CORS (Cross-Origin Resource Sharing) 문제
*   **증상**: 프론트엔드에서 백엔드 API 호출 시 브라우저에서 차단됨.
*   **원인**: Vercel의 Preview 도메인은 매번 바뀌는데, 백엔드의 `allow_origins` 리스트에 포함되지 않음.
*   **해결 방법**: 
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://checkjari.com", ...],
        allow_origin_regex=r"https://kids-library.*\.vercel\.app", # 정규식 추가
        ...
    )
    ```

### 🐍 Python Import 경로 문제
*   **증상**: 배포 환경에서 모듈을 찾지 못하는 오류.
*   **원인**: uvicorn 실행 위치와 Python Path가 불일치함.
*   **해결 방법**: `main.py` 최상단에 현재 경로를 `sys.path`에 추가하는 방어 코드 작성.
    ```python
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    ```

### 🔄 AWS에서 코드 배포/업데이트 방법
*   SSH로 Lightsail 인스턴스 접속 후:
    ```bash
    cd ~/kids_library
    git pull origin main
    pip install -r backend/requirements.txt
    pm2 restart all  # 또는 sudo systemctl restart kids-library
    ```

---

## 💡 종합 팁
- **롤백이 항상 정답은 아니다**: 설정(Settings) 문제일 경우 코드를 예전으로 돌려도 404가 해결되지 않을 수 있습니다. 대시보드의 **Framework Preset**과 **Root Directory**를 먼저 확인하세요.
- **Zero-Config 지향**: 모노레포 구조라도 Vercel 설정에서 Root Directory만 잘 잡아주면 복잡한 `vercel.json` 없이도 잘 작동합니다.
