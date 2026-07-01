---
name: back_route
description: 세션 스토리지를 활용한 지능형 뒤로가기(Smart Back Route) 구현 및 경로 트래킹 가이드
---

# 🗺️ 세션 스토리지 기반 지능형 뒤로가기 (Smart Back Route)

SPA 환경에서의 클라이언트 사이드 라우팅 시 브라우저 `document.referrer`가 갱신되지 않는 문제를 우회하기 위해, 전역 경로 이동 추적 시스템을 구축하여 내부/외부 유입을 완벽히 격리하고 뒤로가기 정합성을 제어합니다.

---

## 🛠️ 설계 원칙
1. **앱 최초 로딩 제어**: 새로고침이나 타 사이트로부터 들어오는 최초 로딩 시점에만 `document.referrer`를 검증하여, 외부 유입인 경우 스택을 리셋하고 첫 페이지로 고정합니다.
2. **경로 전환 트래킹**: 클라이언트 사이드 라우팅에 의해 페이지가 변경될 때마다 `sessionStorage`에 경로를 기록하거나, 이전 페이지로 돌아갔을 시 자동으로 팝(pop) 처리하여 히스토리 깊이를 관리합니다.
3. **지능형 리다이렉트**: 뒤로가기 클릭 시 내부 세션 히스토리 스택 크기가 `1`보다 크면 `router.back()`을, `1` 이하(세션 내 첫 진입 페이지)이면 무조건 홈 피드(`/`) 혹은 지정된 폴백 주소로 리다이렉션합니다.

---

## 💻 핵심 구현 코드

### 1. 전역 경로 추적기 (`HistoryTracker.tsx`)
페이지가 전환될 때마다 세션 스토리지의 경로 스택을 관리하는 클라이언트 컴포넌트입니다. `app/layout.tsx`에 전역으로 마운트됩니다.

```typescript
// frontend/components/HistoryTracker.tsx
'use client'

import { useEffect, useRef } from 'react'
import { usePathname } from 'next/navigation'

export default function HistoryTracker() {
    const pathname = usePathname()
    const isFirstLoad = useRef(true)

    useEffect(() => {
        if (typeof window === 'undefined') return

        try {
            const stored = sessionStorage.getItem('checkjari_history')
            let historyStack: string[] = stored ? JSON.parse(stored) : []

            // 앱 최초 로딩(새로고침, 외부 유입 포함) 시점에만 딱 한번 referrer를 감지해 리셋 처리
            if (isFirstLoad.current) {
                isFirstLoad.current = false
                
                const referrer = document.referrer
                const isInternalReferrer = referrer && referrer.includes(window.location.host)
                
                if (!isInternalReferrer) {
                    historyStack = [pathname]
                }
            }

            // 경로 전환 트래킹 및 스택 동기화
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
```

### 2. 스마트 뒤로가기 버튼 (`BackButton.tsx`)
사용자 클릭 이벤트를 받아 세션 히스토리 크기에 맞춰 분기 처리해주는 공용 UI 컴포넌트입니다.

```typescript
// frontend/components/BackButton.tsx
'use client'

import { useRouter } from 'next/navigation'
import { ChevronLeft } from 'lucide-react'

interface BackButtonProps {
    onClick?: () => void
    href?: string
    className?: string
}

export default function BackButton({ onClick, href, className = '' }: BackButtonProps) {
    const router = useRouter()
    const baseClass = `flex items-center justify-center w-10 h-10 -ml-2 text-gray-500 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 ${className}`

    const handleBack = (e: React.MouseEvent) => {
        if (onClick) {
            e.preventDefault()
            onClick()
            return
        }

        if (typeof window !== 'undefined') {
            try {
                const stored = sessionStorage.getItem('checkjari_history')
                const historyStack: string[] = stored ? JSON.parse(stored) : []
                
                if (historyStack.length > 1) {
                    e.preventDefault()
                    router.back()
                } else {
                    e.preventDefault()
                    router.push(href || '/')
                }
            } catch (err) {
                // sessionStorage 접근 불가 등 오류 발생 시 리퍼러 판별 폴백
                const referrer = document.referrer
                const isInternalReferrer = referrer && referrer.includes(window.location.host)
                
                if (isInternalReferrer) {
                    e.preventDefault()
                    router.back()
                } else {
                    e.preventDefault()
                    router.push(href || '/')
                }
            }
        } else {
            e.preventDefault()
            router.push(href || '/')
        }
    }

    return (
        <button onClick={handleBack} className={baseClass} aria-label="뒤로가기">
            <ChevronLeft className="w-6 h-6" />
        </button>
    )
}
```
