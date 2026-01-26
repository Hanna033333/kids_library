import type { Metadata } from "next";
import "./globals.css";
import Script from "next/script";
import { Providers } from "./providers";

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: {
    canonical: "/",
  },
  title: "책자리 - 도서관에서 3초 만에 책 찾기",
  description: "어린이 추천 도서를 쉽고 빠르게 찾아보세요",
  keywords: "어린이 도서, 어린이 추천 책, 도서관, 어린이 도서관, 청구기호, 판교도서관",
  authors: [{ name: "책자리" }],
  openGraph: {
    title: "책자리 - 도서관에서 3초 만에 책 찾기",
    description: "어린이 추천 도서를 쉽고 빠르게 찾아보세요",
    url: "https://checkjari.com",
    siteName: "책자리",
    locale: "ko_KR",
    type: "website",
    images: [
      {
        url: "/logo.png",
        width: 1200,
        height: 630,
        alt: "책자리 로고",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "책자리 - 도서관에서 3초 만에 책 찾기",
    description: "어린이 추천 도서를 쉽고 빠르게 찾아보세요",
    images: ["/logo.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  verification: {
    google: "yLipdtFnNl8hGiWx_zjWZY3paRWUaZhkxs7AotPaCq4",
    other: {
      "naver-site-verification": ["d2c8b82224a9887592cdbcf4e8caa29a", "d697e7d21ac1762af40d7b1fa9902c06"],
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
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
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
