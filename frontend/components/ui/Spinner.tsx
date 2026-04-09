import * as React from "react"
import { cn } from "@/lib/utils"

export interface SpinnerProps {
    size?: "sm" | "md" | "lg" | "xl"
    variant?: "primary" | "white" | "gray" | "currentColor"
    className?: string
}

export function Spinner({ size = "md", variant = "currentColor", className }: SpinnerProps) {
    const sizeMap = {
        sm: { width: 18, height: 18, strokeWidth: 2 },
        md: { width: 24, height: 24, strokeWidth: 2 },
        lg: { width: 40, height: 40, strokeWidth: 1.5 },
        xl: { width: 64, height: 64, strokeWidth: 1.5 },
    }

    const colorMap = {
        primary: "text-brand-primary",
        white: "text-white",
        gray: "text-gray-400",
        currentColor: "text-current",
    }

    const s = sizeMap[size]

    return (
        <div
            className={cn("inline-flex items-center justify-center flex-shrink-0 animate-in fade-in duration-200", colorMap[variant], className)}
            style={{ width: s.width, height: s.height }}
        >
            <style suppressHydrationWarning>{`
                .spinner-flip-right {
                    transform-origin: 12px center;
                    animation: spinnerFlipScaleRight 1.2s infinite ease-in;
                }
                .spinner-flip-left {
                    transform-origin: 12px center;
                    animation: spinnerFlipScaleLeft 1.2s infinite ease-out;
                }
                @keyframes spinnerFlipScaleRight {
                    0% { transform: scaleX(1); opacity: 1; }
                    50% { transform: scaleX(0); opacity: 1; }
                    50.01% { transform: scaleX(0); opacity: 0; }
                    100% { transform: scaleX(0); opacity: 0; }
                }
                @keyframes spinnerFlipScaleLeft {
                    0% { transform: scaleX(0); opacity: 0; }
                    50% { transform: scaleX(0); opacity: 0; }
                    50.01% { transform: scaleX(0); opacity: 1; }
                    100% { transform: scaleX(1); opacity: 1; }
                }
            `}</style>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={s.strokeWidth}
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-full h-full overflow-visible"
            >
                {/* Background static pages */}
                <path d="M12 4H6a2 2 0 0 0-2 2v14h8V4Z" opacity="0.3" />
                <path d="M12 4h6a2 2 0 0 1 2 2v14h-8V4Z" opacity="0.3" />

                {/* Animated flipping pages */}
                <path d="M12 4h6a2 2 0 0 1 2 2v14h-8V4Z" className="spinner-flip-right" />
                <path d="M12 4H6a2 2 0 0 0-2 2v14h8V4Z" className="spinner-flip-left" />
            </svg>
        </div>
    )
}
