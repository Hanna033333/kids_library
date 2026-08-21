'use client';

import { ReactNode } from 'react';
import Modal from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { ButtonProps } from '@/components/ui/Button';

type ConfirmVariant = ButtonProps['variant'];

interface ConfirmModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    description?: string | ReactNode;
    /** 확인 버튼 텍스트 (기본: '확인') */
    confirmLabel?: string;
    /** 취소 버튼 텍스트. 비워두면 취소 버튼 숨김 */
    cancelLabel?: string;
    /** 확인 버튼 스타일 (기본: 'destructive') */
    confirmVariant?: ConfirmVariant;
    /** 확인 동작 중 로딩 상태 */
    isLoading?: boolean;
    /** 배경 dimmed 오버레이 숨김 */
    hideOverlay?: boolean;
    /** 우측 상단 닫기(X) 버튼 숨김 여부 (기본: true) */
    hideCloseButton?: boolean;
}

/**
 * 공통 확인/취소 팝업 템플릿
 */
export default function ConfirmModal({
    isOpen,
    onClose,
    onConfirm,
    title,
    description,
    confirmLabel = '확인',
    cancelLabel = '취소',
    confirmVariant = 'primary',
    isLoading = false,
    hideOverlay = false,
    hideCloseButton = true,
}: ConfirmModalProps) {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            hideCloseButton={hideCloseButton}
            disableOverlayClose={isLoading}
            hideOverlay={hideOverlay}
        >
            <div className="p-6">
                {/* 타이틀 */}
                <h3 className="text-[20px] font-bold text-gray-900 leading-7 pr-8 mb-3 tracking-tight">{title}</h3>

                {/* 설명 */}
                {description && (
                    <div className="text-gray-600 text-[14.5px] leading-[1.6] mb-6 break-keep">
                        {description}
                    </div>
                )}

                {/* 버튼 영역 */}
                <div className={`flex gap-2.5 ${description ? '' : 'mt-5'}`}>
                    {cancelLabel && (
                        <Button
                            variant="gray"
                            size="md"
                            onClick={onClose}
                            disabled={isLoading}
                            className="flex-1 h-12 rounded-xl font-bold text-[15px]"
                        >
                            {cancelLabel}
                        </Button>
                    )}
                    <Button
                        variant={confirmVariant}
                        size="md"
                        onClick={onConfirm}
                        isLoading={isLoading}
                        disabled={isLoading}
                        className="flex-1 h-12 rounded-xl font-bold text-[15px]"
                    >
                        {confirmLabel}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
