"use client";

import "./globals.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { AuthProvider } from "@/context/AuthContext";
import Script from "next/script";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        {/* SEO Meta Tags */}
        <title>책자리 - 어린이 도서관 책 검색 | 청구기호 바로 찾기</title>
        <meta name="description" content="어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요." />
        <meta name="keywords" content="어린이 도서, 어린이 추천 책, 도서관, 어린이 도서관, 청구기호" />

        {/* Google Search Console Verification */}
        <meta name="google-site-verification" content="yLipdtFnNl8hGiWx_zjWZY3paRWUaZhkxs7AotPaCq4" />

        {/* Open Graph */}
        <meta property="og:title" content="책자리 - 어린이 도서관 책 검색" />
        <meta property="og:description" content="어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요." />
        <meta property="og:url" content="https://checkjari.com" />
        <meta property="og:site_name" content="책자리" />
        <meta property="og:locale" content="ko_KR" />
        <meta property="og:type" content="website" />

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="책자리 - 어린이 도서관 책 검색" />
        <meta name="twitter:description" content="어린이 추천 책을 도서관 청구기호로 바로 확인하세요" />

        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-FG2WYB82L9"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-FG2WYB82L9');
          `}
        </Script>
      </head>
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
