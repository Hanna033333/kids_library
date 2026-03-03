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

## 4. 예시 코드 (Do & Don't)

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

// 아이콘이 포함된 카카오 버튼
<Button variant="kakao" className="w-full">
  <KakaoIcon className="w-5 h-5 mr-2" />
  카카오로 시작하기
</Button>
```

### ❌ DON'T
```tsx
// 하드코딩된 컬러 사용 금지
<button className="bg-[#F59E0B] text-white p-4 rounded">
  확인
</button>

// Button 컴포넌트에 bg-color 직접 지정 지양 (variant 사용 권장)
<Button className="bg-blue-500">
  확인
</Button>
```
