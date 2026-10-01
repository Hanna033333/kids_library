# 책자리 (Kids Library) — Codex 에이전트 설정

이 프로젝트의 규칙, 스킬, 워크플로우는 `.agent/` 디렉토리에 정의되어 있습니다.

---

## Rules (항상 적용)

@.agent/rules/development.md
@.agent/rules/design.md
@.agent/rules/planning.md
@.agent/rules/marketing.md
@.agent/rules/deployment.md
@.agent/rules/QA.md
@.agent/rules/code_reviewer.md
@.agent/rules/growth_hacker.md
@.agent/rules/seo_specialist.md
@.agent/rules/strategy.md

---

## Skills (도메인별 전문 지식)

### Development
@.agent/skills/development/project_workflow/SKILL.md
@.agent/skills/development/deployment/SKILL.md
@.agent/skills/development/supabase_configuration/SKILL.md
@.agent/skills/development/ai_book_categorization/SKILL.md
@.agent/skills/development/curation/SKILL.md
@.agent/skills/development/web_crawling/SKILL.md
@.agent/skills/development/loan_status/SKILL.md
@.agent/skills/development/image_optimization/SKILL.md
@.agent/skills/development/SEO/SKILL.md
@.agent/skills/development/back_route/SKILL.md
@.agent/skills/development/library_expansion/SKILL.md

### Design
@.agent/skills/design/ui_system/SKILL.md
@.agent/skills/design/color_system/SKILL.md
@.agent/skills/design/ux_writing/SKILL.md

### Marketing
@.agent/skills/marketing/ga4_integration/SKILL.md
@.agent/skills/marketing/threads_publishing/SKILL.md
@.agent/skills/marketing/blog_publishing/SKILL.md
# `@.agent/skills/marketing/winter_campaign/SKILL.md`
# `@.agent/skills/marketing/winter_strategy/SKILL.md`

### Planning
# `@.agent/skills/planning/winter_books_policy/SKILL.md`

### QA
@.agent/skills/qa/SKILL.md

---

## Workflows (자주 쓰는 작업 절차)

@.agent/workflows/collaboration_rules.md
@.agent/workflows/deploy_preview.md
@.agent/workflows/deploy_prod.md
@.agent/workflows/update.md
@.agent/workflows/fix_and_document.md
@.agent/workflows/secure_db.md
@.agent/workflows/add_books.md
@.agent/workflows/add_library.md
@.agent/workflows/blog_naver.md
@.agent/workflows/notice_notion.md

---

## Antigravity Slash Command Compatibility

사용자가 Antigravity에서 쓰던 slash command 형태로 요청하면, 실제 슬래시 명령 실행 여부와 관계없이 아래 워크플로우를 같은 의미로 해석하고 실행한다.

| 사용자 입력 | Codex에서 적용할 워크플로우 |
| --- | --- |
| `/deploy-preview`, `/deploy_preview` | `.agent/workflows/deploy_preview.md` |
| `/deploy-prod`, `/deploy_prod` | `.agent/workflows/deploy_prod.md` |
| `/update`, `/learn` | `.agent/workflows/update.md` |
| `/fix-and-document`, `/fix_and_document` | `.agent/workflows/fix_and_document.md` |
| `/secure-db`, `/secure_db` | `.agent/workflows/secure_db.md` |
| `/add-books`, `/add_books` | `.agent/workflows/add_books.md` |
| `/add-library`, `/add_library` | `.agent/workflows/add_library.md` |
| `/blog-naver`, `/blog_naver` | `.agent/workflows/blog_naver.md` |
| `/notice` | `.agent/workflows/notice_notion.md` |

워크플로우 호출 시에는 해당 파일을 먼저 읽고, 관련 Rules/Skills를 필요한 범위에서만 추가로 읽은 뒤 진행한다. `/learn`은 대화에서 합의된 내용을 `.agent/rules/` 또는 `.agent/skills/`에 영구 반영하는 요청으로 취급한다.
