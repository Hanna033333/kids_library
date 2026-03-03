import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
    {
        variants: {
            variant: {
                primary:
                    "bg-brand-primary text-white shadow-lg shadow-gray-200 hover:bg-brand-primary active:bg-brand-primary-active active:scale-[0.98]",
                secondary:
                    "bg-white text-gray-700 border border-gray-200 hover:bg-white hover:border-gray-200",
                kakao:
                    "bg-brand-kakao text-brand-kakao-text hover:bg-brand-kakao active:bg-brand-kakao-active font-semibold",
                intro:
                    "bg-brand-intro text-white hover:bg-brand-intro shadow-[0_10px_30px_rgba(255,179,0,0.3)] hover:shadow-[0_10px_30px_rgba(255,179,0,0.3)] hover:-translate-y-0",
                accent:
                    "bg-brand-accent text-white hover:bg-brand-accent shadow-sm font-bold",
                ghost:
                    "text-gray-500 hover:text-gray-500 hover:bg-transparent rounded-lg",
                destructive:
                    "bg-red-600 text-white hover:bg-red-600 active:bg-red-800",
            },
            size: {
                sm: "h-9 px-3 text-sm",
                md: "h-11 px-5 text-base",
                lg: "h-14 px-6 text-base",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "primary",
            size: "md",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
    isLoading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, isLoading, disabled, children, ...props }, ref) => {
        return (
            <button
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                disabled={disabled || isLoading}
                {...props}
            >
                {isLoading ? (
                    <>
                        <svg
                            className="animate-spin h-4 w-4"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                        </svg>
                        <span>로딩 중...</span>
                    </>
                ) : (
                    children
                )}
            </button>
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
