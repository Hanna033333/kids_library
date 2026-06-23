import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"


const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
    {
        variants: {
            variant: {
                primary:
                    "bg-brand-primary text-white hover:bg-brand-primary active:bg-brand-primary-active",
                secondary:
                    "bg-brand-primary-200 text-brand-primary border border-transparent active:opacity-80",
                outline:
                    "bg-white text-brand-primary border border-brand-primary font-bold active:bg-gray-50",
                kakao:
                    "bg-brand-kakao text-brand-kakao-text font-semibold active:bg-brand-kakao-active",
                google:
                    "bg-white text-gray-700 hover:bg-gray-50 border border-gray-300 font-semibold active:bg-gray-100",
                intro:
                    "bg-brand-intro text-white active:opacity-80",
                accent:
                    "bg-brand-accent text-white font-bold active:opacity-80",
                ghost:
                    "text-gray-500 rounded-lg active:bg-gray-100",
                destructive:
                    "bg-red-600 text-white active:bg-red-700",
            },
            size: {
                sm: "h-11 px-4 text-[13px] font-semibold", // Gray 보조 액션 (44px)
                md: "h-12 px-5 text-[15px] font-semibold", // Medium/Secondary (48px)
                lg: "h-14 px-6 text-[16px] font-bold", // CTA (56px)
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
                {children}
            </button>
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
