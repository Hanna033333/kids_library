"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { AuthProvider } from "@/context/AuthContext";
import { LibraryProvider } from "@/context/LibraryContext";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <QueryClientProvider client={queryClient}>
                <LibraryProvider>
                    {children}
                </LibraryProvider>
            </QueryClientProvider>
        </AuthProvider>
    );
}
