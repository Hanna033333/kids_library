'use client';

import { useRouter } from 'next/navigation';
import Modal from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

interface LoginPromptModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    description?: string;
}

export default function LoginPromptModal({
    isOpen,
    onClose,
    title = '로그인이 필요해요!',
    description = '비밀번호 입력 없이 3초 만에 시작하세요.'
}: LoginPromptModalProps) {
    const router = useRouter();

    return (
        <Modal isOpen={isOpen} onClose={onClose} maxWidth="max-w-[320px]">
            <div className="flex flex-col items-center p-8">
                <img
                    src="/logo.png"
                    alt="책자리"
                    className="w-16 h-auto mb-6"
                />

                <h3 className="text-xl font-bold text-gray-900 mb-2 text-center text-balance leading-snug">
                    {title}
                </h3>
                <p className="text-gray-500 text-sm text-center mb-8 whitespace-pre-wrap">
                    {description}
                </p>

                <div className="w-full space-y-3">
                    <Button
                        onClick={() => router.push('/auth/signup')}
                        variant="kakao"
                        size="lg"
                        className="w-full relative"
                    >
                        <div className="absolute left-4">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 3C5.373 3 0 7.373 0 12.765c0 3.39 2.15 6.42 5.513 8.212l-1.092 4.098c-.12.45.33.84.72.63l4.62-2.31c.712.09 1.442.138 2.18.138 6.627 0 12-4.373 12-9.765C24 7.373 18.627 3 12 3z" />
                            </svg>
                        </div>
                        <span className="text-[15px]">카카오로 3초 만에 시작하기</span>
                    </Button>
                    <Button
                        onClick={() => router.push('/auth/signup')}
                        variant="secondary"
                        size="lg"
                        className="w-full relative"
                    >
                        <div className="absolute left-4">
                            <svg width="18" height="18" viewBox="0 0 24 24">
                                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                            </svg>
                        </div>
                        <span className="text-[15px]">다른 방식(Google / 이메일)</span>
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
