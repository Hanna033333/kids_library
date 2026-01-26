"use client";

import "./globals.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { AuthProvider } from "@/context/AuthContext";
import { LibraryProvider } from "@/context/LibraryContext";
import Script from "next/script";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        {/* SEO Meta Tags - Global Default */}
        <title>책자리 - 판교도서관 어린이책 찾기 | 청구기호 검색</title>
        <meta name="description" content="판교도서관의 어린이 추천 도서를 쉽고 빠르게 찾아보세요. 아이 연령별 필독서, 겨울방학 추천 도서의 청구기호와 대출 가능 여부를 바로 확인하실 수 있습니다." />
        <meta name="keywords" content="판교도서관, 어린이 추천 도서, 초등 필독서, 겨울방학 추천도서, 도서관 청구기호, 아이와 가기 좋은 도서관, 책자리" />

        {/* Google Search Console Verification */}
        <meta name="google-site-verification" content="yLipdtFnNl8hGiWx_zjWZY3paRWUaZhkxs7AotPaCq4" />

        {/* Open Graph */}
        <meta property="og:title" content="책자리 - 판교도서관 어린이책 찾기" />
        <meta property="og:description" content="판교도서관의 어린이 추천 도서를 쉽고 빠르게 찾아보세요. 청구기호와 대출 가능 여부를 바로 확인하실 수 있습니다." />
        <meta property="og:url" content="https://checkjari.com" />
        <meta property="og:site_name" content="책자리" />
        <meta property="og:locale" content="ko_KR" />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="https://checkjari.com/logo.png" />

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="책자리 - 판교도서관 어린이책 찾기" />
        <meta name="twitter:description" content="판교도서관의 어린이 추천 도서를 쉽고 빠르게 찾아보세요." />
        <meta name="twitter:image" content="https://checkjari.com/logo.png" />

        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-FG2WYB82L9"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            if (localStorage.getItem("checkjari_ignore_tracking") === "true" || window.location.search.includes("ignore=true")) {
              if (window.location.search.includes("ignore=true")) {
                localStorage.setItem("checkjari_ignore_tracking", "true");
              }
              console.log("GA Tracking Disabled (Internal)");
            } else {
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-FG2WYB82L9');
            }
          `}
        </Script>
      </head>
      <body className="bg-[#F7F7F7] min-h-screen text-gray-900">
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            <LibraryProvider>
              {children}
            </LibraryProvider>
          </QueryClientProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
