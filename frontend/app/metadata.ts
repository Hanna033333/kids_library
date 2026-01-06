import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "책방구 - 어린이 도서관 책 검색 | 청구기호 바로 찾기",
    description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요.",
    keywords: "어린이 도서, 어린이 추천 책, 도서관, 어린이 도서관, 청구기호",
    authors: [{ name: "책방구" }],
    openGraph: {
        title: "책방구 - 어린이 도서관 책 검색",
        description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요.",
        url: "https://bookbangu.com",
        siteName: "책방구",
        locale: "ko_KR",
        type: "website",
    },
    twitter: {
        card: "summary_large_image",
        title: "책방구 - 어린이 도서관 책 검색",
        description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요",
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
        google: "X91bGqGznK1eio7JJAUbij2Lo4BedhpLb4zf-w75U-M",
    },
};
