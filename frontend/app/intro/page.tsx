// 서버 컴포넌트 래퍼: metadata를 export하기 위해 분리
// 실제 UI는 IntroPageClient에 위임
import { Metadata } from 'next'
import IntroPageClient from './IntroPageClient'

export const metadata: Metadata = {
    metadataBase: new URL("https://checkjari.com"),
    alternates: { canonical: "/intro" },
    title: "책자리 서비스 소개 - 도서관 책 3초 만에 찾는 법",
    description: "도서관 책 찾기가 이렇게 쉬울 수 있습니다. 책자리는 청구기호·위치·대출 여부를 한 번에 보여주는 어린이 도서관 필수 서비스입니다.",
    keywords: "책자리, 도서관 책 찾기, 청구기호, 어린이 도서관, 서비스 소개",
    openGraph: {
        title: "책자리 서비스 소개 - 도서관 책 3초 만에 찾는 법",
        description: "도서관 책 찾기가 이렇게 쉬울 수 있습니다. 책자리는 청구기호·위치·대출 여부를 한 번에 보여주는 어린이 도서관 필수 서비스입니다.",
        url: "https://checkjari.com/intro",
        type: "website",
    },
    robots: { index: true, follow: true },
}

export default function IntroPage() {
    return <IntroPageClient />
}
