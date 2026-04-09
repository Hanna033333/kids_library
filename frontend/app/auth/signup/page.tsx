import { Suspense } from 'react'
import AuthClient from '../AuthClient'
import { PageLoader } from '@/components/ui/PageLoader'

export default function SignupPage() {
    return (
        <Suspense fallback={<PageLoader />}>
            <AuthClient />
        </Suspense>
    )
}
