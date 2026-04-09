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
    confirmVariant = 'destructive',
    isLoading = false,
    hideOverlay = false,
}: ConfirmModalProps) {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            hideCloseButton
            disableOverlayClose={isLoading}
            hideOverlay={hideOverlay}
        >
            <div className="p-6">
                {/* 타이틀 */}
                <h3 className="text-[18px] font-bold text-gray-900 leading-snug mb-2">{title}</h3>

                {/* 설명 */}
                {description && (
                    <p className="text-gray-500 text-sm mb-6 leading-relaxed">
                        {description}
                    </p>
                )}

                {/* 버튼 영역 */}
                <div className={`flex gap-3 ${description ? '' : 'mt-4'}`}>
                    {cancelLabel && (
                        <Button
                            variant="secondary"
                            size="md"
                            onClick={onClose}
                            disabled={isLoading}
                            className="flex-1 rounded-lg font-bold"
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
                        className="flex-1 rounded-lg font-bold"
                    >
                        {confirmLabel}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
