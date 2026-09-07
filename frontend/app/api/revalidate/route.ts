import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

/**
 * 온디맨드 ISR 캐시 무효화 엔드포인트.
 *
 * /collections/curation/[tag] 등 revalidate 주기가 긴(24h) 동적 라우트가
 * 일시적 오류로 잘못된 결과(예: notFound)를 캐싱해버리면, 재배포와
 * 무관하게 그 캐시가 만료 전까지 계속 서빙되는 문제가 있었다(2026-09-07).
 * 재배포로는 Vercel의 ISR/Data 캐시가 지워지지 않으므로, 이 엔드포인트로
 * 특정 경로 템플릿을 직접 재검증한다.
 *
 * 사용법: GET /api/revalidate?secret=<REVALIDATE_SECRET>&path=<encoded path>
 *   - path 생략 시 /collections/curation/[tag] 전체와 홈("/")을 재검증
 */
export async function GET(request: NextRequest) {
    const secret = request.nextUrl.searchParams.get('secret')
    const expected = process.env.REVALIDATE_SECRET

    if (!expected) {
        return NextResponse.json({ error: 'REVALIDATE_SECRET is not configured on the server' }, { status: 500 })
    }

    if (secret !== expected) {
        return NextResponse.json({ error: 'Invalid secret' }, { status: 401 })
    }

    const path = request.nextUrl.searchParams.get('path')

    try {
        if (path) {
            revalidatePath(path)
            return NextResponse.json({ revalidated: true, path, now: Date.now() })
        }

        // 기본값: 큐레이션 동적 라우트 템플릿 전체 + 홈
        revalidatePath('/collections/curation/[tag]', 'page')
        revalidatePath('/')
        return NextResponse.json({
            revalidated: true,
            paths: ['/collections/curation/[tag]', '/'],
            now: Date.now(),
        })
    } catch (err) {
        return NextResponse.json({ error: String(err) }, { status: 500 })
    }
}
