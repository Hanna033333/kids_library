'use client'

import { useEffect, useRef } from 'react'
import { usePathname } from 'next/navigation'

/**
 * 서비스 내부에서 클라이언트 라우팅(Next.js Link 등)을 통해 이동한 경로를 추적하는 컴포넌트
 * 세션 스토리지를 활용해 이동 경로를 스택으로 쌓고, 뒤로가기를 감증하여 스택을 관리합니다.
 * 외부 유입 시 스택을 리셋하여 뒤로가기 시 홈으로 정상 유도될 수 있도록 돕습니다.
 */
export default function HistoryTracker() {
    const pathname = usePathname()
    const isFirstLoad = useRef(true)

    useEffect(() => {
        if (typeof window === 'undefined') return

        try {
            const stored = sessionStorage.getItem('checkjari_history')
            let historyStack: string[] = stored ? JSON.parse(stored) : []

            // 1. 앱 최초 로딩(새로고침, 외부 유입 포함) 시점에만 딱 한번 document.referrer를 감지해 리셋 처리
            if (isFirstLoad.current) {
                isFirstLoad.current = false
                
                const referrer = document.referrer
                const isInternalReferrer = referrer && referrer.includes(window.location.host)
                
                // 외부 유입이거나 리퍼러가 없는 최초 진입일 경우 히스토리 스택을 초기화합니다.
                if (!isInternalReferrer) {
                    historyStack = [pathname]
                }
            }

            // 2. 경로 전환 트래킹 및 스택 동기화
            if (historyStack.length === 0) {
                historyStack = [pathname]
            } else {
                const prevPath = historyStack[historyStack.length - 2]
                const lastPath = historyStack[historyStack.length - 1]

                if (pathname === prevPath) {
                    // 뒤로가기 감지: 마지막 경로 제거
                    historyStack.pop()
                } else if (pathname !== lastPath) {
                    // 새 페이지 이동 감지: 경로 추가
                    historyStack.push(pathname)
                }
            }

            sessionStorage.setItem('checkjari_history', JSON.stringify(historyStack))
        } catch (e) {
            console.error('Failed to sync history stack:', e)
        }
    }, [pathname])

    return null
}
