---
name: deployment-troubleshooting
description: Kids Library 프로젝트의 Vercel(Next.js) 및 Render(FastAPI) 배포 문제 해결 가이드
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
- [ ] 백엔드 신규 라이브러리 확인: `backend/requirements.txt`에 신규 추가된 라이브러리가 Render 빌드를 방해하지 않는지 확인.

### 2단계: Vercel 배포 설정 (Frontend)
- **Root Directory**: 반드시 `frontend`로 설정되어 있어야 함.
- **Framework Preset**: 반드시 `Next.js`로 설정.
- **Environment Variables**: 모든 Supabase/API 변수는 `NEXT_PUBLIC_` 접두사를 사용.
- **Node.js Version**: `package.json`의 엔진 설정과 Vercel 설정을 일치시킴 (현재 18+ 권장).

### 3단계: AWS Lightsail 배포 설정 (Backend)
- **OS**: Ubuntu 22.04 LTS (월 $7 플랜, 1GB RAM)
- **고정 IP**: `43.201.190.46` (네트워킹 탭에서 static IP 연결 필수)
- **서버 환경 구성**: `backend/setup_server.sh` 셸 스크립트로 자동화
  - Python venv 가상환경 구성 (`~/venv`)
  - Nginx 리버스 프록시 바인딩 (포트 80 ➡️ 포트 8000)
  - Systemd 서비스 등록 (`/etc/systemd/system/fastapi.service`)
- **로컬 업로드 배포**: `deploy_to_aws.sh` 실행
  - 로컬 맥북의 `Downloads` 폴더에서 `LightsailDefaultKey-ap-northeast-2.pem` 키를 자동 확인
  - `rsync`를 사용해 불필요한 캐시/가상환경을 제외한 `backend/` 소스코드와 `.env`를 통째로 서버로 전송
- **SSL(HTTPS) 설정**: Certbot 플러그인 사용
  - `sudo certbot --nginx -d api.checkjari.com` 명령어로 HTTPS 강제 적용 및 인증서 자동 갱신 설정

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

---

## 2. Render (Backend - FastAPI - 과거 정보)

> [!NOTE]
> 백엔드 API 서버는 유동 IP 차단 이슈(도서관 정보나루)로 인해 Render에서 AWS Lightsail 고정 IP 환경으로 마이그레이션되었습니다. 아래 Render 트러블슈팅 사례는 참고용입니다.

### ❌ 빌드 실패 (python-Levenshtein)
*   **증상**: `pip install` 과정에서 C 확장 라이브러리 컴파일 오류 발생.
*   **원인**: `python-Levenshtein`은 컴파일 환경이 복잡함.
*   **해결 방법**: 컴파일이 필요 없는 `rapidfuzz`로 대체하거나, `python-Levenshtein`을 `requirements.txt`에서 삭제 (FuzzyWuzzy가 fallback으로 작동함).

### 🌐 CORS (Cross-Origin Resource Sharing) 문제
*   **증상**: 프론트엔드에서 API 호출 시 CORS 오류로 브라우저 차단됨.
*   **해결 방법**: `allow_origin_regex` 정규식(`r"https://.*kids-library.*\.vercel\.app"`)을 사용해 프리뷰 도메인 허용.

### 🐍 Python Import 경로 문제
*   **해결 방법**: `main.py` 최상단에 현재 경로를 `sys.path`에 추가하는 방어 코드 작성.

---

## 3. AWS Lightsail (Backend - FastAPI - 현재)

### ❌ POST /api/books/loan-status 호출 시 422 Unprocessable Entity 에러
*   **증상**: 상용 프론트엔드에서 대출 여부를 호출할 때 백엔드 에러 로그에 `422 Unprocessable Entity` 및 Pydantic validation 실패(이유: `Input should be a valid dictionary...`)가 출력됨.
*   **원인**: 상용에 활성화되어 있는 일부 구버전 프론트엔드가 백엔드에 요청을 보낼 때 신규 JSON Object `{ book_ids: [...] }` 형태가 아니라 구버전인 단순 숫자 리스트 `[book_ids]` 포맷으로 요청을 전송하여 발생한 데이터 스키마 충돌.
*   **해결 방법**: 백엔드 `books.py` 내의 `/loan-status` 엔드포인트 수신 인자를 `Union[LoanStatusRequest, List[int]]` 타입으로 확장 선언하고, 함수 내부에서 두 가지 요청 포맷을 다이나믹하게 매핑하도록 보완하여 완벽한 하위 호환성을 제공함.

### ❌ 정보나루 IP 등록 승인 완료 후에도 대출 상태 배지가 '확인중'으로 유지되는 현상
*   **증상**: 도서관 정보나루에 AWS 고정 IP(`43.201.190.46`)를 승인완료 등록했으나 여전히 대출 상태 배지가 '확인중'으로 뜸.
*   **원인**: IP가 최종 승인 반영되기 이전에 사용자가 사이트에 들어와서 정보나루로부터 차단 응답(302 Found)을 한 번 받아왔고, 이 실패 상태(`확인중`)가 백엔드 메모리 캐시(`LOAN_CACHE`, 30분 TTL)에 영구 저장되었기 때문.
*   **해결 방법**: 정보나루 IP 승인 등록 처리가 완료되면, 반드시 AWS 웹 셸 창에서 `sudo systemctl restart fastapi`를 실행하여 백엔드 메모리 캐시를 강제로 비워주어야 즉각적인 대출 정보 조회가 갱신되어 정상 복구됨.

---

## 💡 종합 팁
- **롤백이 항상 정답은 아니다**: 설정(Settings) 문제일 경우 코드를 예전으로 돌려도 404가 해결되지 않을 수 있습니다. 대시보드의 **Framework Preset**과 **Root Directory**를 먼저 확인하세요.
- **Zero-Config 지향**: 모노레포 구조라도 Vercel 설정에서 Root Directory만 잘 잡아주면 복잡한 `vercel.json` 없이도 잘 작동합니다.
- **아웃바운드 IP 차단 대응**: 도서관 정보나루 등 허용 IP 기반으로 동작하는 외부 API와 연동할 때는 Render와 같이 아웃바운드 IP가 유동적으로 변하는 클라우드 환경을 피하고, AWS Lightsail과 같은 고정 IP 가상 사설 서버(VPS)에 배포 및 SSL을 바인딩하는 것이 정석입니다.
- **하위 호환성 보장**: 백엔드 스키마나 API 규격을 업데이트할 때는 구버전 프론트엔드 캐시 혹은 미갱신 모바일/클라이언트 접속으로 인해 422 에러가 발생하는 것을 차단하기 위해, 백엔드 차원에서 입력 데이터의 타입을 유연하게 받아주는 완충 코드를 반드시 심어둡니다.
