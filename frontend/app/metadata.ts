import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "북방구 - 판교도서관 어린이 도서 검색 | 청구기호 바로 찾기",
    description: "판교도서관 어린이 도서를 쉽고 빠르게 검색하세요. 실시간 대출 현황 확인, 나이별/카테고리별 필터링, 청구기호로 책 위치 바로 찾기",
    keywords: "판교도서관, 어린이 도서, 아동 도서, 그림책, 청구기호, 도서 검색, 대출 현황, 어린이책 추천",
    authors: [{ name: "북방구" }],
    openGraph: {
        title: "북방구 - 판교도서관 어린이 도서 검색",
        description: "판교도서관 어린이 도서를 쉽고 빠르게 검색하세요. 실시간 대출 현황과 청구기호를 확인할 수 있습니다.",
        url: "https://bookbangu.com",
        siteName: "북방구",
        locale: "ko_KR",
        type: "website",
    },
    twitter: {
        card: "summary_large_image",
        title: "북방구 - 판교도서관 어린이 도서 검색",
        description: "판교도서관 어린이 도서를 쉽고 빠르게 검색하세요",
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
        google: "", // Google Search Console 인증 코드 (나중에 추가)
    },
};
