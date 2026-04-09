import { Metadata } from 'next'
import PageHeader from '@/components/PageHeader'

export const metadata: Metadata = {
    title: '개인정보 처리방침 | 책자리',
    description: '책자리 개인정보 처리방침입니다.',
}

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-white">
            <PageHeader title="개인정보 처리방침" />

            {/* Content */}
            <main className="max-w-3xl mx-auto px-4 py-8 md:py-12">
                <div className="prose prose-slate max-w-none space-y-8">

                    <p className="text-sm text-gray-600 leading-relaxed">
                        '책자리' 팀(이하 '회사'라고 합니다)은 회원의 개인정보를 중요시하며, "정보통신망 이용촉진 및 정보보호"에 관한 법률을 준수하고 있습니다.
                        회사는 개인정보처리방침을 통하여 회원이 제공하는 개인정보가 어떠한 용도와 방식으로 이용되고 있으며, 개인정보보호를 위해 어떠한 조치가 취해지고 있는지 알려드립니다.
                    </p>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">1. 개인정보 수집 및 이용 목적</h2>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            회사는 다음의 목적을 위하여 개인정보를 처리합니다. 처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는 경우에는 개인정보 보호법 제18조에 따라 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.
                        </p>
                        <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                            <li><span className="font-semibold text-gray-700">회원 가입 및 관리</span> : 회원 가입 의사 확인, 회원제 서비스 제공에 따른 본인 식별·인증, 회원자격 유지·관리, 제한적 본인확인제 시행에 따른 본인확인, 서비스 부정이용 방지, 만 14세 미만 아동의 개인정보 처리 시 법정대리인의 동의 여부 확인, 각종 고지·통지, 고충처리 등을 목적으로 개인정보를 처리합니다.</li>
                            <li><span className="font-semibold text-gray-700">재화 또는 서비스 제공</span> : 서비스 제공, 콘텐츠 제공, 맞춤 서비스 제공, 본인인증 등을 목적으로 개인정보를 처리합니다.</li>
                            <li><span className="font-semibold text-gray-700">고충처리</span> : 민원인의 신원 확인, 민원사항 확인, 사실조사를 위한 연락·통지, 처리결과 통보 등의 목적으로 개인정보를 처리합니다.</li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">2. 수집하는 개인정보의 항목 및 수집방법</h2>
                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">1) 수집하는 개인정보의 항목</h3>
                            <ul className="list-disc pl-5 text-sm text-gray-600 space-y-2">
                                <li><strong>소셜 로그인(Kakao, Google) 시</strong>:
                                    <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-500">
                                        <li>필수항목: 이메일, 로그인 ID(Provider ID)</li>
                                        <li>선택항목(프로필 정보 설정 시): 닉네임, 프로필 사진</li>
                                    </ul>
                                </li>
                                <li><strong>서비스 이용 과정에서 자동 생성되어 수집되는 항목</strong>: IP Address, 쿠키, 방문 일시, 서비스 이용 기록, 불량 이용 기록, 기기 정보</li>
                            </ul>
                        </section>
                        <section className="space-y-3">
                            <h3 className="text-base font-bold text-gray-800">2) 수집방법</h3>
                            <ul className="list-disc pl-5 text-sm text-gray-600 space-y-2">
                                <li>홈페이지(회원가입), 소셜 로그인 연동, 제휴사로부터의 제공</li>
                                <li>생성정보 수집 툴을 통한 수집</li>
                            </ul>
                        </section>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">3. 개인정보의 보유 및 이용기간</h2>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에 동의받은 개인정보 보유·이용기간 내에서 개인정보를 처리·보유합니다.
                        </p>
                        <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                            <li><span className="font-semibold text-gray-700">회원 가입 및 관리</span> : 회원 탈퇴 시까지 (단, 타 법령에 의하여 보존할 필요가 있는 경우에는 해당 법령에서 정한 기간 동안 보존합니다.)</li>
                            <li><span className="font-semibold text-gray-700">관계 법령에 의한 정보보유 사유</span> : 통신비밀보호법에 따른 로그인 기록 3개월 보관</li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">4. 개인정보의 제3자 제공</h2>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            회사는 정보주체의 개인정보를 제1조(개인정보 수집 및 이용 목적)에서 명시한 범위 내에서만 처리하며, 정보주체의 동의, 법률의 특별한 규정 등 개인정보 보호법 제17조 및 제18조에 해당하는 경우에만 개인정보를 제3자에게 제공합니다.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">5. 개인정보처리의 위탁</h2>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            회사는 원활한 개인정보 업무처리를 위하여 다음과 같이 개인정보 처리업무를 위탁하고 있습니다. 위탁업무의 내용이나 수탁자가 변경될 경우에는 지체 없이 본 개인정보 처리방침을 통하여 공개하도록 하겠습니다.
                        </p>
                        <ul className="list-disc pl-5 text-sm text-gray-600 space-y-2">
                            <li><strong>데이터베이스 호스팅</strong>: Supabase Inc.</li>
                            <li><strong>웹 호스팅</strong>: Vercel Inc., Render Services Inc.</li>
                        </ul>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">6. 이용자 및 법정대리인의 권리와 그 행사방법</h2>
                        <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                            <li>정보주체는 회사에 대해 언제든지 개인정보 열람·정정·삭제·처리정지 요구 등의 권리를 행사할 수 있습니다.</li>
                            <li>권리 행사는 서면, 전화, 전자우편, 모사전송(FAX) 등을 통하여 하실 수 있으며 회사는 이에 대해 지체 없이 조치하겠습니다.</li>
                            <li>이용자가 개인정보의 오류에 대한 정정을 요청한 경우에는 정정을 완료하기 전까지 당해 개인정보를 이용 또는 제공하지 않습니다.</li>
                            <li>만 14세 미만 아동의 경우, 법정대리인이 아동의 개인정보 조회/수정 및 가입해지(동의철회)를 요청할 권리를 가집니다.</li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">7. 개인정보 자동 수집 장치의 설치·운영 및 거부에 관한 사항</h2>
                        <ol className="list-decimal pl-5 text-sm text-gray-600 space-y-2">
                            <li>회사는 이용자에게 개별적인 맞춤서비스를 제공하기 위해 이용정보를 저장하고 수시로 불러오는 '쿠키(cookie)'를 사용합니다.</li>
                            <li>쿠키는 웹사이트를 운영하는데 이용되는 서버가 이용자의 브라우저에 보내는 소량의 정보이며, 이용자의 단말기(PC, 스마트폰 등)에 저장되기도 합니다.</li>
                            <li>쿠키 저장을 거부할 경우 맞춤형 서비스 이용에 어려움이 발생할 수 있습니다.</li>
                        </ol>
                    </div>

                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-900 border-b border-gray-200 pb-2">8. 개인정보 보호책임자</h2>
                        <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600">
                            <p className="font-bold text-gray-800 mb-1">개인정보 보호책임자</p>
                            <p>성명: 책자리 팀</p>
                            <p>이메일: <a href="mailto:privacy@checkjari.com" className="text-blue-600 hover:underline">privacy@checkjari.com</a></p>
                        </div>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-gray-100">
                        <h2 className="text-xl font-bold text-gray-900">부칙</h2>
                        <p className="text-sm text-gray-600">
                            이 개인정보 처리방침은 2026년 3월 1일부터 적용됩니다.
                        </p>
                    </div>

                </div>
            </main>
        </div>
    )
}
