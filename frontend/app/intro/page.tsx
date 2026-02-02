'use client'

import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Search, MapPin, Sparkles, ChevronRight, BookOpen, Check, ChevronLeft, Coins, Smartphone } from 'lucide-react'

export default function IntroPage() {
    const router = useRouter()

    return (
        <main className="min-h-screen bg-white w-full font-sans text-[#111]">
            {/* Header - Book List Style (Back + Title) */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-4">
                <div className="relative flex items-center justify-between">
                    <div
                        onClick={() => router.back()}
                        className="p-3 -ml-2 text-gray-500 hover:text-gray-900 cursor-pointer active:bg-gray-100 rounded-lg transition-colors touch-manipulation"
                        role="button"
                    >
                        <ChevronLeft className="w-6 h-6" />
                    </div>
                    <h1 className="absolute left-1/2 -translate-x-1/2 text-base font-bold text-gray-900">서비스 소개</h1>
                    <div className="w-10" /> {/* Spacer for centering balance */}
                </div>
            </header>

            {/* 1. Hero Section - Larger, tighter, more impactful */}
            <section className="pt-24 pb-8 sm:pt-44 sm:pb-36 px-6 text-center">
                <div className="max-w-[1000px] mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    >

                        <h1 className="text-[32px] sm:text-[40px] lg:text-[64px] font-extrabold leading-[1.3] tracking-[-0.03em] mb-5 text-[#000] break-keep">
                            도서관 책 찾기,<br />
                            3초면 충분합니다.
                        </h1>
                        <p className="text-[18px] sm:text-[24px] text-[#000] leading-[1.6] tracking-[-0.03em] max-w-2xl mx-auto break-keep">
                            복잡한 검색 없이, 내 주변 도서관의<br className="sm:hidden" />
                            <b>책 위치</b>와 <b>대출 가능 여부</b>를 한 번에 확인하세요.
                        </p>
                    </motion.div>
                </div>
            </section>

            {/* 2. Main Service Visual */}
            <section className="px-6 pb-20 sm:pb-40">
                <div className="max-w-[1100px] mx-auto">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.96 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="rounded-[2.5rem] sm:rounded-[3.5rem] overflow-hidden bg-[#FFB300] relative aspect-[4/3] sm:aspect-[21/9] flex items-center justify-center shadow-sm"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-[#FFB300] to-[#FF9E0B]" />
                        <img
                            src="/images/intro/solution.png"
                            alt="Service Preview"
                            className="relative z-10 w-[85%] max-w-[640px] shadow-[0_30px_80px_rgba(0,0,0,0.12)] rounded-2xl"
                        />
                    </motion.div>
                </div>
            </section>

            {/* 3. Problem/Solution - Polished Typography */}
            <section className="py-24 sm:py-36 bg-[#F9FAFB] px-6">
                <div className="max-w-[1100px] mx-auto">
                    <div className="text-center mb-12 sm:mb-20">
                        <h2 className="text-[26px] sm:text-[48px] font-extrabold mb-6 leading-[1.3] tracking-[-0.03em] text-[#000] break-keep">
                            이런 불편함,<br />
                            책자리가 해결했습니다
                        </h2>
                        <p className="text-[18px] sm:text-[21px] text-gray-500 leading-[1.7] tracking-[-0.03em] max-w-2xl mx-auto break-keep">
                            맘카페 추천 도서, 읽히고 싶은데 어느 도서관에 있는지 찾기 힘드셨죠?<br className="hidden sm:block" />
                            책자리가 내 주변 도서관을 싹 스캔해서 <b>위치</b>와 <b>청구기호</b>까지 한 번에 알려드립니다.
                        </p>
                    </div>

                    {/* Merged Single Visual - Style Reference: Line Art + Yellow Accent */}
                    <div className="relative rounded-[40px] overflow-hidden bg-white shadow-[0_20px_60px_rgba(0,0,0,0.05)] border border-gray-100 aspect-[4/3] sm:aspect-[21/9] flex items-center justify-center">
                        <div className="flex flex-col items-center justify-center gap-6">
                            <div className="relative w-32 h-32 flex items-center justify-center">
                                {/* Decor: Yellow Blob/Circle behind */}
                                <div className="absolute inset-0 bg-[#FFB300]/20 rounded-full blur-2xl transform scale-75" />

                                {/* Main Icon Group - Line Art Style */}
                                <div className="relative z-10">
                                    {/* Phone Outline */}
                                    <Smartphone className="w-24 h-24 text-gray-800 stroke-[1.5]" />

                                    {/* Yellow Accent Element (Search) */}
                                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg border border-gray-100">
                                        <Search className="w-6 h-6 text-[#FFB300] stroke-[3]" />
                                    </div>

                                    {/* Floating Decor */}
                                    <div className="absolute -top-2 -right-4 w-8 h-8 bg-[#FFB300] rounded-full flex items-center justify-center shadow-md animate-bounce delay-100">
                                        <Check className="w-5 h-5 text-white stroke-[3]" />
                                    </div>
                                </div>
                            </div>
                            <span className="text-[20px] font-bold text-gray-600 tracking-tight">손쉬운 도서 검색</span>
                        </div>
                    </div>
                </div>
            </section>


            {/* 4. Features - Precise Layout */}
            <section className="py-24 sm:py-40 px-6 bg-white">
                <div className="max-w-[1100px] mx-auto space-y-32 sm:space-y-48">
                    {/* Feature Row 1 */}
                    <div className="flex flex-col md:flex-row items-center gap-12 md:gap-28">
                        <div className="flex-1 text-left">
                            <span className="text-[#F59E0B] font-bold text-[17px] sm:text-[19px] mb-6 block tracking-[-0.03em]">책자리 서비스</span>
                            <h3 className="text-[26px] sm:text-[40px] font-extrabold leading-[1.3] tracking-[-0.03em] mb-6 text-[#000] break-keep">
                                흩어진 도서관 정보를<br />
                                한 곳에서 모아보세요.
                            </h3>
                            <p className="text-[18px] sm:text-[21px] text-gray-500 leading-[1.7] tracking-[-0.03em] break-keep">
                                일일이 도서관 사이트를 로그인하고 검색할 필요 없습니다.
                                책자리 검색창 하나면 우리 동네 모든 도서관을 연결해드립니다.
                            </p>
                        </div>
                        <div className="flex-1 w-full bg-gray-50 rounded-[2.5rem] aspect-[4/3] flex items-center justify-center p-12">
                            <Search className="w-32 h-32 text-gray-200" />
                        </div>
                    </div>

                    {/* Feature Row 2 */}
                    <div className="flex flex-col md:flex-row-reverse items-center gap-12 md:gap-28">
                        <div className="flex-1 text-left">
                            <span className="text-[#FFB300] font-bold text-[18px] mb-5 block sm:mb-6">사서 추천</span>
                            <h3 className="text-[26px] sm:text-[40px] font-extrabold leading-[1.3] tracking-[-0.03em] mb-6 text-[#000] break-keep">
                                전문가의 안목으로<br />
                                좋은 책을 발견하세요.
                            </h3>
                            <p className="text-[18px] sm:text-[21px] text-gray-500 leading-[1.7] tracking-[-0.03em] break-keep">
                                어떤 책을 읽힐지 고민될 때, 사서 선생님들이 엄선한
                                추천 도서 리스트를 확인해보세요. 아이 연령에 딱 맞습니다.
                            </p>
                        </div>
                        <div className="flex-1 w-full bg-gray-50 rounded-[2.5rem] aspect-[4/3] flex items-center justify-center p-12">
                            <Sparkles className="w-32 h-32 text-gray-200" />
                        </div>
                    </div>
                </div>
            </section>

            {/* 5. CTA - Minimal & Bold */}
            <section className="py-32 sm:py-48 px-6 bg-[#F9FAFB] text-center border-t border-gray-100">
                <h2 className="text-[26px] sm:text-[50px] font-extrabold mb-10 leading-[1.3] tracking-[-0.03em] text-[#000] break-keep">
                    아이와의 독서,<br />
                    지금 바로 시작해보세요.
                </h2>
                <button
                    onClick={() => router.push('/')}
                    className="bg-[#FFB300] hover:bg-[#FF8F00] text-white text-[20px] sm:text-[24px] font-bold py-6 px-16 rounded-[20px] transition-all shadow-[0_10px_30px_rgba(255,179,0,0.3)] hover:shadow-[0_15px_40px_rgba(255,179,0,0.4)] hover:-translate-y-1 tracking-[-0.03em]"
                >
                    책자리 시작하기
                </button>
            </section>


            {/* Simple Footer */}
            <div className="bg-[#F9FAFB] pb-16 text-center text-gray-400 text-sm">
                <div className="max-w-[1100px] mx-auto border-t border-gray-200 pt-10">
                    <p>&copy; 2026 책자리. All rights reserved.</p>
                </div>
            </div>
        </main >
    )
}
