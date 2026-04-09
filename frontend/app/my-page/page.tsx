import { Metadata } from 'next'
import MyPageClient from './MyPageClient'

export const metadata: Metadata = {
    title: '마이 페이지 | 책자리',
    description: '책자리 계정 설정을 관리하세요.',
}

export default function MyPage() {
    return <MyPageClient />
}
