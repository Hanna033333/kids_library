'use client'

import { useEffect } from 'react'

interface ToastProps {
    message: string
    isVisible: boolean
    onClose: () => void
    duration?: number
    bottomOffset?: string
}

export default function Toast({ 
    message, 
    isVisible, 
    onClose, 
    duration = 3000,
    bottomOffset = 'bottom-20'
}: ToastProps) {
    useEffect(() => {
        if (isVisible && duration > 0) {
            const timer = setTimeout(() => {
                onClose()
            }, duration)
            return () => clearTimeout(timer)
        }
    }, [isVisible, duration, onClose])

    if (!isVisible) return null

    return (
        <div className={`fixed ${bottomOffset} left-1/2 -translate-x-1/2 bg-gray-800 text-white px-5 py-3.5 rounded-xl shadow-lg text-[13px] font-medium z-50 animate-in fade-in slide-in-from-bottom-4 text-center break-keep w-max max-w-[90vw]`}>
            {message}
        </div>
    )
}
