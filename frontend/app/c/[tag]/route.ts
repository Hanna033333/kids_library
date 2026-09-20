import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'
import { ALL_TAXONOMY } from '@/lib/constants/taxonomy'

export function GET(
    request: NextRequest,
    { params }: { params: { tag: string } }
) {
    const { tag } = params
    const decodedTag = decodeURIComponent(tag).replace(/^#/, '') // 혹시 샵이 붙어있다면 제거
    
    // 학년별 단축 링크 처리 (예: /c/초등1학년, /c/grade1 등)
    const gradeMatch = decodedTag.match(/(?:초등)?([1-6])학년|grade([1-6])/i);
    if (gradeMatch) {
        const gradeNum = gradeMatch[1] || gradeMatch[2];
        const gradeTag = `초등${gradeNum}학년`;
        const destination = `/books?curation=%EA%B5%90%EA%B3%BC%EC%84%9C%EC%88%98%EB%A1%9D&tag=${encodeURIComponent(gradeTag)}&utm_source=threads&utm_medium=referral&utm_campaign=grade_${gradeNum}`;
        redirect(destination);
    }
    
    // ALL_TAXONOMY에서 tag(한글) 또는 slug(영어)와 매칭되는 항목 찾기
    const matched = ALL_TAXONOMY.find(
        item => item.tag === decodedTag || item.slug === decodedTag
    )
    
    // 매칭되는 항목이 있으면 영어 slug를 사용하고, 없으면 그대로 사용
    const targetSlug = matched ? matched.slug : decodedTag
    
    const destination = `/collections/curation/${encodeURIComponent(targetSlug)}?utm_source=threads&utm_medium=referral&utm_campaign=weekly_${encodeURIComponent(targetSlug)}`
    redirect(destination)
}

