import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    const { searchParams, pathname } = new URL(request.url)

    // 홈 페이지("/")로 유입된 경우에만 광고 리다이렉트 로직 실행
    if (pathname === '/') {
        const utmTerm = searchParams.get('utm_term')
        const utmCampaign = searchParams.get('utm_campaign')

        if (utmTerm || utmCampaign) {
            const term = decodeURIComponent(utmTerm || utmCampaign || '')

            // 1. 4-7세 (유아/유치) 관련 키워드
            if (['4세', '5세', '6세', '7세', '유아', '유치원'].some(k => term.includes(k))) {
                const url = request.nextUrl.clone()
                url.pathname = '/books'
                url.searchParams.set('age', '4-7')
                return NextResponse.redirect(url)
            }

            // 2. 0-3세 (영유아) 관련 키워드
            if (['0세', '1세', '2세', '3세', '아기', '영유아'].some(k => term.includes(k))) {
                const url = request.nextUrl.clone()
                url.pathname = '/books'
                url.searchParams.set('age', '0-3')
                return NextResponse.redirect(url)
            }

            // 3. 8-12세 (초등) 관련 키워드
            if (['8세', '9세', '10세', '11세', '12세', '초등', '1학년', '2학년', '3학년'].some(k => term.includes(k))) {
                const url = request.nextUrl.clone()
                url.pathname = '/books'
                url.searchParams.set('age', '8-12')
                return NextResponse.redirect(url)
            }

            // 4. 청구기호/책찾기/위치 관련 키워드
            if (['청구기호', '위치', '찾기', '사서'].some(k => term.includes(k))) {
                const url = request.nextUrl.clone()
                url.pathname = '/books'
                return NextResponse.redirect(url)
            }
        }
    }

    return NextResponse.next()
}

// 매쳐 설정: 홈 페이지와 정적 자산을 제외한 전체 경로 (효율성을 위해)
export const config = {
    matcher: ['/'],
}
