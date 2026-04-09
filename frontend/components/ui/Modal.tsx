'use client';

import { useEffect, ReactNode } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    /** 'center': 화면 중앙 팝업 (기본값) | 'bottom': 하단 시트 */
    position?: 'center' | 'bottom';
    /** 모달 최대 너비 (Tailwind 클래스) */
    maxWidth?: string;
    /** 우측 상단 닫기(X) 버튼을 숨김 */
    hideCloseButton?: boolean;
    /** 오버레이 클릭 시 닫기 비활성화 */
    disableOverlayClose?: boolean;
    /** 배경 dimmed 오버레이 숨김 */
    hideOverlay?: boolean;
    children: ReactNode;
    /** 테스트/접근성용 ID */
    id?: string;
}

export default function Modal({
    isOpen,
    onClose,
    position = 'center',
    maxWidth = 'max-w-sm',
    hideCloseButton = false,
    disableOverlayClose = false,
    hideOverlay = false,
    children,
    id,
}: ModalProps) {
    // Escape 키 닫기
    useEffect(() => {
        if (!isOpen) return;
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    // body 스크롤 잠금 (hideOverlay일 때는 스크롤 유지)
    useEffect(() => {
        if (isOpen && !hideOverlay) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => { document.body.style.overflow = ''; };
    }, [isOpen, hideOverlay]);

    if (!isOpen) return null;

    const isBottom = position === 'bottom';

    return (
        <div
            id={id}
            className={`fixed inset-0 z-50 flex ${isBottom ? 'items-end md:items-center' : 'items-center'} justify-center ${hideOverlay ? '' : 'bg-black/50 backdrop-blur-sm'} animate-in fade-in duration-200 px-4`}
            onClick={disableOverlayClose ? undefined : (e) => { if (e.target === e.currentTarget) onClose(); }}
            role="dialog"
            aria-modal="true"
        >
            <div
                className={`
                    relative w-full ${maxWidth} bg-white overflow-hidden
                    ${hideOverlay ? 'shadow-2xl' : ''}
                    ${isBottom
                        ? 'rounded-t-2xl md:rounded-2xl max-h-[90vh] flex flex-col animate-in slide-in-from-bottom md:slide-in-from-bottom-10 duration-300'
                        : 'rounded-2xl animate-in zoom-in-95 duration-200'
                    }
                `}
            >
                {!hideCloseButton && (
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 z-10 text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 transition-colors"
                        aria-label="닫기"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
                {children}
            </div>
        </div>
    );
}
