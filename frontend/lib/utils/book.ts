/**
 * 도서 제목에서 부제(서브타이틀)를 제거하고 메인 타이틀만 반환합니다.
 * 
 * 예:
 * - "화내지 말고 예쁘게 말해요 - 올바른 의사표현을 도와주는 책" -> "화내지 말고 예쁘게 말해요"
 * - "진짜 일 학년 책가방을 지켜라! - 2017 아침독서신문 선정..." -> "진짜 일 학년 책가방을 지켜라!"
 * - "스마트폰이 사라진 날 : 어린이를 위한 미디어 리터러시" -> "스마트폰이 사라진 날"
 */
export function cleanBookTitle(title: string): string {
  if (!title) return ''

  // 1. 앞뒤 공백이 있는 하이픈(" - ") 기준 분리
  let cleaned = title.split(/\s+-\s+/)[0]

  // 2. 콜론(" : " 또는 ": ") 기준 분리
  cleaned = cleaned.split(/\s*:\s+/)[0]

  return cleaned.trim() || title
}
