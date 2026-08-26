import { Metadata } from 'next'
import { Suspense } from 'react'
import MyPageClient from './MyPageClient'
import { PageLoader } from '@/components/ui/PageLoader'

export const metadata: Metadata = {
    title: '마이 페이지',
    description: '책자리 계정 설정을 관리하세요.',
}

export default function MyPage() {
    return (
        <Suspense fallback={<PageLoader />}>
            <MyPageClient />
        </Suspense>
    )
}
