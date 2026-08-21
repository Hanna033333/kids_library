# 📚 책자리 (Checkjari) 디자인 시스템 가이드 (Figma 연동용)

본 문서는 피그마(Figma)에서 디자인 시스템 및 UI 라이브러리를 구성할 때 필요한 토큰과 컴포넌트 규격서입니다.

---

## 1. 🎨 Color Tokens (Styles & Variables)

### 🔶 Primary Brand Colors
| Token Name | HEX / Value | Role & Usage |
| :--- | :--- | :--- |
| `primary/main` | `#F59E0B` (Amber 500) | 메인 브랜드 컬러, CTA 버튼, 활성 탭, 주요 강조 |
| `primary/dark` | `#D97706` (Amber 600) | 버튼 클릭/터치 시 (Pressed / Active 상태) |
| `primary/200` | `#FDE68A` (Amber 200) | 보조 액션 버튼 배경 (Secondary Button) |
| `primary/light` | `#FEF3C7` (Amber 100) | 연령 뱃지 배경, 부드러운 강조 배경 |
| `primary/dim` | `rgba(245, 158, 11, 0.10)` | 은은한 호버/포커스 링 배경 |

### ⚪ Neutral & Backgrounds
| Token Name | HEX / Value | Role & Usage |
| :--- | :--- | :--- |
| `bg/card` | `#FFFFFF` | 도서 카드, 모달, 리스트 아이템 배경 |
| `bg/muted` | `#F5F5F8` | 서비스 전체 바디 배경 (Muted Background) |
| `border/default`| `#E5E7EB` | 구분선, 인풋 테두리, 카드 외곽선 |
| `text/primary` | `#111827` (Gray 900) | 메인 타이틀, 도서명, 주요 본문 |
| `text/secondary`| `#6B7280` (Gray 500) | 부가 설명, 저자/출판사명, 서브 타이틀 |
| `text/muted` | `#9CA3AF` (Gray 400) | 청구기호 보조 텍스트, 비활성 텍스트 |

### 🟢 Status & Loan Status
| Token Name | BG / Text Color | Label |
| :--- | :--- | :--- |
| `status/success` | `bg-emerald-50` / `#10B981` | **대출가능** (대출 가능 상태) |
| `status/checking`| `bg-orange-100` / `text-orange-700` | **확인중** (실시간 조회 중 또는 확인 필요) |
| `status/not-owned`| `bg-gray-100` / `text-gray-600` | **미소장** (해당 도서관 미소장) |
| `status/error` | `#EF4444` | 오류 알림 및 실패 상태 |

---

## 2. 🔤 Typography System

* **기본 서체**: `SUIT Variable` 또는 `Pretendard`

| Name | Size / Line-Height | Weight | Letter-Spacing | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Display** | `36px` / 1.3 | Bold (700) | -0.5px | 온보딩 타이틀, 랜딩 헤드라인 |
| **Title 1** | `28px` / 1.3 | Bold (700) | -0.3px | 대주제 타이틀, 검색 메인 |
| **Title 2** | `22px` / 1.35 | Bold (700) | -0.3px | **홈 섹션 타이틀** (`text-xl sm:text-2xl`) |
| **Title 3** | `18px` / 1.4 | Bold (700) | -0.3px | 도서 상세 제목, 헤더 타이틀 |
| **Title 4** | `16px` / 1.4 | SemiBold (600) | 0 | 카드 서브 제목, 모달 타이틀 |
| **Body 1** | `15px` / 1.6 | Regular (400) | 0 | 상세 줄거리 설명, 긴 본문 |
| **Body 2** | `14px` / 1.5 | Regular (400) | 0 | 일반 리스트 설명글 |
| **Caption 1**| `13px` / 1.4 | Regular (400) | -0.2px | 청구기호, 도서관 위치 메타 |
| **Caption 2**| `12px` / 1.4 | Regular (400) | -0.2px | 뱃지, 태그 텍스트 |

---

## 3. 📐 Elevation, Radius & Spacing

### 둥글기 (Border Radius)
* `radius-sm` (6px ~ 8px): 상태 뱃지, 미니 태그
* `radius-md` (12px): 버튼, 검색 입력창, 정보 박스
* `radius-lg` (16px): 도서 카드, 목록 아이템 (메인 카드)
* `radius-2xl` (24px): 모바일 바텀시트 상단
* `radius-full` (9999px): 필터 알약 버튼(Pill), 테마 해시태그

### 그림자 (Shadows)
* `Level 1` (Card): `0 1px 4px rgba(0, 0, 0, 0.06)`
* `Level 2` (Modal): `0 4px 16px rgba(0, 0, 0, 0.10)`
* `Level 3` (Bottom Sheet): `0 -4px 24px rgba(0, 0, 0, 0.10)`

---

## 4. 🧩 Core Components (피그마 컴포넌트 세트)

1. **Button Set**
   * `CTA Button`: Height 56px, Radius 12px, Background `#F59E0B`, Text White (Bold 16px)
   * `Secondary Button`: Height 48px, Radius 12px, Background `#FDE68A`, Text `#B45309`
   * `Gray Button`: Height 44px, Radius 12px, Background `#F3F4F6`, Text `#374151`
   * `Filter Chip`: Height 40px, Radius 9999px, Padding X 16px

2. **BookCard (가로 슬라이더용)**
   * 너비: `165px` ~ `190px` (모바일/데스크톱 대응)
   * 표지 이미지 비율: `1:1.4` (세로형 직사각형)
   * 여백: 내부 패딩 10px, 카드 그림자 `Level 1` 적용

3. **BookItem (세로 목록형)**
   * 썸네일(W 64px, H 90px) + 도서명 + 대출 뱃지 + 저자/출판사 + 청구기호 + 태그
   * Auto Layout: Horizontal, Gap 16px, Padding 16px
