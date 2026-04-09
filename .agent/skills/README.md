# 책자리 스킬(Skills) 가이드라인

이 디렉토리는 `Antigravity` 에이전트가 특정 도메인이나 작업에 대해 참조할 수 있는 전문 지식과 가이드를 포함합니다.

## 📁 디렉토리 구조 규칙

모든 스킬은 다음과 같은 구조를 따라야 합니다.

```
.agent/skills/
└── [category]/
    └── [skill_name]/
        ├── SKILL.md       (필수: 메인 가이드/설명 파일)
        ├── examples/      (선택: 예시 코드나 문서)
        └── scripts/       (선택: 관련 헬퍼 스크립트)
```

### 1. 명명 규칙 (Naming Convention)
- **카테고리 및 스킬 이름**: 반드시 `lower_snake_case` (소문자 및 언더바)를 사용합니다.
  - ✅ 예: `ai_book_categorization`, `ga4_integration`, `seo`
  - ❌ 예: `AI_Book_Categorization`, `SEO`, `QA`

### 2. SKILL.md 구성 (Requirement)
모든 스킬 디렉토리에는 반드시 `SKILL.md` 파일이 존재해야 합니다. 이 파일에는 해당 스킬의 정의, 트리거 조건, 구체적인 작업 지침이 포함됩니다.

## 🏷️ 현재 카테고리 (Categories)

- **design**: UI/UX, 컬러 시스템, 라이팅 가이드 등
- **development**: API 설계, DB 설정, 크롤링, 검색 최적화(SEO) 등
- **marketing**: 캠페인 전략, 데이터 분석(GA4) 등
- **planning**: 운영 정책, 기획 문서 등
- **qa**: 서비스 품질 검증 및 체크리스트

## 🛠️ 새로운 스킬 추가 방법
1. 적절한 카테고리를 선택하거나 생성합니다.
2. 스킬 이름으로 디렉토리를 생성합니다 (`lower_snake_case`).
3. 디렉토리 내에 `SKILL.md` 파일을 작성합니다.
4. 필요한 경우 `examples/` 또는 `scripts/` 디렉토리를 추가하여 보충 자료를 넣습니다.
