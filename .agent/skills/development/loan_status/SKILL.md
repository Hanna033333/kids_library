# Loan Status Management Skill

## 🎯 개요
전국 1,600+ 공공도서관의 실시간 대출 가능 여부(Loan Status) 및 On-Demand 실물 청구기호를 조회하고 사용자에게 일관된 상태를 제공하는 가이드입니다.

## 🛠️ 핵심 로직

### 1. 상태 정의 및 매핑 (4대 상태 정제)
사용자 혼란을 줄이고 UX Writing 톤앤매너를 고려하여 최종적으로 다음 4가지 상태만 노출합니다.

| UI 노출 상태 | 설명 | 대응되는 백엔드/API 상태 | 색상 가이드 |
| :--- | :--- | :--- | :--- |
| **대출가능** | 도서관에 책이 있고 대출 가능한 상태 | `available: true`, `status: "대출가능"` | Green |
| **대출중** | 도서관에 책이 있으나 모두 대출 중인 상태 | `available: false`, `status: "대출중"` | Red |
| **미소장** | 도서관에 해당 도서(ISBN)가 없는 상태 | `status: "미소장"`, `status: "정보없음"` (미소장 단일화) | Gray |
| **확인중** | API 오류, 타임아웃, 점검 등으로 상태 확인 실패 | `status: "확인중"`, `status: "확인불가"`, `status: "시간초과"` | Orange |

### 2. 백엔드 처리 원칙 (`backend/services/loan_status.py`, `backend/api/books.py`, `backend/services/library_registry.py`)
- **전국 1,600+ 공공도서관 단일 실시간 구조**:
  - 기존 13개 DB 검증 도서관과 신규 전국 도서관을 분기하지 않고, 모든 도서관에 대해 `backend/data/libraries.json`에서 기관 코드(`libCode`)를 해석한 뒤 정보나루 `bookExist` API로 실시간 소장·대출 상태를 병렬 조회합니다.
  - `book_library_info`에 이미 저장된 청구기호가 있으면 사전 캐시로 우선 응답에 첨부합니다.
- **병렬 처리 & 동시성 제어**: `asyncio.gather` + 지연 초기화 세마포어(`get_semaphore()`, 동시 25건)를 사용해 1페이지(24권) 분량을 1라운드에 처리합니다.
- **API 한도 방어 캐싱**:
  - `대출가능` / `대출중`: 백엔드 인메모리 **10분 TTL** (`CACHE_TTL = 10m`)
  - `미소장`: 백엔드 인메모리 **24시간 TTL** (`NOT_HELD_CACHE_TTL = 24h`)
  - On-Demand 청구기호: **24시간 인메모리 캐시** (`CALLNO_CACHE_TTL = 24h`) + 조회 성공 시 백그라운드에서 Supabase `book_library_info`에 자동 UPSERT(점진적 DB 축적)
- **On-Demand 실물 청구기호 조회 (`fetch_callno_on_demand`, `include_callno=True`)**:
  - 도서 상세 단건(또는 3권 이하) 요청에서 `status in ("대출가능", "대출중")`이나 DB에 청구기호가 없을 때 정보나루 `itemSrch` API를 1회 호출합니다.
  - **필수 파라미터**: `type=ALL`을 반드시 포함합니다. (누락 시 정보나루가 `{"errCode": "periodErr"}` 반환)
  - **`class_no` 폴백**: `callNumbers` 내부가 아닌 상위 `doc["class_no"]`에 내려오는 도서관이 많으므로 `cn.get("class_no") or doc.get("class_no")` 순서로 추출합니다.
  - **별치기호 정제**: `separate_shelf_name`이 4자 이하 짧은 기호(`그`, `아`, `유`)면 `name` 우선, 긴 설명문(`엄마와어린이(별치 JM)`)이면 `separate_shelf_code`(`JM`) 우선 사용 후 `^E([가-힣])` 내부 영문 접두어를 제거합니다.
- **필터링**: ISBN이 없는 도서는 API를 호출하지 않고 즉시 `미소장`으로 처리합니다.

### 3. 프론트엔드 처리 원칙 (`frontend/components/BookItem.tsx`, `frontend/app/book/[id]/BookDetailClient.tsx`)
- **비로그인 전면 개방**: 로그인 여부와 무관하게 사용자가 도서관을 선택(`localStorage` 저장)하면 목록·상세 모두에서 실시간 대출 가능 여부를 즉시 조회·노출합니다.
- **실시간 응답 최우선 (청구기호 부재 시 강제 미소장 덮어쓰기 금지)**:
  - DB(`book_library_info`)에 청구기호가 없더라도 전국 도서관 실시간 응답(`loanStatus`)을 최우선 반영합니다.
  - 도서 상세에서 `대출가능`/`대출중`이나 청구기호가 미제공된 도서관인 경우, 대출 상태 배지와 함께 `"청구기호 미제공"` + 도서관 홈페이지 외부 링크(`library_homepage`)를 노출합니다.
- **UI 정규화 (Normalization)**: 백엔드의 다양한 에러 상태(`시간초과`, `확인불가`, `확인중`)는 `"확인중"`으로 정규화하며, 목록/상세 UI에서 `"확인중"` 상태일 때는 배지를 숨깁니다.
- **데이터 페칭 & 캐싱**: `react-query`로 목록은 페이지 단위(24권) Batch Fetch(`includeCallno: false`), 상세는 단건 Fetch(`includeCallno: true`), `staleTime: 5분`, `retry: 1`을 유지합니다.

## ⚠️ 주의사항
1. **ISBN 필수**: 대출 상태 및 `itemSrch` 조회는 ISBN 13자리를 기반으로 합니다.
2. **목록에서 `itemSrch` 호출 금지**: 목록 24권 일괄 조회 시 `include_callno`는 항상 `false`로 유지해 정보나루 API 호출량과 응답 지연을 방어합니다.
3. **타임아웃 핸들링**: 외부 API 응답 지연/302 리다이렉트 시 Graceful Degradation(`확인중`) 및 전체 실패 감지 시 텔레그램 경고 알림(1시간 쿨다운)을 유지합니다.
