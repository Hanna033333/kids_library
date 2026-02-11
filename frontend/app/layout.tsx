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
  authors: [{ name: "책자리" }],
  icons: {
    icon: '/logo.png',
    apple: '/logo.png',
  },
  openGraph: {
    siteName: "책자리",
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
        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-FG2WYB82L9"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            // Bot detection function
            function isBotOrAutomation() {
              if (typeof navigator === "undefined") return true;

              // Check for WebDriver
              if (navigator.webdriver) {
                console.log("🤖 Bot detected: WebDriver");
                return true;
              }

              // Check User-Agent
              const ua = navigator.userAgent.toLowerCase();
              const botPatterns = ['headless', 'phantom', 'selenium', 'puppeteer', 'playwright', 'chrome-lighthouse', 'bot', 'crawler'];
              for (const pattern of botPatterns) {
                if (ua.includes(pattern)) {
                  console.log("🤖 Bot detected: " + pattern);
                  return true;
                }
              }

              return false;
            }

            // Check if tracking should be ignored
            const shouldIgnore = localStorage.getItem("checkjari_ignore_tracking") === "true" || 
                                window.location.search.includes("ignore=true") ||
                                isBotOrAutomation();

            if (shouldIgnore) {
              if (window.location.search.includes("ignore=true")) {
                localStorage.setItem("checkjari_ignore_tracking", "true");
              }
              console.log("🚫 GA Tracking Disabled");
            } else {
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-FG2WYB82L9');
              console.log("✅ GA Tracking Enabled");
            }
          `}
        </Script>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
