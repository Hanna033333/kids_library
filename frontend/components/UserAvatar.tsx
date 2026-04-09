'use client'

import { User as UserIcon } from 'lucide-react'
import { User } from '@supabase/supabase-js'

interface UserAvatarProps {
    user: User | null
    size?: number
    className?: string
}

/**
 * 로그인 상태에 따라 사용자 아바타 또는 기본 아이콘을 렌더링하는 컴포넌트
 */
export default function UserAvatar({ user, size = 24, className = "" }: UserAvatarProps) {
    // 1. 로그아웃 상태: 기본 User 아이콘 반환
    if (!user) {
        return <UserIcon size={size} className={className} />
    }

    const avatarUrl = user.user_metadata?.avatar_url
    const name = user.user_metadata?.full_name || user.user_metadata?.name || user.email
    const initial = name?.charAt(0).toUpperCase() || '?'

    // 2. 프로필 이미지가 있는 경우: 이미지 아바타
    if (avatarUrl) {
        return (
            <div
                className={`rounded-full overflow-hidden border border-gray-100 flex-shrink-0 ${className}`}
                style={{ width: size, height: size }}
            >
                <img
                    src={avatarUrl}
                    alt={name}
                    className="w-full h-full object-cover"
                />
            </div>
        )
    }

    // 3. 프로필 이미지가 없는 경우: 이니셜 아바타
    return (
        <div
            className={`rounded-full bg-brand-primary flex items-center justify-center text-white font-bold flex-shrink-0 ${className}`}
            style={{
                width: size,
                height: size,
                fontSize: size * 0.5
            }}
        >
            {initial}
        </div>
    )
}
