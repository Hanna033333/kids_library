import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"


const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
    {
        variants: {
            variant: {
                primary:
                    "bg-brand-primary text-white",
                secondary:
                    "bg-white text-gray-700 border border-gray-200",
                outline:
                    "bg-white text-brand-primary border border-brand-primary font-bold",
                kakao:
                    "bg-brand-kakao text-brand-kakao-text font-semibold",
                intro:
                    "bg-brand-intro text-white",
                accent:
                    "bg-brand-accent text-white font-bold",
                ghost:
                    "text-gray-500 rounded-lg",
                destructive:
                    "bg-red-600 text-white",
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
                {children}
            </button>
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
