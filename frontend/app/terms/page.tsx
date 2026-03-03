import { Metadata } from 'next'
import Link from 'next/link'
import { ChevronLeft } from 'lucide-react'

export const metadata: Metadata = {
    title: '서비스 이용약관 | 책자리',
    description: '책자리 서비스 이용약관입니다.',
}

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-white border-b border-gray-100">
                <div className="max-w-3xl mx-auto px-4 h-14 flex items-center">
                    <Link href="/auth" className="flex items-center text-gray-600 hover:text-gray-900 transition-colors">
                        <ChevronLeft className="w-5 h-5 mr-1" />
                        <span className="text-sm font-medium">돌아가기</span>
                    </Link>
                    <h1 className="absolute left-1/2 -translate-x-1/2 text-lg font-bold text-gray-900">
                        서비스 이용약관
                    </h1>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-3xl mx-auto px-4 py-8 md:py-12">
                <div className="prose prose-slate max-w-none space-y-8">

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">제1장 총칙</h2>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제1조 [목적]</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                본 약관은 '책자리' 팀(이하 '회사'라고 합니다)이 제공하는 어린이 도서 탐색 및 청구기호 확인 서비스(웹, 모바일 웹•앱 서비스 등을 포함합니다, 이하 '서비스')를 이용함에 있어 '회원'과 '회사' 간의 권리, 의무 및 책임사항, 서비스 이용조건 등 기본적인 사항을 규정하는 것을 목적으로 합니다.
                            </p>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제2조 [용어 정의]</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                이 약관에서 사용하는 용어의 정의는 다음 각 호와 같습니다. 각 호에 정의된 용어 이외의, 약관 내 용어의 정의에 대해서는 관계 법령 및 서비스 안내에서 정하는 바에 따릅니다.
                            </p>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li><span className="font-semibold text-gray-700">서비스</span> : '회사'가 제공하는 도서 검색, 청구기호 정보 제공, 도서관 소장 정보 확인, 큐레이션 추천 등 제반 서비스를 말합니다.</li>
                                <li><span className="font-semibold text-gray-700">콘텐츠</span> : '서비스' 내에서 제공되는 도서 정보, 청구기호, 이미지, 텍스트, 큐레이션 태그 등의 모든 자료를 말합니다.</li>
                                <li><span className="font-semibold text-gray-700">회원</span> : '회사'와 이용계약을 체결하고(또는 비로그인 상태로) '회사'가 제공하는 서비스를 이용하는 자를 말합니다.</li>
                                <li><span className="font-semibold text-gray-700">계정(ID)</span> : '회원'의 식별과 서비스 이용을 위하여 '회원'이 선정하고 '회사'가 승인한 소셜 로그인 계정(카카오, 구글 등)을 말합니다.</li>
                                <li><span className="font-semibold text-gray-700">게시물</span> : '회원'이 서비스를 이용하는 과정에서 작성한 텍스트, 이미지, 링크 등의 정보나 자료(오류 신고, 피드백 등 포함)를 의미합니다.</li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제3조 [약관의 효력 및 변경]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회사'는 본 약관의 내용을 '회원'이 쉽게 알 수 있도록 서비스 내 메뉴 또는 연결화면을 통하여 게시합니다.</li>
                                <li>'회사'는 관련 법령을 위배하지 않는 범위에서 본 약관을 개정할 수 있습니다.</li>
                                <li>'회사'가 약관을 개정할 경우에는 적용일자 및 개정사유를 명시하여 현행 약관과 함께 서비스 내 공지사항 등을 통해 그 적용일자 7일 이전부터 적용일자 전일까지 공지합니다. 다만, '회원'에게 불리한 약관의 개정의 경우에는 30일 이상의 유예기간을 두고 공지합니다.</li>
                                <li>'회원'이 개정약관의 적용에 동의하지 않는 경우 '회원'은 이용계약을 해지(회원탈퇴)할 수 있습니다.</li>
                            </ol>
                        </section>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">제2장 회원</h2>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제4조 [회원 가입]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'서비스'를 이용하고자 하는 자는 '회사'가 정한 가입 절차(소셜 로그인 등)에 따라 본 약관 및 개인정보 처리방침에 동의함으로써 이용계약을 체결합니다.</li>
                                <li>'회사'는 다음 각 호에 해당하는 신청에 대하여 승낙을 거부하거나 유보할 수 있습니다.
                                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-500">
                                        <li>만 14세 미만의 아동이 법정대리인의 동의 없이 가입을 신청한 경우</li>
                                        <li>타인의 명의나 계정을 도용하여 신청한 경우</li>
                                        <li>사회의 안녕질서 또는 미풍양속을 저해할 목적으로 신청한 경우</li>
                                        <li>기타 '회사'가 정한 제반 사항을 위반하여 신청하는 경우</li>
                                    </ul>
                                </li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제5조 [회원정보의 변경]</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                '회원'은 개인정보관리화면을 통하여 언제든지 본인의 개인정보를 열람하고 수정할 수 있습니다. 다만, 서비스 관리를 위해 필요한 실명, 아이디 등은 수정이 불가능할 수 있습니다.
                            </p>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제6조 [회원의 의무]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회원'은 관계법령, 이 약관의 규정, 이용안내 및 서비스와 관련하여 공지한 주의사항, '회사'가 통지하는 사항 등을 준수하여야 하며, 기타 '회사'의 업무에 방해되는 행위를 하여서는 안 됩니다.</li>
                                <li>'회원'은 다음 행위를 하여서는 안 됩니다.
                                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-500">
                                        <li>신청 또는 변경 시 허위내용의 등록</li>
                                        <li>타인의 정보 도용</li>
                                        <li>'회사'가 게시한 정보의 변경</li>
                                        <li>'회사'가 정한 정보 이외의 정보(컴퓨터 프로그램 등) 등의 송신 또는 게시</li>
                                        <li>'회사' 및 기타 제3자의 저작권 등 지적재산권에 대한 침해</li>
                                        <li>'회사' 및 기타 제3자의 명예를 손상시키거나 업무를 방해하는 행위</li>
                                        <li>외설 또는 폭력적인 메시지, 화상, 음성, 기타 공서양속에 반하는 정보를 서비스에 공개 또는 게시하는 행위</li>
                                        <li>'회사'의 동의 없이 영리를 목적으로 서비스를 사용하는 행위</li>
                                    </ul>
                                </li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제7조 [회원탈퇴 및 자격 상실 등]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회원'은 언제든지 서비스 내 설정 메뉴 등을 통하여 이용계약 해지 신청(회원탈퇴)을 할 수 있으며, '회사'는 관련 법령 등이 정하는 바에 따라 이를 즉시 처리하여야 합니다.</li>
                                <li>'회원'이 탈퇴할 경우, 관련 법령 및 개인정보 처리방침에 따라 '회사'가 회원정보를 보유하는 경우를 제외하고는 해지 즉시 '회원'의 모든 데이터는 소멸됩니다.</li>
                                <li>'회원'이 제6조의 의무를 위반하거나 서비스의 정상적인 운영을 방해한 경우, '회사'는 사전 통지 없이 회원 자격을 제한, 정지 또는 상실시킬 수 있습니다.</li>
                            </ol>
                        </section>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">제3장 서비스 이용</h2>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제8조 [서비스의 제공 및 변경]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'서비스'는 연중무휴, 1일 24시간 제공함을 원칙으로 합니다.</li>
                                <li>'회사'는 컴퓨터 등 정보통신설비의 보수점검, 교체 및 고장, 통신두절 또는 운영상 상당한 이유가 있는 경우 '서비스'의 제공을 일시적으로 중단할 수 있습니다.</li>
                                <li>'회사'는 운영상, 기술상의 필요에 따라 제공하고 있는 전부 또는 일부 '서비스'를 변경할 수 있습니다. 이에 대하여 관련 법령에 특별한 규정이 없는 한 '회원'에게 별도의 보상을 하지 않습니다.</li>
                                <li>'서비스'에서 제공하는 청구기호 및 도서관 소장 정보는 도서관 시스템 상황에 따라 실제와 다를 수 있으며, '회사'는 정보의 완전무결성을 보장하지 않습니다.</li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제9조 [정보의 제공 및 광고의 게재]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회사'는 '서비스' 운용과 관련하여 서비스 화면, 홈페이지, 푸시 알림 등에 광고를 게재할 수 있습니다.</li>
                                <li>'회원'은 '서비스' 이용 시 노출되는 광고 게재에 대해 동의합니다.</li>
                                <li>'회원'이 광고를 통해 제3자가 제공하는 서비스나 재화 등을 이용하는 경우, 이는 '회원'과 제3자 간의 법률관계이므로 '회사'는 이에 개입하거나 책임지지 않습니다.</li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제10조 [책임제한]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회사'는 천재지변 또는 이에 준하는 불가항력으로 인하여 '서비스'를 제공할 수 없는 경우에는 '서비스' 제공에 관한 책임이 면제됩니다.</li>
                                <li>'회사'는 '회원'의 귀책사유로 인한 '서비스' 이용의 장애에 대하여는 책임을 지지 않습니다.</li>
                                <li>'회사'는 '회원'이 '서비스'와 관련하여 게재한 정보, 자료, 사실의 신뢰도, 정확성 등의 내용에 관하여는 책임을 지지 않습니다.</li>
                                <li>'회사'는 무료로 제공되는 서비스 이용과 관련하여 관련 법령에 특별한 규정이 없는 한 책임을 지지 않습니다.</li>
                                <li>본 '서비스'가 제공하는 청구기호 및 도서 위치 정보는 참고용이며, 실제 도서관에서의 도서 위치와 일치하지 않을 수 있습니다. 이로 인한 이용자의 불편이나 손해에 대해 '회사'는 책임을 지지 않습니다.</li>
                            </ol>
                        </section>

                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">제11조 [재판권 및 준거법]</h3>
                            <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                                <li>'회사'와 '회원' 간 제기된 소송은 대한민국법을 준거법으로 합니다.</li>
                                <li>'회사'와 '회원' 간 발생한 분쟁에 관한 소송은 민사소송법 상의 관할법원에 제기합니다.</li>
                            </ol>
                        </section>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-gray-100">
                        <h2 className="text-xl font-bold text-gray-900">부칙</h2>
                        <p className="text-sm text-gray-600">
                            1. 이 약관은 2026년 3월 1일부터 시행합니다.
                        </p>
                    </div>

                </div>
            </main>
        </div>
    )
}
