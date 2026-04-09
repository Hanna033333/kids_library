'use client'

import { useRouter } from 'next/navigation'
import UserAvatar from '@/components/UserAvatar'
import { useAuth } from '@/context/AuthContext'

export default function ProfileDropdown() {
    const router = useRouter()
    const { user } = useAuth()

    if (!user) return null;

    return (
        <button
            onClick={() => router.push('/my-page')}
            className="flex items-center justify-center text-gray-500 hover:text-gray-900 transition-colors p-1"
            aria-label="마이 페이지"
        >
            <UserAvatar user={user} size={24} />
        </button>
    )
}
