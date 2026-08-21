'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ConfirmModal from '@/components/ui/ConfirmModal'

export default function SignupWelcomeModal() {
  const [isOpen, setIsOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (sessionStorage.getItem('showSignupComplete') === 'true') {
        setIsOpen(true)
        sessionStorage.removeItem('showSignupComplete')
      }
    }
  }, [])

  if (!isOpen) return null

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      onConfirm={() => {
        setIsOpen(false)
        router.push('/my-page?action=select-library')
      }}
      title="회원 가입을 축하해요! 🎉"
      description={
        <div className="text-gray-600 leading-[1.6] break-keep">
          책자리 가입이 완료되었습니다.<br />
          <span className="font-bold text-amber-600">자주 가는 도서관 1곳</span>을 설정하시면,<br />
          찜한 책의 대출 가능 여부를 바로 확인할 수 있어요!
        </div>
      }
      confirmLabel="내 도서관 설정하기"
      cancelLabel=""
      hideCloseButton={false}
      confirmVariant="primary"
      hideOverlay
    />
  )
}
