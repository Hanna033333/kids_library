import type { Metadata, Viewport } from "next";
import "./globals.css";
import Script from "next/script";
import { Providers } from "./providers";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  title: {
    default: "주변 도서관 그림책 대출 + 연령별 큐레이션 | 책자리",
    template: "%s | 책자리"
  },
  description: "우리 동네 도서관에 이 책이 있을까? 전국 도서관 대출 상태와 청구기호를 실시간으로 확인하고, 연령/정서별 엄선된 그림책 큐레이션을 만나보세요!",
  keywords: ["그림책 큐레이션", "그림책 추천", "어린이 도서", "잠자리 동화", "사회성 그림책", "감정조절 그림책", "책자리", "육아도서", "주변 도서관 책 검색", "도서관 대출"],
  authors: [{ name: "책자리" }],
  icons: {
    icon: '/logo.png',
    apple: '/logo.png',
  },
  openGraph: {
    title: "주변 도서관 그림책 대출 + 연령별 큐레이션 | 책자리",
    description: "우리 동네 도서관에 이 책이 있을까? 전국 도서관 대출 상태와 청구기호를 실시간으로 확인하고, 연령/정서별 엄선된 그림책 큐레이션을 만나보세요!",
    url: "https://checkjari.com",
    siteName: "책자리",
    images: [
      {
        url: "/logo.png",
        width: 512,
        height: 512,
        alt: "책자리 그림책 큐레이션"
      }
    ],
    locale: "ko_KR",
    type: "website",
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
      <body className="bg-[#F7F7F7] min-h-screen text-gray-900 overflow-x-hidden">
        {/* Google Analytics 차단 최우선 처리 스크립트 (동기식 실행하여 경쟁 상태 해결) */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var isBot = false;
                  if (typeof navigator !== "undefined") {
                    if (navigator.webdriver) isBot = true;
                    var ua = navigator.userAgent.toLowerCase();
                    var botPatterns = ['headless', 'phantom', 'selenium', 'puppeteer', 'playwright', 'chrome-lighthouse', 'bot', 'crawler'];
                    for (var i = 0; i < botPatterns.length; i++) {
                      if (ua.indexOf(botPatterns[i]) !== -1) { isBot = true; break; }
                    }
                  }
                  
                  var hasIgnore = false;
                  if (typeof window !== "undefined" && window.location && window.location.search) {
                    if (window.location.search.indexOf("ignore=true") !== -1) {
                      hasIgnore = true;
                      localStorage.setItem("checkjari_ignore_tracking", "true");
                    }
                  }
                  
                  if (typeof localStorage !== "undefined") {
                    if (localStorage.getItem("checkjari_ignore_tracking") === "true") {
                      hasIgnore = true;
                    }
                  }
                  
                  if (hasIgnore || isBot) {
                    window['ga-disable-G-FG2WYB82L9'] = true;
                    console.log("🚫 [GA4] Tracking Disabled (ga-disable-G-FG2WYB82L9 = true)");
                  }
                } catch (e) {
                  console.error("GA Ignore check error:", e);
                }
              })();
            `
          }}
        />
        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-FG2WYB82L9"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            if (!window['ga-disable-G-FG2WYB82L9']) {
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-FG2WYB82L9');
              console.log("✅ [GA4] Tracking Enabled");
            }
          `}
        </Script>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
