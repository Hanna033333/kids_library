---
name: qa-checklist
description: 시간/데이터 의존적 버그를 포함한 종합 QA 체크리스트 및 배포 후 검증 가이드
---

### 교훈: 홈페이지 책 표시 이슈
**문제**: 1주차에는 정상 작동했으나 2주차에 책이 표시되지 않는 시간 의존적 버그 발생  
**원인**: Offset 계산이 실제 데이터 개수를 초과하여 빈 결과 반환  
**QA 실패 이유**: 특정 시점(1주차)에만 테스트하여 주차 변경 시 문제 발견 못함

### 필수 테스트 항목

#### 1. 시간 의존적 로직 테스트
**대상**: 날짜/시간 기반 계산, 주간/월간 로테이션, 캐시 만료 등

**체크리스트**:
- [ ] **현재 시점 테스트**: 오늘 날짜로 정상 작동 확인
- [ ] **미래 시점 테스트**: 시스템 시간을 1주일, 1개월 후로 변경하여 테스트
- [ ] **과거 시점 테스트**: 시스템 시간을 과거로 변경하여 테스트
- [ ] **경계 시점 테스트**: 연말/연초, 월말/월초, 주말/주초 경계에서 테스트
- [ ] **다양한 주차 테스트**: 1주차, 2주차, 52주차 등 다양한 주차에서 동작 확인

**테스트 방법**:
```bash
# Windows: 시스템 시간 변경 (관리자 권한 필요)
Set-Date -Date "2026-01-26"  # 다음 주
Set-Date -Date "2026-12-31"  # 연말

# 또는 코드에서 시간 주입 가능하도록 리팩토링 요청
```

#### 2. 데이터 경계 조건 테스트
**대상**: Pagination, Offset, Limit, Range 쿼리 등

**체크리스트**:
- [ ] **빈 데이터셋**: 데이터가 0개일 때 UI 확인
- [ ] **최소 데이터**: 데이터가 1개일 때 정상 작동
- [ ] **Offset 초과**: Offset이 총 데이터 개수보다 클 때 처리
- [ ] **실제 데이터 개수 확인**: 각 카테고리/필터별 실제 데이터 개수 파악
- [ ] **동적 Offset 계산**: Offset이 실제 데이터 개수를 고려하는지 확인

**검증 스크립트 예시**:
```typescript
// 각 연령대별 데이터 개수 확인
const ageGroups = ['0-3', '4-7', '8-12', '13+']
for (const age of ageGroups) {
  const count = await getBookCount(age)
  console.log(`${age}: ${count}개`)
  
  // 최대 offset 계산
  const maxWeek = 52
  const maxOffset = (maxWeek * 5) % 100
  
  if (count < maxOffset) {
    console.error(`⚠️ 위험: ${age}는 ${count}개인데 최대 offset은 ${maxOffset}`)
  }
}
```

#### 3. 26주 무중복 큐레이션 및 7-Book Rule 정밀 검증
**대상**: 26주 무중복 큐레이션 스케줄(`SCHEDULE_TABLE`), 각 테마별 7-Book Rule, 매칭 노이즈 정제
**체크리스트**:
- [ ] **78개 테마 무중복 검증**: 26주 동안 배정된 78개 슬롯(72개 고유 테마)에 중복 매핑이 없는지 확인
- [ ] **7-Book Rule 전수 검증**: 78개 테마 전체가 DB 내에서 실제로 7권 이상의 도서를 확보하고 있는지 검증 (`check_78_tags_count.py` 실행)
- [ ] **매칭 노이즈 검출 및 정합성 감사**: 동음이의어나 무관한 도서가 키워드 매칭으로 유입되지 않았는지 `rule_based_audit.py`를 통해 전수 감사 후, 정제 후에도 7권 미만으로 떨어지는 테마가 없는지 확인

#### 4. 동적 로직 검증
**대상**: 주간 로테이션, 랜덤 추천, A/B 테스트 등

**체크리스트**:
- [ ] **로테이션 동작**: 시간 변경 시 다른 결과 반환 확인
- [ ] **일관성**: 동일 시점에서는 동일 결과 반환 확인
- [ ] **전환 시점**: 로테이션 전환 시점(주 경계)에서 정상 작동
- [ ] **캐시 무효화**: 시간 변경 시 캐시가 올바르게 갱신되는지 확인

#### 4. 상태 저장/복원 테스트
**대상**: localStorage, sessionStorage, 쿠키 등

**체크리스트**:
- [ ] **저장 확인**: 데이터가 올바르게 저장되는지 확인
- [ ] **불러오기 확인**: 페이지 새로고침 후 저장된 데이터 복원 확인
- [ ] **만료 처리**: 오래된 데이터 처리 로직 확인
- [ ] **저장소 초과**: 저장소 용량 초과 시 처리 확인

---

## 📋 표준 QA 체크리스트

### 기능 테스트
- [ ] 기획서(PRD) 명시된 모든 기능 동작 확인
- [ ] Happy Path (정상 시나리오) 테스트
- [ ] Edge Case (극단적 상황) 테스트
- [ ] Error Case (오류 상황) 테스트

### UI/UX 테스트 (모바일 우선)
- [ ] 모바일 해상도(360px ~ 480px) 반응형 레이아웃 깨짐 확인 (텍스트 밀림, 가로 스크롤 강제 발생 등)
- [ ] 터치 대상(버튼, 링크, 탭 등) 크기가 패딩 포함 48px x 48px 이상인지 확인
- [ ] 마우스 hover 동작에만 의존하는 기능이 없는지 확인 (모든 기능이 터치로 조작 가능해야 함)
- [ ] 버튼 클릭 시 active/pressed 피드백이 시각적으로 명확한지 확인 (배경색 변화 등)
- [ ] 모바일 기기(실제 기기 또는 iOS/Android 시뮬레이터)에서 스크롤 바운싱 및 바텀시트 터치 스와이프 충돌 여부 확인
- [ ] 로딩 상태(`PageLoader`) 및 검색 결과 없음 등 빈 화면(`Empty State`)이 모바일 화면 중앙에 정합성 있게 위치하는지 확인
- [ ] 반응형 디자인 (모바일/태블릿/데스크톱)

### 성능 테스트
- [ ] 페이지 로딩 시간 (모바일 3G/LTE 환경에서 LCP 3초 이내)
- [ ] API 응답 시간
- [ ] 대용량 데이터 처리

### 보안 테스트
- [ ] 인증/인가 확인
- [ ] XSS, CSRF 방어
- [ ] 민감 정보 노출 확인

### 브라우저 호환성 (모바일 우선)
- [ ] Safari (iOS 모바일 기본 브라우저)
- [ ] Chrome (Android 모바일 기본 브라우저 및 iOS Chrome)
- [ ] WebViews (인스타그램, 페이스북, 텔레그램 내장 브라우저)
- [ ] Chrome/Safari (데스크톱)

---

## 🔄 회귀 테스트 (Regression Test)

### 주간 회귀 테스트
매주 월요일마다 다음 항목 자동 테스트:
- [ ] 시간 의존적 로직 (다음 주 시뮬레이션)
- [ ] 핵심 사용자 플로우
- [ ] 데이터 무결성

### 배포 전 필수 체크
- [ ] 모든 자동화 테스트 통과
- [ ] 수동 QA 체크리스트 완료
- [ ] 성능 지표 확인
- [ ] 에러 로그 확인

---

## 🚀 배포 후 검증 (Post-Deployment Verification) - 필수

배포 직후 반드시 다음 워크플로우를 실행하여 운영 정책(예: 겨울방학 도서 7권 노출) 준수 여부를 확인해야 합니다.

### 개발(Dev) 환경 배포 후
```bash
/verify_dev
```

### 상용(Prod) 환경 배포 후
```bash
/verify_prod
```

**자동 검증 항목:**
1. **홈페이지 상태**: HTTP 200 OK 응답 확인
2. **콘텐츠 정책**: 모든 추천 섹션(겨울방학, 연령별, 어린이도서연구회)의 도서가 DB에서 7권 이상 확보되어 있는지 확인
3. **데이터 로직**: 랜덤 선택 알고리즘 정상 동작 여부 시뮬레이션

---

## 💡 QA 베스트 프랙티스

1. **"지금 되면 다음 주도 된다"고 가정하지 마라**
   - 시간 의존적 로직은 반드시 미래 시점 테스트

2. **"데이터가 충분하다"고 가정하지 마라**
   - 실제 데이터 개수 확인 후 경계 조건 테스트

3. **"한 번 테스트하면 끝"이라고 생각하지 마라**
   - 주기적 회귀 테스트로 지속적 검증

4. **"개발자가 처리했겠지"라고 믿지 마라**
   - 모든 Edge Case를 직접 확인

5. **버그 리포트는 재현 가능하게**
   - 정확한 시간, 데이터 상태, 재현 단계 명시

---

## 📊 QA 메트릭

### 추적 지표
- **버그 발견율**: QA에서 발견한 버그 / 전체 버그
- **회귀 버그율**: 재발한 버그 / 전체 버그
- **시간 의존 버그**: 시간 변경 시 발견된 버그 수
- **데이터 경계 버그**: 데이터 경계 조건에서 발견된 버그 수

### 목표
- QA 버그 발견율: 90% 이상
- 회귀 버그율: 5% 이하
- Critical 버그: 배포 전 100% 해결

---

## 🔍 시드 리뷰 품질 감사 체크리스트

새로운 시드 리뷰가 DB에 삽입된 후, 반드시 아래 4종 기준으로 전수 감사를 실행한다.

### 감사 기준 (4종)
1. **[책제목] 브래킷 패턴** — `content`가 `[`로 시작하고 50자 이내에 `]`가 존재 → 고정 템플릿 방식 생성 증거
2. **판박이 템플릿 문구** — `"] 아이 정서에도 참 좋은"`, `"] 연령대에 딱 맞아서"`, `"] 도서관 큐레이션 보고"` 등 반복 문구 존재
3. **연령 불일치** — `child_age`가 책의 `age` 그룹과 다름 (0-3 / 4-7 / 8-12 매핑 기준)
4. **null 필드** — `content`, `child_age`, `nickname` 중 하나라도 null

### 연령 그룹 매핑 기준
| child_age 값 | 해당 그룹 | 허용 책 age |
|---|---|---|
| 1세, 2세, 3세 | 0-3 | `0-3` 도서만 |
| 4세, 5세, 6세, 7세 | 4-7 | `4-7` 도서만 |
| 8세 이상, 초등* | 8-12 | `8-12` 도서만 |

### 감사 스크립트 (backend/ 폴더에서 실행)

```bash
source venv/bin/activate && python3 - << 'EOF'
import os, sys
sys.path.append('.')
from core.config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

all_reviews = supabase.table("book_reviews").select("id, book_id, nickname, child_age, content").execute()
book_ids = list(set([r["book_id"] for r in all_reviews.data]))
book_res = supabase.table("childbook_items").select("id, age").in_("id", book_ids).execute()
books = {b["id"]: b for b in book_res.data}

def age_group(s):
    if not s: return "unknown"
    if "0-3" in s: return "0-3"
    if "4-7" in s: return "4-7"
    if "8-12" in s: return "8-12"
    return "unknown"

def child_age_group(s):
    if not s: return None
    c = s.replace("세","").strip()
    try:
        age = int(c)
        if age <= 3: return "0-3"
        elif age <= 7: return "4-7"
        else: return "8-12"
    except:
        if "초등" in s: return "8-12"
    return None

template_phrases = [
    "] 아이 정서에도 참 좋은", "] 연령대에 딱 맞아서", "] 도서관 큐레이션 보고",
    "] 아이 눈높이에 딱 맞는", "] 요즘 저희 아이 최애", "] 주말에 도서관",
    "] 아이랑 밤마다 같이 읽고", "] 그림체도 예쁘고", "] 아이 반응이 너무 좋아서",
    "] 도서관에서 빌려 읽었다가",
]

total = len(all_reviews.data)
bracket = sum(1 for r in all_reviews.data if (r.get("content","") or "").startswith("[") and "]" in (r.get("content","") or "")[:50])
template = sum(1 for r in all_reviews.data if any(p in (r.get("content","") or "") for p in template_phrases))
mismatch = sum(1 for r in all_reviews.data
               if age_group(books.get(r["book_id"],{}).get("age","")) != "unknown"
               and child_age_group(r.get("child_age"))
               and age_group(books.get(r["book_id"],{}).get("age","")) != child_age_group(r.get("child_age")))
null_any = sum(1 for r in all_reviews.data if not r.get("content") or not r.get("child_age") or not r.get("nickname"))
problem = len(set(r["id"] for r in all_reviews.data if
    (r.get("content","") or "").startswith("[") or
    any(p in (r.get("content","") or "") for p in template_phrases) or
    not r.get("content") or not r.get("child_age") or not r.get("nickname")))
print(f"총 {total}건 | 브래킷:{bracket} 템플릿:{template} 연령불일치:{mismatch} null:{null_any}")
print(f"문제 리뷰: {problem}건 ({problem/total*100:.1f}%) / 클린: {total-problem}건 ({(total-problem)/total*100:.1f}%)")
if problem > 0:
    print("⚠️  문제 리뷰 발견 — 즉시 삭제 후 generate_seed_reviews.py로 재생성 필요")
else:
    print("✅ 모든 기준 통과")
EOF
```

### 허용 기준
- 문제 리뷰 비율 **0%** (1건이라도 발견 시 즉시 처리)
- 문제 발생 시: 해당 리뷰 삭제 → `backend/scripts/generate_seed_reviews.py --skip-existing` 재실행 → 재감사

