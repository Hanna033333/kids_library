---
description: 책자리 프로젝트의 버튼 컬러 시스템 및 디자인 가이드
---

# 버튼 컬러 시스템 및 디자인 가이드

## 1. 개요
책자리 프로젝트는 **일관된 사용자 경험**을 위해 Tailwind CSS Config 기반의 커스텀 컬러 시스템과 재사용 가능한 `Button` 컴포넌트를 사용합니다. 하드코딩된 hex 값 사용을 지양하고, 정의된 시멘틱 컬러와 컴포넌트를 사용해야 합니다.

## 2. 컬러 팔레트 (Tailwind Config)

모든 컬러는 `tailwind.config.ts`의 `theme.extend.colors.brand`에 정의되어 있습니다.

| 컬러 이름 | Tailwind Class | Hex Code | 용도 |
|---|---|---|---|
| **Primary** | `bg-brand-primary` | `#F59E0B` | 메인 액션 (검색, 필터 적용, 완료) |
| **Primary Hover** | `bg-brand-primary-hover` | `#D97706` | Primary 버튼 호버 상태 |
| **Accent** | `bg-brand-accent` | `#FF4D00` | 강조 액션 (로그인 유도 등) |
| **Kakao** | `bg-brand-kakao` | `#FEE500` | 카카오 로그인 전용 |
| **Intro** | `bg-brand-intro` | `#FFB300` | 인트로 페이지 전용 |

## 3. Button 컴포넌트 사용법

`components/ui/Button.tsx`를 사용하여 버튼을 구현합니다.

### Import
```tsx
import { Button } from "@/components/ui/Button"
```

### Variants
| Variant | 설명 | 사용 예시 |
|---|---|---|
| `primary` | **(기본값)** 메인 액션 버튼 | `<Button>검색</Button>` |
| `secondary` | 회색 보조 버튼 (취소, 초기화) | `<Button variant="secondary">취소</Button>` |
| `kakao` | 카카오 로그인 전용 | `<Button variant="kakao">카카오 로그인</Button>` |
| `accent` | 붉은 계열 강조 버튼 | `<Button variant="accent">로그인</Button>` |
| `intro` | 인트로 페이지 전용 스타일 | `<Button variant="intro">시작하기</Button>` |
| `ghost` | 배경 없는 투명 버튼 | `<Button variant="ghost"><Icon /></Button>` |

### Sizes
| Size | 높이 | 용도 |
|---|---|---|
| `sm` | 36px (h-9) | 작은 버튼, 헤더 내 버튼 |
| `md` | 44px (h-11) | **(기본값)** 일반적인 폼 버튼 |
| `lg` | 56px (h-14) | 주요 CTA, 하단 고정 버튼 |
| `icon` | 40px (h-10) | 아이콘 전용 버튼 (w=h) |

### 주요 Props
- `isLoading` (boolean): 로딩 스피너 자동 표시 및 비활성화
- `disabled` (boolean): 비활성화 스타일 적용
- `className` (string): 추가 스타일 적용 (Tailwind Merge 지원)

## 4. 버튼 내 아이콘 가이드라인 (Icon in Button)

버튼 내부에 아이콘(예: lucide-react)을 배치할 때 디자인 파편화를 막고 시각적 안정감을 유지하기 위해 다음 규칙을 준수합니다.

1. **색상 일체화 (Color Unity):** 아이콘의 색상은 **반드시 버튼 텍스트 색상과 동일**하게 맞춰야 합니다. 텍스트와 다른 별도의 포인트 컬러(예: 텍스트는 회색인데 아이콘만 주황색 탑재 등) 적용은 엄격히 금지합니다.
2. **크기 (Size):** 일반 버튼(`md`, `lg` 사이즈) 기준 아이콘 크기는 **`w-5 h-5`**를 기본으로 사용합니다.
3. **여백 (Spacing):** 여백은 아이콘을 텍스트 왼쪽에 배치할 경우 `mr-2` 혹은 `mr-1`을 사용하거나, 부모 컴포넌트에 통일된 `gap-2`를 적용합니다.

## 5. 예시 코드 (Do & Don't)

### ✅ DO
```tsx
// 로딩 상태가 필요한 메인 버튼
<Button 
  variant="primary" 
  size="lg" 
  isLoading={isLoading}
  onClick={handleSubmit}
  className="w-full"
>
  확인
</Button>

// 텍스트와 동일한 색상 톤으로 안착된 아이콘 (디자인 가이드 준수)
<Button variant="secondary" className="text-gray-600">
  <ShoppingCart className="w-5 h-5 mr-2" />
  도서 구매하기
</Button>
```

### ❌ DON'T
```tsx
// 하드코딩된 컬러 사용 금지
<button className="bg-[#F59E0B] text-white p-4 rounded">
  확인
</button>

// Button 컴포넌트에 bg-color 직접 지정 지양
<Button className="bg-blue-500">
  확인
</Button>

// 아이콘에만 색상을 넣어 시선을 반감시키는 행위 엄격히 금지!
<Button variant="secondary" className="text-gray-800">
  <ShoppingCart className="w-5 h-5 mr-2 text-brand-primary" />
  도서 구매하기
</Button>
```
