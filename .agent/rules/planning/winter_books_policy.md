---
description: 겨울방학 추천 도서 노출 정책
---

# 겨울방학 추천 도서 노출 정책

## 📋 정책 개요

홈페이지 및 도서 목록 페이지에서 겨울방학 추천 도서 섹션의 노출 정책을 정의합니다.

---

## 🎯 핵심 정책

### 1. 노출 개수 고정
- **항상 정확히 7권의 책을 노출**
- 데이터베이스에 충분한 책이 있는 한 절대 7권 미만으로 노출되어서는 안 됨
- 하루에 한 번 랜덤으로 선택된 7권이 24시간 동안 유지됨

### 2. 랜덤 선택 방식
- **매일 자정(00:00)을 기준으로 새로운 7권 선택**
- 선택 방식: 시드 기반 랜덤 셔플 (Fisher-Yates algorithm)
- 시드 계산: `dayOfYear * 0.001` (연중 날짜 기반)
- 같은 날에는 항상 동일한 7권이 노출됨 (일관성 보장)

### 3. 필터링 조건
겨울방학 추천 도서로 노출되기 위한 조건:
1. ✅ `curation_tag = '겨울방학2026'`
2. ✅ `is_hidden IS NULL OR is_hidden = false` (숨김 처리되지 않은 책)
3. ✅ `pangyo_callno IS NOT NULL` (청구기호가 있는 책)

---

## 📂 구현 위치

### Frontend API
- **파일**: `frontend/lib/home-api.ts`
- **함수**: `getWinterBooks(limit: number = 7)`
- **구현 방식**:
  1. DB에서 최대 100권의 겨울방학 도서 조회 (필터링 적용)
  2. 클라이언트 사이드에서 시드 기반 랜덤 셔플
  3. 상위 7권 선택하여 반환

```typescript
export async function getWinterBooks(limit: number = 7): Promise<Book[]> {
    // 날짜 기반 시드로 하루 동안 일관된 랜덤 순서 유지
    const now = new Date()
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (24 * 60 * 60 * 1000))
    const seed = dayOfYear * 0.001

    // DB 조회
    const { data, error } = await supabase
        .from('childbook_items')
        .select('...')
        .eq('curation_tag', '겨울방학2026')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id', { ascending: true })
        .limit(100)

    // 시드 기반 셔플 후 7권 선택
    // ... Fisher-Yates shuffle 로직
    return shuffled.slice(0, Math.min(limit, shuffled.length))
}
```

---

## 🔍 데이터 현황 (2026-01-22 기준)

- **전체 겨울방학 도서**: 40권
- **노출 가능 도서**: 38권 (청구기호 보유 + 비숨김)
- **일일 노출 도서**: 7권 (랜덤 선택)

---

## ⚠️ 주의사항

### 이전 방식의 문제점
❌ **주차 기반 Offset 로테이션 방식** (이전)
- 주차별로 offset을 계산하여 `.range(offset, offset + 7)` 사용
- **문제**: offset이 끝부분에 가까워지면 7권 미만 노출 발생
- **예시**: 38권 중 주차 offset이 35일 경우 → 3권만 노출

✅ **현재 방식: 랜덤 선택** (개선)
- 전체 도서를 먼저 가져온 후 클라이언트에서 셔플 & 선택
- **보장**: 항상 정확히 7권 노출 (데이터 충분 시)

### 트러블슈팅
만약 7권 미만이 노출된다면:
1. DB에 충분한 겨울방학 도서가 있는지 확인 (`겨울방학2026` 태그)
2. `is_hidden = true`로 설정된 책이 너무 많지 않은지 확인
3. `pangyo_callno`가 NULL인 책이 많지 않은지 확인

---

## 📊 검증 스크립트

겨울방학 도서 현황을 확인하려면:
```bash
cd backend
python check_winter_books.py
```

랜덤 선택 로직을 테스트하려면:
```bash
cd backend
python test_winter_random.py
```

---

## 📝 변경 이력

| 날짜 | 변경 내용 | 담당자 |
|------|-----------|--------|
| 2026-01-22 | 주차 기반 offset 방식 → 랜덤 선택 방식 변경 (7권 보장) | Development Agent |
| 2026-01-22 | 정책 문서 최초 작성 | Development Agent |

---

## 🔗 관련 문서
- [개발 워크플로우](./development.md)
- [프로젝트 계획서](../../project_plan.md)
- [겨울방학 캠페인 성과 측정](./.agent/workflows/check_winter_campaign.md)
