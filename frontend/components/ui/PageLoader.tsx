import * as React from "react"
import { cn } from "@/lib/utils"

export function PageLoader({ className }: { className?: string }) {
    return (
        <div className={cn("fixed inset-0 z-50 flex flex-col items-center justify-center bg-white", className)}>
            <img 
                src="/children-book.gif" 
                alt="로딩 중..." 
                className="w-24 h-24 object-contain"
            />
        </div>
    )
}
