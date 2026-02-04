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
