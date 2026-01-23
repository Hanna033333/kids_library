import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "책자리 - 어린이 도서관 책 검색 | 청구기호 바로 찾기",
    description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요.",
    keywords: "어린이 도서, 어린이 추천 책, 도서관, 어린이 도서관, 청구기호",
    authors: [{ name: "책자리" }],
    openGraph: {
        title: "책자리 - 어린이 도서관 책 검색",
        description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요. 아이 책, 도서관에서 어디 있는지 쉽게 찾을 수 있어요.",
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
        title: "책자리 - 어린이 도서관 책 검색",
        description: "어린이 추천 책을 도서관 청구기호로 바로 확인하세요",
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
        other: {
            "naver-site-verification": "d2c8b82224a9887592cdbcf4e8caa29a",
        },
    },
};
