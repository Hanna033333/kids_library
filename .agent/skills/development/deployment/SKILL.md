---
name: deployment-troubleshooting
description: Kids Library 프로젝트의 Vercel(Next.js) 및 Render(FastAPI) 배포 문제 해결 가이드
---

# 🚀 배포 트러블슈팅 가이드 (Kids Library)

이 문서는 프로젝트 배포 과정에서 발생한 주요 이슈와 해결 방법을 기록합니다.

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

## 2. Render (Backend - FastAPI)

### ❌ 빌드 실패 (python-Levenshtein)
*   **증상**: `pip install` 과정에서 C 확장 라이브러리 컴파일 오류 발생.
*   **원인**: `python-Levenshtein`은 컴파일 환경이 복잡함.
*   **해결 방법**: 컴파일이 필요 없는 `rapidfuzz`로 대체하거나, `python-Levenshtein`을 `requirements.txt`에서 삭제 (FuzzyWuzzy가 fallback으로 작동함).

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
*   **원인**: `render.yaml`의 `startCommand`가 실행되는 위치와 Python Path가 불일치함.
*   **해결 방법**: `main.py` 최상단에 현재 경로를 `sys.path`에 추가하는 방어 코드 작성.
    ```python
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    ```

---

## 💡 종합 팁
- **롤백이 항상 정답은 아니다**: 설정(Settings) 문제일 경우 코드를 예전으로 돌려도 404가 해결되지 않을 수 있습니다. 대시보드의 **Framework Preset**과 **Root Directory**를 먼저 확인하세요.
- **Zero-Config 지향**: 모노레포 구조라도 Vercel 설정에서 Root Directory만 잘 잡아주면 복잡한 `vercel.json` 없이도 잘 작동합니다.
