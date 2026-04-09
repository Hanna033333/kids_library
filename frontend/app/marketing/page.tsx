import { Metadata } from 'next'
import PageHeader from '@/components/PageHeader'

export const metadata: Metadata = {
    title: '마케팅 정보 수신 동의 | 책자리',
    description: '책자리 이벤트 및 마케팅 정보 수신 동의 안내입니다.',
}

export default function MarketingPage() {
    return (
        <div className="min-h-screen bg-white">
            <PageHeader title="이벤트 등 알림 혜택 수신" />

            {/* Content */}
            <main className="max-w-3xl mx-auto px-4 py-8 md:py-12">
                <div className="prose prose-slate max-w-none space-y-8">

                    <div className="space-y-4">
                        <section className="space-y-3">
                            <p className="text-sm text-gray-600 leading-relaxed">
                                '책자리'는 더 나은 서비스를 제공하고자 광고·마케팅 목적의 개인정보 수집 및 이용에 대한 동의를 받고자 합니다. 수집된 개인 정보는 이메일, PUSH 알림 등 영리목적의 광고성 정보 전달에 활용되거나 영업 및 마케팅 목적으로 활용될 수 있습니다.
                            </p>
                            <p className="text-sm font-medium text-gray-700 pt-2">
                                ※ 동의를 거부하시는 경우에도 기본 서비스는 이용이 가능합니다.
                            </p>
                        </section>
                    </div>

                    <div className="space-y-6 pt-6 border-t border-gray-100">
                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">1. 개인정보의 수집 및 이용 목적</h3>
                            <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                                <li>책자리 및 제휴사의 상품/서비스에 대한 광고·홍보·프로모션 제공</li>
                            </ul>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">2. 수집하는 개인정보의 항목</h3>
                            <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                                <li>이메일, 닉네임, 기기 정보, 서비스 이용 기록</li>
                            </ul>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">3. 개인정보의 이용 및 보유기간</h3>
                            <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                                <li><span className="font-semibold text-gray-700">동의 철회 시 또는 회원 탈퇴 시까지</span></li>
                            </ul>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">4. 수신동의 설정 변경 방법</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                로그인 &gt; 마이페이지 &gt; 설정 &gt; 마케팅 및 광고 수신 동의 on/off
                            </p>
                        </section>
                    </div>

                </div>
            </main>
        </div>
    )
}
