import { redirect } from 'next/navigation'
import { NextRequest } from 'next/server'

export function GET(
    request: NextRequest,
    { params }: { params: Promise<{ tag: string }> }
) {
    return params.then(({ tag }) => {
        const decodedTag = decodeURIComponent(tag)
        const destination = `/collections/curation/${encodeURIComponent(decodedTag)}?utm_source=threads&utm_medium=referral&utm_campaign=weekly_${encodeURIComponent(decodedTag)}`
        redirect(destination)
    })
}
