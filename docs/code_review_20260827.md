# 책자리(kids_library) 전체 코드 검수 리포트

- 검수일: 2026-08-27
- 대상: `backend/` (FastAPI), `frontend/` (Next.js 14 App Router), 마이그레이션·배포 설정
- 정적 검사 결과: `tsc --noEmit` **통과**, `next lint` **경고 0** — 타입/린트 레벨은 깨끗함

---

## 🔴 High — 먼저 고쳐야 할 것

### 1. QA 백도어 토큰이 `auth.py`에서 환경 가드 없이 상시 열려 있음
`backend/api/auth.py:56`

```python
if token == "TEST_QA_TOKEN":   # ← 조건이 이것뿐
```

같은 백도어가 `backend/api/wishlists.py:59-60`에는 가드가 걸려 있습니다.

```python
is_qa_allowed = os.getenv("ENV") == "development" or os.getenv("ALLOW_QA_MOCK") == "true"
if token == "TEST_QA_TOKEN" and is_qa_allowed:
```

`tests/test_api.py`의 `test_qa_token_blocked_in_production`도 **wishlists만** 검증하고 있어서 이 구멍을 잡지 못합니다.
현재는 `auth.py`의 모든 엔드포인트가 QA일 때 목 데이터를 반환하고 DB를 건드리지 않아 실제 데이터 유출은 없지만,
앞으로 누군가 `from api.auth import get_current_user`로 새 엔드포인트를 붙이는 순간 즉시 실 데이터 접근 백도어가 됩니다.

**수정**: `wishlists.py`와 동일한 가드를 적용하고, 두 곳의 `get_current_user`를 `core/auth.py` 하나로 합치세요. 테스트도 `/api/auth/me` 케이스를 추가.

### 2. `book_reviews` 테이블이 anon 키로 무제한 쓰기 가능
`backend/migrations/015_create_book_reviews.sql:33-34`

```sql
CREATE POLICY "book_reviews_insert_all" ON book_reviews
    FOR INSERT WITH CHECK (true);
```

`NEXT_PUBLIC_SUPABASE_ANON_KEY`는 브라우저에 그대로 노출되는 값입니다. 즉 누구나 백엔드를 거치지 않고
Supabase에 직접 리뷰를 삽입할 수 있고, `api/reviews.py`의 뱃지 화이트리스트 검증·`max_length=500`·닉네임 규칙이 **전부 우회**됩니다.

거기에 `POST /api/books/{book_id}/reviews` 자체도 인증·레이트리밋·중복 방지·도서 존재 확인이 전혀 없습니다.

**수정**: `WITH CHECK (false)`로 바꿔 삽입은 서비스 롤(백엔드)만 가능하게 하고, 백엔드 쪽에 IP/기기 단위 레이트리밋과 `book_id` 존재 검증을 추가.

### 3. AI 생성 리뷰가 실제 부모 후기로 노출됨
`backend/scripts/generate_seed_reviews.py:156-176`이 `NICKNAME_POOL`에서 가짜 닉네임을 뽑아 `is_ai_generated: True`로 저장하는데,
`api/reviews.py:80-89`의 응답에는 그 플래그가 포함되지 않고, `components/BookReviewSection.tsx`에도 AI 표기가 없습니다.
사용자 입장에서는 AI가 지어낸 육아 에피소드가 진짜 부모 후기와 구분되지 않습니다.

한국 표시·광고의 공정화에 관한 법률과 전자상거래법상 후기 조작으로 해석될 소지가 있는 영역입니다.
(작업 중인 diff에서 하드코딩 샘플 리뷰를 제거하신 건 좋은 방향입니다 — DB에 이미 적재된 시드 리뷰도 같이 정리하시길 권합니다.)

**수정**: 셋 중 하나 — ① 시드 리뷰 삭제, ② 응답에 `is_ai_generated`를 포함하고 UI에 "AI 생성 예시" 배지 표시, ③ 별도 "책자리 코멘트" 섹션으로 분리.

### 4. 외부 HTML을 검증 없이 렌더링 (저장형 XSS 경로)
`frontend/app/book/[id]/page.tsx:237`, `frontend/app/book/[id]/BookDetailClient.tsx:607`

```tsx
<div dangerouslySetInnerHTML={{ __html: book.description }} />
```

`book.description`은 알라딘 API 응답을 그대로 DB에 저장한 값(`api/books.py:204-208`)입니다. 외부 서비스 응답 또는 DB가 오염되면 그대로 실행됩니다.

**수정**: `isomorphic-dompurify`로 sanitize 하거나, 서버에서 저장할 때 허용 태그(`<p> <br> <b> <i>`)만 남기고 스트립.

### 5. 관리자 승인 페이지 반사형 XSS
`backend/api/threads.py:670` (그리고 `/approve` 뷰도 동일)

```python
body: JSON.stringify({{ feed_id: {feed_id}, signature: "{signature}" }})
```

`signature`는 쿼리스트링에서 온 임의 문자열인데 이스케이프 없이 JS 문자열 리터럴에 박힙니다.
`?signature="+alert(1)+"` 같은 값으로 `api.checkjari.com`에서 스크립트 실행이 가능합니다.

**수정**: 뷰 진입 시점에 `re.fullmatch(r'[0-9a-f]{64}', signature)`로 형식 검증 후 거부, 그리고 `json.dumps()`로 직렬화해 삽입.

### 6. `sync` 엔드포인트가 fail-open
`backend/api/sync.py:23`

```python
if os.getenv("ENV") == "production":
    raise HTTPException(403, ...)
```

`render.yaml`의 `envVars`에 **`ENV`가 선언되어 있지 않습니다**. 값이 없으면 조건이 거짓이 되어 프로덕션에서
`POST /api/sync/childbook/recommendations`가 인증 없이 열립니다 — 누구나 크롤링 + `childbook_items` upsert를 트리거할 수 있습니다.

**수정**: 화이트리스트 방식으로 뒤집기(`if os.getenv("ENV") != "development": 403`) + `_require_admin_token` 적용. `render.yaml`에 `ENV=production` 명시.

---

## 🟠 Medium — 안정성·정확성

### 7. 동기 Supabase 호출이 async 엔드포인트 안에서 이벤트 루프를 막음
`supabase-py`의 `.execute()`는 동기 호출인데, `async def` 안에서 직접 호출되고 있습니다.
`api/books.py:77` `get_loan_status`, `api/wishlists.py` 전 엔드포인트, `api/auth.py`의 `supabase.auth.get_user`, `api/threads.py` 전반이 해당됩니다.

가장 심한 곳은 `api/threads.py:722-736` `approve_text_submit` — PIL 카드 이미지 5장 생성(`generate_card_news`)이 async 함수 안에서 동기로 돌아
10~20초 동안 **서버 전체가 다른 요청을 처리하지 못합니다**.

**수정**: `def`(동기)로 선언해 FastAPI 스레드풀에 맡기거나, DB/이미지 작업을 `await anyio.to_thread.run_sync(...)`로 감싸기. `api/books.py:167` `get_book_detail`이 동기 `def`로 잘 되어 있는 게 올바른 패턴입니다.

### 8. 데이터 조회 경로가 3중화되어 있고 필터 규칙이 서로 다름
| 경로 | `pangyo_callno` 필터 | 연령 필터 | `category` 필터 |
|---|---|---|---|
| `backend/services/search.py` | **NOT NULL & != '없음'** | `.eq(age)` | 제거됨 |
| `frontend/lib/supabase-client.ts` | 없음 | `.eq(age)` | 제거됨 |
| `frontend/lib/books-api-server.ts` | 없음 | **`.in(AGE_MAP[age])`** | **아직 살아있음** |

같은 필터 조건인데도 SSR/CSR/백엔드 경로에 따라 결과 목록과 `total` 건수가 달라집니다.
페이지네이션 총 페이지 수 불일치, 목록에는 있는데 상세로 못 가는 도서 등이 여기서 나옵니다.

**수정**: 필터 로직을 `lib/utils/curation-filter.ts`처럼 한 곳으로 모으고, 세 경로가 같은 빌더를 쓰게 하거나 아예 백엔드 API 하나로 일원화.

### 9. 리뷰 저장 실패인데 201 성공을 반환
`backend/api/reviews.py:188-199` — 예외를 잡아 `id: "new-review-id"`인 가짜 객체를 그대로 돌려줍니다.
사용자는 "등록 완료"를 보지만 DB에는 아무것도 없습니다. `get_book_reviews`의 `except`(120-128)도 오류를 빈 목록으로 삼켜 장애를 감지할 수 없습니다.

**수정**: 실패 시 5xx 반환, 프론트에서 에러 토스트. 조회 실패도 최소한 로그 레벨을 error로 올리고 모니터링 연결.

### 10. `render.yaml` 환경변수 누락
선언되지 않은 값: `ENV`, `THREADS_ADMIN_TOKEN`, `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID`, `SUPABASE_SERVICE_KEY`, `ALLOW_QA_MOCK`.
특히 `THREADS_ADMIN_TOKEN`은 `main.py:26`의 lifespan에서 `ensure_threads_admin_token()`이 `RuntimeError`를 던지므로 **앱 부팅 자체가 실패**합니다.
대시보드에 수동 등록되어 있더라도 IaC와 실제 설정이 어긋난 상태입니다.

### 11. 요청 검증 실패 시 본문 전체를 stdout에 출력
`backend/main.py:70-74` — 422 핸들러가 `request.body()`를 통째로 print 합니다.
회원가입/프로필 요청이 검증에 실패하면 이메일·닉네임 등이 Render 로그에 평문으로 남습니다.
응답에도 `"body": str(exc.body)`로 원본을 되돌려주고 있습니다.

**수정**: 필드명과 에러 타입만 로깅, 응답 본문에서 `body` 제거.

### 12. 스케줄러·텔레그램 폴링이 웹 워커 프로세스 안에서 동작
`main.py:27-28`이 `weekly_threads_scheduler`와 `telegram_feedback_listener`를 asyncio 태스크로 띄웁니다.
- uvicorn 워커가 2개 이상이 되면 `getUpdates`가 동시 폴링되어 텔레그램이 409를 반환하고 피드백이 유실됩니다.
- Render 인스턴스 재시작/슬립 시 13:00·21:30 트리거를 통째로 놓칩니다(메모리 락 `last_trigger_date_*`도 함께 초기화).
- 3초 주기 폴링이 상시 도는 구조라 워커 하나가 계속 붙잡혀 있습니다.

**수정**: 별도 worker 서비스(Render Background Worker)로 분리하거나 Render Cron Job + 관리자 토큰 호출 방식으로 전환.

### 13. CORS 정규식이 넓음
`backend/main.py:59` — `^https://kids-library-.*\.vercel\.app$` + `allow_credentials=True`.
제3자가 `kids-library-xxx.vercel.app` 이름으로 프로젝트를 만들면 자격증명 포함 요청이 허용됩니다.
프리뷰 도메인은 `-hannas-projects` 패턴만 남기는 편이 안전합니다.

### 14. `book_library_info` RLS 정책이 리포지토리에 없음
프론트엔드가 브라우저에서 anon 키로 이 테이블을 조인해 읽고 있는데(`supabase-client.ts:20`),
`migrations/`와 `scripts/sql/supabase_rls_setup.sql` 어디에도 이 테이블의 RLS 설정이 없습니다.
Supabase 대시보드에서 실제 상태를 확인하고, RLS 미적용이면 읽기 전용 정책을 추가하세요. (`threads_feeds`도 정책 내용 재확인 권장)

---

## 🟡 Low — 품질·유지보수

| # | 위치 | 내용 |
|---|---|---|
| 15 | `context/AuthContext.tsx:29` | QA 모드가 `localStorage` 값만으로 활성화됩니다. 로그인 버튼은 프로덕션에서 숨겨지지만(`AuthClient.tsx:34`) 값을 직접 넣으면 프로덕션 도메인에서도 QA 상태가 됩니다. `process.env.NODE_ENV` 가드 추가. |
| 16 | `lib/home-api.ts:22-23` | `estimatedTotal = 1000` 고정 offset. 대부분의 연령대는 도서 수가 그보다 적어 항상 fallback(`range(0, limit-1)`)으로 떨어집니다 — "주간 로테이션"이 사실상 동작하지 않습니다. |
| 17 | `lib/home-api.ts:119` | `seed` 변수를 계산만 하고 쓰지 않습니다. 주석은 "매일 랜덤 7권"이라고 하지만 실제로는 `order('id')` 고정 순서입니다. |
| 18 | `lib/supabase.ts` + `lib/supabase-client.ts` | 브라우저용 Supabase 클라이언트가 두 개 생성되어 GoTrue 인스턴스가 중복됩니다. 하나로 통합. |
| 19 | `lib/supabase-client.ts:28-32` | 쿼리 빌더를 `try/catch`로 감쌌지만 빌더는 동기적으로 throw 하지 않습니다 — 죽은 코드. |
| 20 | `api/threads.py:503-527` | `trigger_weekly_post`가 `curation_tag`/`curation_title`을 받고도 사용하지 않고 `validate_curation_tag`도 호출하지 않습니다. GET 버전과 동작이 다릅니다. |
| 21 | `api/threads.py:1108-1114` | `except Exception as smoke_err: pass` 뒤에 도달 가능한 코드가 남아 있습니다. 텔레그램 전송이 실패하면 "스모크 테스트 실패"라는 엉뚱한 500으로 둔갑합니다. |
| 22 | `api/books.py:166` | `GET /api/books/{book_id}`에 `is_hidden` 체크가 없습니다. 숨김 처리한 도서도 ID를 알면 상세 조회됩니다(목록에서는 필터링됨). |
| 23 | 백엔드 전반 | `print()` 84개. 구조화된 로깅이 없어 Render 로그에서 레벨 필터링이 불가능합니다. `logging` 일원화 권장. |
| 24 | `.eslintrc.json` | `react-hooks/exhaustive-deps: off` — stale closure 버그를 잡아주는 규칙입니다. `warn`으로라도 되돌리는 걸 권합니다. |
| 25 | JSON-LD 삽입부 (`app/page.tsx:130` 외 5곳) | `JSON.stringify(jsonLd)`를 그대로 스크립트에 넣습니다. 도서 제목에 `</script>`가 들어가면 태그가 깨집니다. `.replace(/</g, '\\u003c')` 처리 권장. |
| 26 | `backend/tests/` | 테스트가 `test_api.py` 하나이고 실제 운영 Supabase에 의존합니다. `package.json`에는 `test` 스크립트가 아예 없습니다(vitest 설정만 존재). |
| 27 | `backend/scripts/`, `docs/archive/` | 일회성 스크립트 250개 이상이 리포지토리에 남아 있고 `docs/archive`와 중복됩니다. `.gitignore`로 일부만 가리는 대신 정리 권장. |
| 28 | `core/config.py` | dotenv를 직접 재구현했습니다. 따옴표로 감싼 값, `#` 인라인 주석, 멀티라인을 처리하지 못합니다. `python-dotenv`가 이미 의존성에 있으니 그것만 쓰는 편이 낫습니다. |

---

## ✅ 잘 되어 있는 부분

- `tsc --noEmit`, `next lint` 모두 클린 — 타입 안정성 관리가 잘 되고 있습니다.
- `.env`, `ga4-key.json` 등 시크릿이 git에 추적되지 않습니다(`.gitignore` 적절).
- PostgREST `or()` 필터의 백슬래시·따옴표·쉼표 이스케이프 처리(`services/search.py:47,60`) — 실제 파서 깨짐을 막는 좋은 방어입니다.
- 관리자 승인 링크의 HMAC 서명 + `hmac.compare_digest` 타이밍 공격 방어.
- 발행 중복 방지를 위한 원자적 선점(`published_at IS NULL` 조건부 update)과 실패 시 롤백.
- `next.config.js`의 보안 헤더 세트(HSTS/X-Frame-Options/nosniff/Permissions-Policy).
- 대출 조회의 인메모리 TTL 캐시 + 주기적 GC + 세마포어(25) 동시성 제어.
- `.agent/` 기반 규칙·스킬·워크플로우 문서화 체계.

---

## 권장 처리 순서

1. **오늘**: #1(QA 백도어), #6(sync fail-open), #10(`render.yaml` 환경변수) — 설정/한 줄 수정으로 끝나고 위험도가 가장 큽니다.
2. **이번 주**: #2(리뷰 RLS + 레이트리밋), #3(AI 리뷰 표기), #4·#5(XSS), #11(로그 유출).
3. **다음 스프린트**: #7(이벤트 루프 블로킹), #8(조회 경로 일원화), #12(스케줄러 분리).
4. **점진적**: Low 항목 및 테스트 보강.

---

## 처리 현황 (2026-08-27 수정 반영)

| # | 항목 | 상태 |
|---|---|---|
| 1 | QA 백도어 가드 통일 | ✅ 수정 (`backend/api/auth.py`) |
| 2 | `book_reviews` anon INSERT 허용 | ✅ 마이그레이션 추가 (`019_lock_book_reviews_insert.sql`, **Supabase에 수동 실행 필요**) + `api/reviews.py`에 book 존재 확인·레이트리밋 추가 |
| 3 | AI 생성 리뷰 미표기 | ✅ API 응답에 `is_ai_generated` 포함, 프론트에 "AI 생성 예시" 배지 추가. 기존 DB 시드 데이터 정리 여부는 별도 판단 필요 |
| 4 | `book.description` XSS | ✅ `lib/utils/sanitize-html.ts` 추가 후 두 렌더링 지점에 적용 |
| 5 | 관리자 승인 페이지 반사형 XSS | ✅ `signature` 형식(hex 64자) 검증 추가 |
| 6 | `sync.py` fail-open | ✅ 화이트리스트 방식(`ENV == "development"`만 허용)으로 반전 |
| 7 | 동기 Supabase 호출의 이벤트 루프 블로킹 | ⏳ 미적용 — 범위가 크고 배포 검증이 필요해 별도 작업으로 분리 권장 |
| 9 | 리뷰 저장 실패 시 가짜 성공 응답 | ✅ 실패 시 500 반환하도록 수정 |
| 10 | 누락 환경변수 문서화 | ✅ (정정) 실제 배포는 Render가 아니라 **AWS Lightsail**(`deploy_to_aws.sh` → systemd `fastapi.service`)이라 `render.yaml` 수정은 되돌렸습니다. 대신 `backend/.env.example`에 `SUPABASE_SERVICE_KEY`, `ALLOW_QA_MOCK`을 추가하고 `ENV`/`THREADS_ADMIN_TOKEN` 설명을 보강했습니다. **Lightsail 서버의 실제 `backend/.env` 파일에 이 값들이 들어있는지 SSH로 직접 확인 필요** (배포 스크립트가 `.env`를 rsync에서 제외하므로 서버에 이미 있어야 함) |
| 11 | 422 핸들러 요청 본문 평문 로깅 | ✅ 필드명/타입만 로깅하도록 수정, 응답에서 `body` 제거 |
| 12 | 스케줄러/텔레그램 폴링이 웹 워커에서 동작 | ⏳ 미적용 — Render 서비스 분리 등 인프라 변경이 필요해 별도 작업으로 분리 권장 |
| 13 | CORS 프리뷰 정규식 과다 허용 | ✅ `kids-library-*-hannas-projects.vercel.app` 형태로 좁힘 |
| 14 | `book_library_info` RLS 누락 | ✅ 마이그레이션 추가 (`020_add_book_library_info_rls.sql`, **Supabase에 수동 실행 필요**) |
| 8 | 검색 필터 3중화 | ✅ `pangyo_callno` 필터를 `supabase-client.ts`/`books-api-server.ts`에도 추가, 잔존 `category` 필터 제거 |

Low 우선순위 항목(15~28)은 이번 라운드에서는 다루지 않았습니다.

### 배포 전 확인할 것
1. ✅ Supabase SQL Editor에서 `backend/migrations/019_lock_book_reviews_insert.sql`, `020_add_book_library_info_rls.sql` 실행 완료
2. AWS Lightsail 서버(`43.201.190.46`)에 SSH 접속해 `~/kids_library/backend/.env`에 아래 값이 들어있는지 확인:
   - `ENV=production` (없으면 fail-closed로 sync API가 항상 막히긴 하지만, 명시적으로 넣어두는 걸 권장)
   - `THREADS_ADMIN_TOKEN` (없으면 `fastapi.service` 기동 자체가 실패함)
   - `SUPABASE_KEY` 또는 `SUPABASE_SERVICE_KEY`가 anon 키가 아닌 **service_role 키**인지 (RLS를 이번에 잠갔기 때문에 anon 키로는 리뷰 저장 등 쓰기 작업이 실패함)
   - `ALLOW_QA_MOCK`은 운영에서는 비워두거나 `false`
   - 값 수정 후에는 `sudo systemctl restart fastapi.service`로 반영
3. `frontend/lib/utils/sanitize-html.ts`는 정규식 기반 최소 구현입니다 — 트래픽/예산이 허락하면 `isomorphic-dompurify` 도입 검토
4. `render.yaml`은 실제로 쓰이지 않는 파일로 확인되어(운영은 AWS Lightsail) 이번 수정을 되돌렸습니다. 완전히 안 쓰는 게 맞다면 삭제를 검토하세요.
