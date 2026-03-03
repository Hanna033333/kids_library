'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Check } from 'lucide-react'

interface Agreements {
    allAgreed: boolean
    ageConfirmed: boolean
    termsAgreed: boolean
    privacyAgreed: boolean
    marketingAgreed: boolean
}

export default function AgreementsPage() {
    const router = useRouter()
    const [agreements, setAgreements] = useState<Agreements>({
        allAgreed: false,
        ageConfirmed: false,
        termsAgreed: false,
        privacyAgreed: false,
        marketingAgreed: false
    })

    const handleAllAgree = (checked: boolean) => {
        setAgreements({
            allAgreed: checked,
            ageConfirmed: checked,
            termsAgreed: checked,
            privacyAgreed: checked,
            marketingAgreed: checked
        })
    }

    const handleIndividualAgree = (key: keyof Agreements, checked: boolean) => {
        const newAgreements = { ...agreements, [key]: checked }

        // 필수 항목만 체크되었을 때 모두 동의가 활성화되지 않도록, 
        // 실제 모든 항목이 체크되었을 때만 allAgreed를 true로 설정하거나
        // 이미지 디자인에 따라 '모두 동의' 동작을 정의합니다.
        const allChecked = newAgreements.ageConfirmed &&
            newAgreements.termsAgreed &&
            newAgreements.privacyAgreed &&
            newAgreements.marketingAgreed

        newAgreements.allAgreed = allChecked
        setAgreements(newAgreements)
    }

    const isValid = agreements.ageConfirmed &&
        agreements.termsAgreed &&
        agreements.privacyAgreed

    const handleNext = () => {
        if (!isValid) return
        sessionStorage.setItem('signup_agreements', JSON.stringify(agreements))
        router.push('/auth/set-password')
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white px-6 py-12">
            <div className="w-full max-w-sm flex flex-col items-center">
                {/* 헤더 */}
                <div className="text-center mb-10 flex flex-col items-center">
                    <img
                        src="/logo.png"
                        alt="책자리"
                        className="w-20 h-auto mb-6"
                    />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">회원가입</h2>
                    <p className="text-gray-500 text-[15px]">서비스 약관에 동의해주세요</p>
                </div>

                {/* 약관 동의 영역 */}
                <div className="w-full bg-gray-50/50 rounded-[24px] p-6 mb-8 border border-gray-100/50">
                    {/* 모두 동의 */}
                    <div className="flex items-center mb-5">
                        <label className="flex items-center gap-3 cursor-pointer group w-full">
                            <div className="relative flex items-center justify-center">
                                <input
                                    type="checkbox"
                                    checked={agreements.allAgreed}
                                    onChange={(e) => handleAllAgree(e.target.checked)}
                                    className="peer sr-only"
                                />
                                <div className={`w-[22px] h-[22px] rounded-[5px] transition-all flex items-center justify-center border-[1.5px]
                                    ${agreements.allAgreed ? 'bg-brand-primary border-brand-primary' : 'bg-white border-gray-300'}`}>
                                    <Check className={`w-3.5 h-3.5 stroke-[3.5] transition-colors
                                        ${agreements.allAgreed ? 'text-white' : 'text-transparent'}`} />
                                </div>
                            </div>
                            <span className="font-bold text-gray-900 text-[17px]">모두 동의</span>
                        </label>
                    </div>

                    <div className="h-[1px] bg-gray-200/60 w-full mb-5"></div>

                    {/* 개별 항목 리스트 */}
                    <div className="space-y-6 text-zinc-400">
                        {/* 만 14세 이상 */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-3 cursor-pointer group flex-1">
                                <div className="relative flex items-center justify-center w-6">
                                    <input
                                        type="checkbox"
                                        checked={agreements.ageConfirmed}
                                        onChange={(e) => handleIndividualAgree('ageConfirmed', e.target.checked)}
                                        className="peer sr-only"
                                    />
                                    <div className="transition-all flex items-center justify-center">
                                        <Check className={`w-5 h-5 stroke-[1.5] transition-colors
                                            ${agreements.ageConfirmed ? 'text-brand-primary' : 'text-gray-200'}`} />
                                    </div>
                                </div>
                                <span className="text-gray-700 text-[15px] font-medium tracking-tight">[필수] 만 14세 이상입니다.</span>
                            </label>
                        </div>

                        {/* 서비스 이용약관 */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-3 cursor-pointer group flex-1">
                                <div className="relative flex items-center justify-center w-6">
                                    <input
                                        type="checkbox"
                                        checked={agreements.termsAgreed}
                                        onChange={(e) => handleIndividualAgree('termsAgreed', e.target.checked)}
                                        className="peer sr-only"
                                    />
                                    <div className="transition-all flex items-center justify-center">
                                        <Check className={`w-5 h-5 stroke-[1.5] transition-colors
                                            ${agreements.termsAgreed ? 'text-brand-primary' : 'text-gray-200'}`} />
                                    </div>
                                </div>
                                <span className="text-gray-700 text-[15px] font-medium tracking-tight">[필수] 서비스 이용약관</span>
                            </label>
                            <button
                                onClick={() => window.open('/terms', '_blank')}
                                className="text-gray-400 text-[13px] hover:text-gray-600 transition-colors ml-4 shrink-0"
                            >
                                보기 &gt;
                            </button>
                        </div>

                        {/* 개인정보 수집 및 이용 */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-3 cursor-pointer group flex-1">
                                <div className="relative flex items-center justify-center w-6">
                                    <input
                                        type="checkbox"
                                        checked={agreements.privacyAgreed}
                                        onChange={(e) => handleIndividualAgree('privacyAgreed', e.target.checked)}
                                        className="peer sr-only"
                                    />
                                    <div className="transition-all flex items-center justify-center">
                                        <Check className={`w-5 h-5 stroke-[1.5] transition-colors
                                            ${agreements.privacyAgreed ? 'text-brand-primary' : 'text-gray-200'}`} />
                                    </div>
                                </div>
                                <span className="text-gray-700 text-[15px] font-medium tracking-tight">[필수] 개인정보 수집 및 이용</span>
                            </label>
                            <button
                                onClick={() => window.open('/privacy', '_blank')}
                                className="text-gray-400 text-[13px] hover:text-gray-600 transition-colors ml-4 shrink-0"
                            >
                                보기 &gt;
                            </button>
                        </div>

                        {/* 이벤트/혜택 정보 수신 */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-3 cursor-pointer group flex-1">
                                <div className="relative flex items-center justify-center w-6">
                                    <input
                                        type="checkbox"
                                        checked={agreements.marketingAgreed}
                                        onChange={(e) => handleIndividualAgree('marketingAgreed', e.target.checked)}
                                        className="peer sr-only"
                                    />
                                    <div className="transition-all flex items-center justify-center">
                                        <Check className={`w-5 h-5 stroke-[1.5] transition-colors
                                            ${agreements.marketingAgreed ? 'text-brand-primary' : 'text-gray-200'}`} />
                                    </div>
                                </div>
                                <span className="text-gray-700 text-[15px] font-medium tracking-tight">[선택] 이벤트·혜택 정보 수신 및 활용 동의</span>
                            </label>
                            <button
                                onClick={() => window.open('/marketing', '_blank')}
                                className="text-gray-400 text-[13px] hover:text-gray-600 transition-colors ml-4 shrink-0"
                            >
                                보기 &gt;
                            </button>
                        </div>
                    </div>
                </div>

                {/* 다음 버튼 */}
                <Button
                    onClick={handleNext}
                    disabled={!isValid}
                    variant="primary"
                    size="lg"
                    className={`w-full rounded-xl h-[56px] text-lg font-bold shadow-sm transition-all
                        ${isValid ? 'opacity-100' : 'opacity-40 brightness-95'}`}
                >
                    다음
                </Button>
            </div>
        </div>
    )
}
