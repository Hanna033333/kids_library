---
name: UI/UX Component System Consistency
description: Rules for maintaining consistency across planning, design, and development to avoid fragmented UI and duplicated effort.
---

# UI/UX 일관성 및 컴포넌트 시스템 가이드 (기획/디자인/개발 공통)

## 📌 개요
마이 페이지 기능 등 화면을 추가/수정하는 작업을 수행할 때, **기존의 룩앤필(회원가입, 로그인 등)**에 쓰인 컴포넌트 스타일을 무시하고 불필요하게 하드코딩된 UI를 생성하는 파편화 방지를 위한 가이드라인입니다.

## 🎯 1. 기획 팀장 (@planning) 지침
- **기능 명세 작성 시 컴포넌트 정책 명시**: PRD에 폼(이메일, 비밀번호 등), 버튼(CTA 등) 등의 입력 및 컨트롤 요소가 등장할 경우, "기존 인증(Auth) 화면과 동일한 컴포넌트 정책을 따른다"와 같이 **어떤 기존 공통 UI를 재사용할 것인지 명시적**으로 작성해야 합니다.
- **예외 없는 일관성 추구**: 서비스의 특정 페이지에서만 예외적으로 다르게 동작하거나 다르게 디자인된 폼을 띄우는 기획은 피합니다.

## 🎨 2. 디자인/UX 팀장 (@design) 지침
- **규격화된 UI 세트 기준 정의**: 버튼(`Button`), 입력창(`Input`) 등은 `.agent/skills/design/color_system/SKILL.md`와 결합하여 정의된 일관적인 **공용 컴포넌트 디자인 시스템**을 따릅니다. 
- **플랫(Flat) 디자인 준수**: 버튼이나 카드 디자인 등에서 무작위적인 엠보싱/그림자 처리(`shadow-lg`, `shadow-[...]` 등)를 특별한 사유 없이 사용하는 것을 지양합니다. 모던하고 일관된 룩을 유지해야 합니다.
- 유효성 검사 등 부가 상태 인디케이터 UI 역시 각기 다른 디자인으로 만들지 말고 **가장 최근에 정립된 UI 규격(좌측 아이콘(Leading Icon) 삽입 유무 등)**을 참고합니다.

## 💻 3. 개발 팀장 (@development) 지침
- **공통 컴포넌트(UI) 활용 필수**: `<input className="...">` 형태로 페이지별로 하드코딩 하는 것을 엄격히 금지합니다.
- 폼 요소를 추가할 때는 반드시 `@/components/ui/Input.tsx`, `@/components/ui/Button.tsx` 등의 **공용 UI 컴포넌트**를 호출(Import)하여 프롭스(Props)에 필요한 텍스트 및 속성, 아이콘 여부만 전달하는 방식으로 작성합니다.
- 반복 렌더링을 막고 한 곳의 스타일 수정 (`Input.tsx`의 텍스트 색상, 모서리 등)이 전체 서비스에 동일하게 퍼지도록 리팩토링과 구현을 동시에 진행해야 합니다.
