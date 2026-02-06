import { Metadata } from 'next'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase-server'
import BookItem from '@/components/BookItem'

export const metadata: Metadata = {
    metadataBase: new URL("https://checkjari.com"),
    alternates: { canonical: '/caldecott' },
    title: "칼데콧 수상작 (2000-2026) - 책자리",
    description: "2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다. 판교도서관 청구기호와 대출 정보를 확인하세요.",
    keywords: "칼데콧상, Caldecott Medal, 어린이 그림책, 수상작, 추천 도서, 판교도서관",
    openGraph: {
        title: "칼데콧 수상작 (2000-2026) - 책자리",
        description: "2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다.",
        url: "https://checkjari.com/caldecott",
        images: [
            {
                url: "/logo.png",
                width: 1200,
                height: 630,
                alt: "책자리 - 칼데콧 수상작",
            },
        ],
    },
    twitter: {
        card: "summary_large_image",
        title: "칼데콧 수상작 (2000-2026) - 책자리",
        description: "2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다.",
        images: ["/logo.png"],
    },
};

export default async function CaldecottPage() {
    const supabase = createClient()
    const books = await getCaldecottBooks(supabase)

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        itemListElement: books.map((book, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            item: {
                '@type': 'Book',
                name: book.title,
                author: {
                    '@type': 'Person',
                    name: book.author,
                },
                isbn: book.isbn,
                image: book.image_url,
                url: `https://checkjari.com/book/${book.id}`,
            },
        })),
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-block mb-4">
                        <span className="text-5xl">🏆</span>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        칼데콧 수상작
                    </h1>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        2000년부터 2026년까지 <span className="font-semibold text-amber-600">칼데콧 메달(Caldecott Medal)</span>을 수상한
                        세계 최고의 어린이 그림책 목록입니다.
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                        총 {books.length}권의 수상작을 만나보세요
                    </p>
                </div>

                {/* Books Grid */}
                {books.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {books.map((book) => (
                            <BookItem key={book.id} book={book} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16">
                        <p className="text-gray-500 text-lg">
                            칼데콧 수상작 데이터를 불러오는 중입니다...
                        </p>
                    </div>
                )}

                {/* Info Section */}
                <div className="mt-16 bg-white rounded-lg shadow-sm p-8 border border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        칼데콧 메달이란?
                    </h2>
                    <p className="text-gray-700 leading-relaxed mb-4">
                        칼데콧 메달(Caldecott Medal)은 미국도서관협회(ALA)에서 매년 전년도에 출판된
                        가장 뛰어난 미국 어린이 그림책의 일러스트레이터에게 수여하는 상입니다.
                    </p>
                    <p className="text-gray-700 leading-relaxed">
                        1938년부터 시작된 이 상은 뉴베리상(Newbery Medal)과 함께 미국에서 가장 권위 있는
                        아동 문학상으로 인정받고 있습니다.
                    </p>
                </div>
            </div>
        </div>
    )
}
