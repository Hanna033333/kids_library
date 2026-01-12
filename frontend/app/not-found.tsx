'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'

export default function NotFound() {
    const pathname = usePathname()

    useEffect(() => {
        // GA에 404 이벤트 전송
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('event', 'page_not_found', {
                page_path: pathname,
                page_title: '404 - Page Not Found',
            })
        }

        // 콘솔에 404 로그 출력 (디버깅용)
        console.warn(`404 Error: ${pathname}`)
    }, [pathname])

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="text-center max-w-md">
                <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
                <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                    페이지를 찾을 수 없습니다
                </h2>
                <p className="text-gray-600 mb-8">
                    요청하신 페이지가 존재하지 않거나 이동되었습니다.
                </p>
                <Link
                    href="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                    홈으로 돌아가기
                </Link>
                {pathname && (
                    <p className="mt-8 text-sm text-gray-500">
                        경로: <code className="bg-gray-100 px-2 py-1 rounded">{pathname}</code>
                    </p>
                )}
            </div>
        </div>
    )
}
