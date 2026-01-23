import "./globals.css";
import { Providers } from "./providers";
import Script from "next/script";
import { metadata } from "./metadata";

export { metadata };

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
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-FG2WYB82L9');
          `}
        </Script>
      </head>
      <body className="bg-[#F7F7F7] min-h-screen text-gray-900">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
