import { Metadata } from 'next'
import AuthClient from './AuthClient'

export const metadata: Metadata = {
    title: '로그인 | 책자리 - 어린이 도서관 서비스',
    description: '책자리 로그인 및 회원가입 페이지입니다. 나만의 서재를 만들고 추천 도서를 관리하세요.',
    robots: {
        index: false, // 로그인 페이지는 검색엔진 인덱싱 방지 권장
        follow: false
    }
}

export default function AuthPage() {
    return <AuthClient />
}
