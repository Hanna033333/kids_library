---
name: image-optimization
description: 알라딘 API 책 이미지 URL 관리 및 고화질 이미지 최적화 가이드
---

# 책 이미지 URL 가이드

## 1. 알라딘 이미지 URL 패턴

알라딘 API에서 가져온 이미지 URL은 다음 사이즈 옵션을 지원합니다:

| 패턴 | 사이즈 | 용도 | 권장 |
|------|--------|------|------|
| `coversum` | ~85px | 작은 썸네일 | ❌ 사용 금지 |
| `cover200` | 200px | 중간 크기 | △ 필요시 |
| `cover500` | 500px | 고화질 | ✅ **기본 권장** |

### URL 변환 예시
```
# 저화질 (coversum)
https://image.aladin.co.kr/product/36888/38/coversum/8955889135_1.jpg

# 고화질 (cover500) - 권장
https://image.aladin.co.kr/product/36888/38/cover500/8955889135_1.jpg
```

## 2. 이미지 화질 문제 해결

저화질 이미지가 발견되면 다음 SQL로 일괄 수정:

```sql
-- coversum → cover500 일괄 변경
UPDATE childbook_items 
SET image_url = REPLACE(image_url, '/coversum/', '/cover500/')
WHERE image_url LIKE '%/coversum/%';
```

### 특정 태그(curation)만 수정
```sql
UPDATE childbook_items 
SET image_url = REPLACE(image_url, '/coversum/', '/cover500/')
WHERE curation_tag = '겨울방학2026'
  AND image_url LIKE '%/coversum/%';
```

## 3. 이미지 소스별 특징

| 소스 | 도메인 패턴 | 품질 | 비고 |
|------|------------|------|------|
| 알라딘 | `image.aladin.co.kr` | 고 | cover500 사용 권장 |
| 네이버 | `shopping-phinf.pstatic.net` | 중 | - |
| YES24 | `image.yes24.com` | 중 | - |
| 교보 | `image.kyobobook.co.kr` | 중 | - |

## 4. 새 책 데이터 추가 시 체크리스트

- [ ] 알라딘 API 사용 시 `cover500` 사이즈 URL 사용
- [ ] `coversum` URL 사용 금지
- [ ] 이미지 URL이 정상 로드되는지 확인
- [ ] Next.js Image 컴포넌트 사용 시 모바일 우선 중단점을 고려한 `sizes` 속성이 적절하게 정의되었는가?
- [ ] 스펙타클한 이미지 로딩 지연을 막기 위해 썸네일/플레이스홀더 및 레이지 로딩이 올바르게 켜져 있는가?

---

## 5. 모바일 우선 반응형 이미지 최적화 (Next.js Image)
모바일 기기의 성능 및 네트워크 트래픽 낭비를 줄이고 로딩 성능을 최적화하기 위해 다음 개발 정책을 적용한다.
- **`sizes` 속성 정의 의무화**: Next.js `next/image` 컴포넌트를 사용할 때는, 모바일과 데스크톱 화면의 크기 변화에 대응하기 위해 반드시 `sizes` 속성을 알맞게 지정하여 각 화면 크기에 맞는 물리 이미지 크기를 로드하도록 한다.
  - 예시: `sizes="(max-width: 480px) 100vw, (max-width: 768px) 50vw, 33vw"`
- **레이지 로딩 기본화**: 화면 초기 로딩 시 보이지 않는 영역의 이미지는 성능 향상을 위해 레이지 로딩(`loading="lazy"`)을 기본 적용한다. (단, LCP 영역에 해당하는 홈 화면 최상단 배너 및 첫 카드 뉴스는 `priority` 속성을 제공해 우선 로드되게 한다.)
- **포맷 변환**: 가능한 모바일 브라우저 호환성이 좋은 `WebP` 또는 `AVIF` 포맷으로 이미지를 압축 가공하여 서비스하도록 서버/클라이언트 코드를 구성한다.
