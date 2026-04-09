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
    title = '도서관 가서 헤매지 마세요!',
    description = '책을 찜하면 청구기호와 함께 \'내 책장\'에 저장돼요.\n도서관에서 헤매지 말고 바로 찾아보세요!'
}: LoginPromptModalProps) {
    const router = useRouter();

    return (
        <Modal isOpen={isOpen} onClose={onClose} hideCloseButton maxWidth="max-w-[320px]">
            <div className="p-6">
                <h3 className="text-[18px] font-bold text-gray-900 leading-snug mb-2">
                    {title}
                </h3>
                <p className="text-gray-500 text-sm mb-6 leading-relaxed whitespace-pre-wrap">
                    {description}
                </p>

                <div className="flex flex-col gap-3">
                    <Button
                        onClick={() => router.push('/auth/signup')}
                        variant="kakao"
                        size="md"
                        className="w-full relative rounded-lg font-bold"
                    >
                        <div className="absolute left-4">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 3C5.373 3 0 7.373 0 12.765c0 3.39 2.15 6.42 5.513 8.212l-1.092 4.098c-.12.45.33.84.72.63l4.62-2.31c.712.09 1.442.138 2.18.138 6.627 0 12-4.373 12-9.765C24 7.373 18.627 3 12 3z" />
                            </svg>
                        </div>
                        카카오로 3초 만에 시작하기
                    </Button>
                    <div className="flex gap-3">
                        <Button
                            onClick={onClose}
                            variant="secondary"
                            size="md"
                            className="flex-1 rounded-lg font-bold text-[14px]"
                        >
                            다음에 할게요
                        </Button>
                        <Button
                            onClick={() => router.push('/auth/signup')}
                            variant="secondary"
                            size="md"
                            className="flex-1 relative rounded-lg font-bold text-[14px]"
                        >
                            이메일/Google
                        </Button>
                    </div>
                </div>
            </div>
        </Modal>
    );
}
