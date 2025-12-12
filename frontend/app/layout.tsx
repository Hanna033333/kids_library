import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kids Library - 아동 도서 검색",
  description: "판교 도서관 아동 도서 검색",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

