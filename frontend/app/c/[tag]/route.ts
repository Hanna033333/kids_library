import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'
import { ALL_TAXONOMY } from '@/lib/constants/taxonomy'

export function GET(
    request: NextRequest,
    { params }: { params: { tag: string } }
) {
    const { tag } = params
    const decodedTag = decodeURIComponent(tag).replace(/^#/, '') // 혹시 샵이 붙어있다면 제거
    
    // ALL_TAXONOMY에서 tag(한글) 또는 slug(영어)와 매칭되는 항목 찾기
    const matched = ALL_TAXONOMY.find(
        item => item.tag === decodedTag || item.slug === decodedTag
    )
    
    // 매칭되는 항목이 있으면 영어 slug를 사용하고, 없으면 그대로 사용
    const targetSlug = matched ? matched.slug : decodedTag
    
    const destination = `/collections/curation/${encodeURIComponent(targetSlug)}?utm_source=threads&utm_medium=referral&utm_campaign=weekly_${encodeURIComponent(targetSlug)}`
    redirect(destination)
}

