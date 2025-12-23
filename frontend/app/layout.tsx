"use client";

import type { Metadata } from "next";
import "./globals.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";

// Note: metadata export removed because this is now a client component
// Move metadata to a separate metadata.ts file if needed

import { AuthProvider } from "@/context/AuthContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="bg-[#F7F7F7] min-h-screen text-gray-900">
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

