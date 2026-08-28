'use client'

import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchBookReviews, createBookReview, updateBookReview, deleteBookReview } from '@/lib/api'
import { BADGES, BADGE_CATEGORIES, findBadge } from '@/lib/badge_constants'
import type { ReviewData } from '@/lib/types'
import { Star, ChevronDown, ChevronUp, X, Pencil, Trash2, LogIn } from 'lucide-react'
import Toast from '@/components/ui/Toast'
import { sendGAEvent } from '@/lib/analytics'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'

interface BookReviewSectionProps {
  bookId: number
  bookTitle: string
}

// ─────────────────────────────────────────────────
// 별점 인라인 렌더
// ─────────────────────────────────────────────────
function StarRating({ rating, size = 16 }: { rating: number; size?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={`transition-colors ${i <= Math.round(rating) ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
          style={{ width: size, height: size }}
        />
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────────
// 별점 입력 컴포넌트
// ─────────────────────────────────────────────────
function StarInput({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex items-center gap-2">
      {[1, 2, 3, 4, 5].map((i) => (
        <button
          key={i}
          type="button"
          onClick={() => onChange(i)}
          className="p-1 active:scale-115 transition-transform"
          aria-label={`${i}점`}
        >
          <Star
            className={`w-9 h-9 transition-colors ${i <= value ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
          />
        </button>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────────
// 시간 포맷
// ─────────────────────────────────────────────────
function timeAgo(dateStr: string): string {
  const now = new Date()
  const d = new Date(dateStr)
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '방금 전'
  if (diffMin < 60) return `${diffMin}분 전`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}시간 전`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay < 7) return `${diffDay}일 전`
  if (diffDay < 30) return `${Math.floor(diffDay / 7)}주 전`
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' })
}


// ─────────────────────────────────────────────────
// 별점 반응형 라벨
// ─────────────────────────────────────────────────
function getRatingLabel(rating: number): string {
  switch (rating) {
    case 5: return '최고예요! 🌟'
    case 4: return '좋아요! 👍'
    case 3: return '보통이에요 🙂'
    case 2: return '아쉬워요 😅'
    case 1: return '별로예요 😢'
    default: return '별점을 남겨주세요'
  }
}

// ─────────────────────────────────────────────────
// 회원가입 정책 기준 랜덤 닉네임 생성기
// ─────────────────────────────────────────────────
const ADJECTIVES = ['지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', '마음넓은', '빛나는', '샘깊은', '글사랑', '봄날의']
const NOUNS = ['책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님', '글나무', '책나무']

function generateRandomNickname() {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
  return `${adj}${noun}`
}

// ─────────────────────────────────────────────────
// 메인 컴포넌트
// ─────────────────────────────────────────────────
export default function BookReviewSection({ bookId, bookTitle }: BookReviewSectionProps) {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [showWriteModal, setShowWriteModal] = useState(false)
  const [showLoginPrompt, setShowLoginPrompt] = useState(false)
  const [showAllReviews, setShowAllReviews] = useState(false)

  // 폼 상태
  const [nickname, setNickname] = useState('')
  const [childAge, setChildAge] = useState('')
  const [rating, setRating] = useState(0)
  const [selectedBadges, setSelectedBadges] = useState<string[]>([])
  const [content, setContent] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formError, setFormError] = useState('')

  // 수정 상태
  const [editingReviewId, setEditingReviewId] = useState<string | null>(null)
  const [editRating, setEditRating] = useState(0)
  const [editBadges, setEditBadges] = useState<string[]>([])
  const [editContent, setEditContent] = useState('')
  const [editChildAge, setEditChildAge] = useState('')
  const [editError, setEditError] = useState('')
  const [isEditSubmitting, setIsEditSubmitting] = useState(false)

  // 토스트 알림
  const [toastMessage, setToastMessage] = useState('')
  const [showToast, setShowToast] = useState(false)

  // 기존 리뷰 수정 모달 모드 (중복 방지용)
  const [isEditingExisting, setIsEditingExisting] = useState(false)

  // 삭제 확인 상태
  const [deletingReviewId, setDeletingReviewId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // 리뷰 데이터 로드
  const { data: reviewData, isLoading } = useQuery({
    queryKey: ['book-reviews', bookId],
    queryFn: () => fetchBookReviews(bookId),
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: false,
  })

  // 닉네임 / 아이 나이 초기화 (로컬스토리지 기억 복원)
  useEffect(() => {
    try {
      const saved = localStorage.getItem('checkjari_reviewer')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed.nickname) setNickname(parsed.nickname)
        if (parsed.childAge) setChildAge(parsed.childAge)
      }
    } catch { /* ignore */ }
  }, [])


  const userProfileName =
    user?.user_metadata?.nickname ||
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    ((user as any)?.email ? (user as any).email.split('@')[0] : '')

  const effectiveNickname = (
    userProfileName ||
    nickname ||
    generateRandomNickname()
  ).replace(/\s+/g, '')

  // 현재 로그인 유저의 기존 리뷰 (중복 방지 및 수정 모달 전환용)
  const myExistingReview = user
    ? ((reviewData?.reviews || []) as ReviewData[]).find((r) => r.user_id === user.id) ?? null
    : null

  const handleBadgeToggle = (badgeFull: string) => {
    setSelectedBadges((prev) =>
      prev.includes(badgeFull)
        ? prev.filter((b) => b !== badgeFull)
        : prev.length < 5
          ? [...prev, badgeFull]
          : prev // 최대 5개
    )
  }

  const resetForm = () => {
    setRating(0)
    setSelectedBadges([])
    setContent('')
    setFormError('')
    setIsEditingExisting(false)
    setShowWriteModal(false)
  }

  // access token 헬퍼
  const getAccessToken = async (): Promise<string> => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) throw new Error('로그인이 필요합니다.')
    return session.access_token
  }

  // 별점 클릭 시 팝업 열기 (비로그인이면 로그인 유도, 기존 리뷰 있으면 수정 모달)
  const handleStarClick = (starVal: number) => {
    if (!user) {
      setShowLoginPrompt(true)
      return
    }
    if (myExistingReview) {
      // 이미 리뷰가 있으면 기존 데이터로 수정 모달 열기
      setRating(myExistingReview.rating)
      setSelectedBadges(myExistingReview.selected_badges || [])
      setContent(myExistingReview.content || '')
      setChildAge(myExistingReview.child_age || '')
      setIsEditingExisting(true)
      setFormError('')
      setShowWriteModal(true)
      return
    }
    setRating(starVal)
    setFormError('')
    setShowWriteModal(true)
    sendGAEvent('click_inline_star_rating', {
      book_id: bookId,
      book_title: bookTitle,
      rating: starVal,
    })
  }

  // 수정 시작
  const handleEditStart = (review: ReviewData) => {
    setEditingReviewId(review.id)
    setEditRating(review.rating)
    setEditBadges(review.selected_badges || [])
    setEditContent(review.content || '')
    setEditChildAge(review.child_age || '')
    setEditError('')
  }

  const handleEditBadgeToggle = (badgeFull: string) => {
    setEditBadges((prev) =>
      prev.includes(badgeFull)
        ? prev.filter((b) => b !== badgeFull)
        : prev.length < 5 ? [...prev, badgeFull] : prev
    )
  }

  const handleEditSubmit = async (reviewId: string) => {
    if (editRating === 0) { setEditError('별점을 선택해 주세요'); return }
    if (editBadges.length === 0) { setEditError('키워드를 1개 이상 선택해 주세요'); return }
    if (editContent.trim().length > 0 && editContent.trim().length < 10) {
      setEditError('한줄평은 최소 10자 이상 작성해 주세요')
      return
    }
    setIsEditSubmitting(true)
    setEditError('')
    try {
      const token = await getAccessToken()
      await updateBookReview(bookId, reviewId, {
        rating: editRating,
        selected_badges: editBadges,
        content: editContent.trim() || undefined,
        child_age: editChildAge.trim() || undefined,
      }, token)
      queryClient.invalidateQueries({ queryKey: ['book-reviews', bookId] })
      setEditingReviewId(null)
      setToastMessage('리뷰가 수정되었어요')
      setShowToast(true)
    } catch (err: any) {
      setEditError(err.message || '수정 중 오류가 발생했습니다.')
    } finally {
      setIsEditSubmitting(false)
    }
  }

  const handleDelete = async (reviewId: string) => {
    setIsDeleting(true)
    try {
      const token = await getAccessToken()
      await deleteBookReview(bookId, reviewId, token)
      queryClient.invalidateQueries({ queryKey: ['book-reviews', bookId] })
      setDeletingReviewId(null)
    } catch (err: any) {
      console.error('Delete failed:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleSubmit = async () => {
    // 유효성 검증
    if (rating === 0) {
      setFormError('별점을 선택해 주세요')
      return
    }
    if (selectedBadges.length === 0) {
      setFormError('키워드를 1개 이상 선택해 주세요')
      return
    }
    if (content.trim().length > 0 && content.trim().length < 10) {
      setFormError('한줄평은 최소 10자 이상 작성해 주세요')
      return
    }

    setIsSubmitting(true)
    setFormError('')

    try {
      const token = await getAccessToken()

      if (isEditingExisting && myExistingReview) {
        // 기존 리뷰 수정 (모달에서 별점 클릭 → 수정 모드)
        await updateBookReview(bookId, myExistingReview.id, {
          rating,
          selected_badges: selectedBadges,
          content: content.trim() || undefined,
          child_age: childAge.trim() || undefined,
        }, token)
        setToastMessage('리뷰가 수정되었어요')
      } else {
        // 새 리뷰 등록
        await createBookReview(bookId, {
          nickname: effectiveNickname,
          child_age: childAge.trim() || undefined,
          rating,
          selected_badges: selectedBadges,
          content: content.trim() || undefined,
        }, token)

        // 아이 나이 로컬 저장 (다음 리뷰 시 재사용)
        try {
          localStorage.setItem(
            'checkjari_reviewer',
            JSON.stringify({ nickname: effectiveNickname, childAge: childAge.trim() })
          )
        } catch { /* ignore */ }

        // GA 이벤트
        sendGAEvent('submit_book_review', {
          book_id: bookId,
          book_title: bookTitle,
          rating,
          badge_count: selectedBadges.length,
        })
        setToastMessage('리뷰가 등록되었어요')
      }

      // 쿼리 갱신 & 폼 닫기
      queryClient.invalidateQueries({ queryKey: ['book-reviews', bookId] })
      setShowToast(true)
      resetForm()
    } catch (err) {
      console.error('Failed to submit review:', err)
      setFormError(isEditingExisting
        ? '리뷰 수정 중 오류가 발생했습니다. 다시 시도해 주세요.'
        : '리뷰 등록 중 오류가 발생했습니다. 다시 시도해 주세요.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const reviewCount = reviewData?.review_count || 0
  const avgRating = reviewData?.avg_rating
  const badgeCounts = reviewData?.badge_counts || {}
  const reviews = reviewData?.reviews || []
  const displayedReviews = showAllReviews ? reviews : reviews.slice(0, 3)

  // 뱃지 집계 정렬 (득표수 내림차순)
  const sortedBadgeCounts = Object.entries(badgeCounts).sort((a, b) => b[1] - a[1])

  return (
    <div className="mt-12 max-w-4xl mx-auto px-6">
      {/* ── 섹션 헤더 ── */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-black text-gray-900">
            리뷰
          </h3>
          {reviewCount > 0 && (
            <span className="text-sm text-gray-400 font-bold">{reviewCount}개</span>
          )}
        </div>
      </div>

      {/* ── 평점 요약 카드 (정돈된 상하 2열 컴팩트 카드) ── */}
      {reviewCount > 0 && (
        <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-4 sm:p-5 mb-4">
          {/* 상단: 평균 별점 & 평가 개수 (좌우 수평 균형 정렬) */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="text-3xl font-black text-gray-900 leading-none">
                {avgRating?.toFixed(1)}
              </span>
              <StarRating rating={avgRating || 0} size={18} />
            </div>
            <span className="text-xs text-gray-400 font-bold bg-gray-50 px-2.5 py-1 rounded-full border border-gray-100">
              총 {reviewCount}개 평가
            </span>
          </div>

          {/* 수평 구분선 */}
          {sortedBadgeCounts.length > 0 && (
            <div className="my-3.5 h-px bg-gray-100 w-full" />
          )}

          {/* 뱃지 득표 Top (칼같이 정돈된 2열 그리드 배열) */}
          {sortedBadgeCounts.length > 0 && (
            <div className="grid grid-cols-2 gap-2">
              {sortedBadgeCounts.slice(0, 6).map(([badge, count]) => {
                const badgeObj = findBadge(badge)
                return (
                  <div
                    key={badge}
                    className="flex items-center justify-between gap-1.5 px-3 py-2 bg-gray-50/90 rounded-xl text-xs sm:text-[13px] font-bold border border-gray-100/80"
                  >
                    <span className="text-gray-700 font-bold truncate">
                      {badgeObj?.emoji || '👍'} {badgeObj?.label || badge}
                    </span>
                    <span className="text-gray-900 font-extrabold text-[11px] bg-white px-1.5 py-0.5 rounded-md border border-gray-200/60 shrink-0">
                      {count}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* ── 밀리의 서재 스타일: 1-Tap 별점 직접 클릭 카드 ── */}
      <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-6 mb-5 text-center flex flex-col items-center justify-center">
        <div className="flex items-center justify-center gap-1.5 mb-2.5">
          {[1, 2, 3, 4, 5].map((starVal) => (
            <button
              key={starVal}
              type="button"
              onClick={() => handleStarClick(starVal)}
              className="p-1 active:scale-125 transition-transform group"
              aria-label={`${starVal}점 평가하기`}
            >
              <Star
                className={`w-9 h-9 transition-colors ${
                  myExistingReview && starVal <= Math.round(myExistingReview.rating)
                    ? 'text-amber-400 fill-amber-400'
                    : 'text-gray-200 group-hover:text-amber-400 group-hover:fill-amber-400'
                }`}
              />
            </button>
          ))}
        </div>
        <p className="text-sm sm:text-base font-bold text-gray-600">
          {myExistingReview
            ? '내 리뷰가 있어요. 별점을 눌러 수정할 수 있어요'
            : '이 책은 어떠셨나요? 별점을 남겨주세요'}
        </p>
      </div>

      {/* ── 비로그인 로그인 유도 모달 ── */}
      {showLoginPrompt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-[24px] shadow-2xl max-w-[340px] w-full p-6 relative animate-in zoom-in-95 duration-200">
            <button
              onClick={() => setShowLoginPrompt(false)}
              className="absolute top-5 right-5 p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors"
              aria-label="닫기"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex flex-col gap-3 mb-5 mt-1">
              <h4 className="text-[18px] font-black text-gray-900">로그인 후 리뷰를 남겨주세요</h4>
              <p className="text-[14px] text-gray-500 leading-relaxed">
                내가 남긴 리뷰를 나중에 수정하거나 삭제하려면 로그인이 필요해요.
              </p>
            </div>
            <a
              href="/login"
              className="flex items-center justify-center gap-2 w-full h-12 bg-brand-primary active:bg-brand-primary-dark text-white font-bold text-base rounded-xl transition-colors shadow-xs"
            >
              <LogIn className="w-5 h-5" />
              로그인하기
            </a>
          </div>
        </div>
      )}

      {/* ── 리뷰 작성 모달 팝업 ── */}
      {showWriteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-[24px] shadow-2xl max-w-[440px] w-full max-h-[90vh] overflow-y-auto p-6 relative animate-in zoom-in-95 duration-200">
            {/* 상단 닫기 */}
            <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-3">
              <h4 className="text-lg font-black text-gray-900">{isEditingExisting ? '리뷰 수정' : '리뷰 작성'}</h4>
              <button
                onClick={resetForm}
                className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors"
                aria-label="닫기"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 도서 정보 및 별점 피드백 */}
            <div className="text-center my-3">
              <p className="text-sm font-bold text-gray-500 mb-1 truncate px-4">{bookTitle}</p>
              <div className="text-xl font-black text-gray-900 mb-2">
                {getRatingLabel(rating)}
              </div>
              <div className="flex justify-center py-1">
                <StarInput value={rating} onChange={setRating} />
              </div>
            </div>

            {/* 키워드 뱃지 선택 (2단 카테고리) */}
            <div className="bg-gray-50/80 rounded-2xl p-4 my-4 border border-gray-100/80">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-base font-extrabold text-gray-900">어떤 점이 좋았나요?</h4>
                <span className="px-2 py-0.5 text-xs font-bold text-white bg-gray-900 rounded-md">필수</span>
              </div>
              <p className="text-sm font-semibold text-gray-500 mb-3">
                이 책에 어울리는 키워드를 골라주세요. (1~5개)
              </p>

              <div className="grid grid-cols-2 gap-2.5">
                {BADGE_CATEGORIES.map((cat) => {
                  const catBadges = BADGES.filter((b) => b.category === cat)
                  return (
                    <div key={cat} className="bg-white rounded-2xl p-2.5 border border-gray-100 shadow-2xs flex flex-col justify-between">
                      <div>
                        <h5 className="text-xs sm:text-sm font-black text-gray-800 mb-2 px-0.5">
                          {cat}
                        </h5>
                        <div className="flex flex-col gap-1.5">
                          {catBadges.map((badge) => {
                            const isSelected = selectedBadges.includes(badge.full)
                            return (
                              <button
                                key={badge.full}
                                type="button"
                                onClick={() => handleBadgeToggle(badge.full)}
                                className={`w-full flex items-center justify-start gap-1 px-2.5 py-2.5 rounded-xl text-[13px] font-bold border transition-all active:scale-[0.97] text-left leading-tight ${
                                  isSelected
                                    ? 'bg-brand-primary text-white border-brand-primary shadow-2xs font-extrabold'
                                    : 'bg-gray-50/70 text-gray-700 border-gray-100 hover:bg-gray-100/80 hover:border-gray-200'
                                }`}
                              >
                                <span className="text-sm shrink-0">{badge.emoji}</span>
                                <span className="truncate">{badge.label}</span>
                              </button>
                            )
                          })}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 한줄평/리뷰 내용 입력 */}
            <div className="mb-4">
              <p className="text-sm font-bold text-gray-700 mb-1.5">한 줄 리뷰 (선택)</p>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="이 책에 대한 솔직한 후기를 남겨주세요 (200자 이내) ☺️"
                maxLength={250}
                rows={3}
                className="w-full min-h-[85px] px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-[15px] font-medium leading-relaxed text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30 resize-none"
              />
            </div>

            {/* 아이 나이 */}
            <div className="mb-4">
              <p className="text-sm font-bold text-gray-700 mb-1.5">아이 나이 (선택)</p>
              <div className="relative">
                <select
                  value={childAge}
                  onChange={(e) => setChildAge(e.target.value)}
                  className={`w-full pl-4 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-[15px] font-medium appearance-none focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30 cursor-pointer ${
                    !childAge ? 'text-gray-400' : 'text-gray-900'
                  }`}
                >
                  <option value="" className="text-gray-400">선택</option>
                  <option value="0세" className="text-gray-900">0세</option>
                  <option value="1세" className="text-gray-900">1세</option>
                  <option value="2세" className="text-gray-900">2세</option>
                  <option value="3세" className="text-gray-900">3세</option>
                  <option value="4세" className="text-gray-900">4세</option>
                  <option value="5세" className="text-gray-900">5세</option>
                  <option value="6세" className="text-gray-900">6세</option>
                  <option value="7세" className="text-gray-900">7세</option>
                  <option value="8세" className="text-gray-900">8세</option>
                  <option value="9세" className="text-gray-900">9세</option>
                  <option value="10세" className="text-gray-900">10세</option>
                  <option value="11세" className="text-gray-900">11세</option>
                  <option value="12세" className="text-gray-900">12세</option>
                  <option value="13세 이상" className="text-gray-900">13세 이상</option>
                </select>
                <ChevronDown className="w-4 h-4 text-gray-400 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* 에러 메시지 */}
            {formError && (
              <p className="text-xs text-red-500 font-bold mb-3">{formError}</p>
            )}

            {/* 등록 버튼 */}
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full h-12 bg-brand-primary active:bg-brand-primary-dark text-white font-bold text-base rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-xs"
            >
              {isEditingExisting ? '수정하기' : '등록하기'}
            </button>
          </div>
        </div>
      )}

      {/* ── 리뷰 리스트 ── */}
      {/* ── 삭제 확인 모달 ── */}
      {deletingReviewId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-[24px] shadow-2xl max-w-[340px] w-full p-6 animate-in zoom-in-95 duration-200">
            <h4 className="text-[18px] font-black text-gray-900 mb-2">리뷰를 삭제할까요?</h4>
            <p className="text-[14px] text-gray-500 mb-5">삭제한 리뷰는 복구할 수 없어요.</p>
            <div className="flex gap-2">
              <button
                onClick={() => setDeletingReviewId(null)}
                className="flex-1 h-12 bg-gray-100 text-gray-700 font-bold rounded-xl active:bg-gray-200 transition-colors"
              >
                취소
              </button>
              <button
                onClick={() => handleDelete(deletingReviewId)}
                disabled={isDeleting}
                className="flex-1 h-12 bg-red-500 active:bg-red-600 text-white font-bold rounded-xl transition-colors disabled:opacity-50"
              >
                {isDeleting ? '삭제 중...' : '삭제'}
              </button>
            </div>
          </div>
        </div>
      )}

      {displayedReviews.length > 0 ? (
        <div className="space-y-3">
          {displayedReviews.map((review: ReviewData) => {
            const isOwn = user && review.user_id && review.user_id === user.id
            const isEditing = editingReviewId === review.id

            return (
            <div
              key={review.id}
              className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-4"
            >
              {/* 상단: 닉네임 + 별점 + 수정/삭제 */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[15px] text-gray-900">{review.nickname}</span>
                  {review.child_age && !isEditing && (
                    <span className="text-xs sm:text-sm text-gray-500 font-medium">({review.child_age})</span>
                  )}
                  {review.is_ai_generated && (
                    <span
                      className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-bold text-gray-500 bg-gray-100 rounded-full shrink-0"
                      title="책자리가 작성 방식을 안내하기 위해 만든 AI 생성 예시 리뷰입니다."
                    >
                      AI 생성 예시
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  {!isEditing && <StarRating rating={review.rating} size={15} />}
                  <span className="text-xs sm:text-sm text-gray-400">{timeAgo(review.created_at)}</span>
                  {isOwn && !isEditing && (
                    <>
                      <button
                        onClick={() => handleEditStart(review)}
                        className="p-1.5 text-gray-400 active:text-gray-700 rounded-lg transition-colors"
                        aria-label="수정"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeletingReviewId(review.id)}
                        className="p-1.5 text-gray-400 active:text-red-500 rounded-lg transition-colors"
                        aria-label="삭제"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>

              {isEditing ? (
                /* ── 인라인 수정 폼 ── */
                <div className="mt-2 space-y-3">
                  {/* 별점 */}
                  <div className="flex items-center gap-1">
                    {[1,2,3,4,5].map((i) => (
                      <button key={i} type="button" onClick={() => setEditRating(i)} className="p-0.5 active:scale-115 transition-transform">
                        <Star className={`w-7 h-7 transition-colors ${i <= editRating ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`} />
                      </button>
                    ))}
                  </div>
                  {/* 뱃지 */}
                  <div className="flex flex-wrap gap-1.5">
                    {BADGES.map((badge) => {
                      const isSel = editBadges.includes(badge.full)
                      return (
                        <button
                          key={badge.full}
                          type="button"
                          onClick={() => handleEditBadgeToggle(badge.full)}
                          className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full text-[12px] font-bold border transition-all active:scale-[0.97] ${
                            isSel ? 'bg-brand-primary text-white border-brand-primary' : 'bg-gray-50 text-gray-700 border-gray-200'
                          }`}
                        >
                          {badge.emoji} {badge.label}
                        </button>
                      )
                    })}
                  </div>
                  {/* 한줄평 */}
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    placeholder="한 줄 리뷰 (선택, 10자 이상)"
                    maxLength={250}
                    rows={2}
                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-[15px] font-medium text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary resize-none"
                  />
                  {/* 아이 나이 */}
                  <div className="relative">
                    <select
                      value={editChildAge}
                      onChange={(e) => setEditChildAge(e.target.value)}
                      className={`w-full pl-4 pr-10 py-2 bg-gray-50 border border-gray-200 rounded-xl text-[15px] font-medium appearance-none focus:outline-none focus:border-brand-primary cursor-pointer ${!editChildAge ? 'text-gray-400' : 'text-gray-900'}`}
                    >
                      <option value="">아이 나이 (선택)</option>
                      {['0세','1세','2세','3세','4세','5세','6세','7세','8세','9세','10세','11세','12세','13세 이상'].map((a) => (
                        <option key={a} value={a} className="text-gray-900">{a}</option>
                      ))}
                    </select>
                    <ChevronDown className="w-4 h-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  </div>
                  {editError && <p className="text-xs text-red-500 font-bold">{editError}</p>}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditingReviewId(null)}
                      className="flex-1 h-10 bg-gray-100 text-gray-700 font-bold rounded-xl text-sm active:bg-gray-200 transition-colors"
                    >
                      취소
                    </button>
                    <button
                      onClick={() => handleEditSubmit(review.id)}
                      disabled={isEditSubmitting}
                      className="flex-1 h-10 bg-brand-primary text-white font-bold rounded-xl text-sm active:bg-brand-primary-dark transition-colors disabled:opacity-50"
                    >
                      {isEditSubmitting ? '저장 중...' : '저장'}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {/* 선택한 뱃지 (단정한 한 줄 1-Line Flow) */}
                  {review.selected_badges && review.selected_badges.length > 0 && (
                    <div className="flex items-center gap-1.5 mb-2.5 overflow-x-auto scrollbar-hide py-0.5 whitespace-nowrap">
                      {review.selected_badges.map((badge) => {
                        const badgeObj = findBadge(badge)
                        return (
                          <span
                            key={badge}
                            className="inline-flex items-center gap-1 px-3 py-1 bg-white text-gray-700 rounded-full text-[13px] font-bold border border-gray-200 shrink-0"
                          >
                            {badgeObj?.emoji} {badgeObj?.label || badge}
                          </span>
                        )
                      })}
                    </div>
                  )}

                  {/* 본문 */}
                  {review.content && (
                    <p className="text-[15px] text-gray-800 leading-relaxed font-medium line-clamp-3">{review.content}</p>
                  )}
                </>
              )}
            </div>
          )})}


          {/* 더보기 / 접기 */}
          {reviews.length > 3 && (
            <button
              onClick={() => setShowAllReviews(!showAllReviews)}
              className="w-full py-3 flex items-center justify-center gap-1 text-base font-bold text-gray-600 active:text-gray-800 transition-colors"
            >
              {showAllReviews ? (
                <>접기 <ChevronUp className="w-4 h-4" /></>
              ) : (
                <>리뷰 {reviews.length - 3}개 더보기 <ChevronDown className="w-4 h-4" /></>
              )}
            </button>
          )}
        </div>
      ) : (
        !isLoading && reviewCount === 0 && !showWriteModal && (
          <div className="text-center py-8">
            <p className="text-sm sm:text-base text-gray-700 font-bold mb-1">아직 작성된 리뷰가 없어요</p>
            <p className="text-xs sm:text-sm text-gray-500 font-medium mb-4">첫 번째 후기의 주인공이 되어주세요!</p>
            <button
              type="button"
              onClick={() => handleStarClick(5)}
              className="inline-flex items-center justify-center gap-1.5 px-5 h-10 bg-white border border-gray-200 active:bg-gray-50 text-gray-600 font-bold text-xs sm:text-sm rounded-xl transition-all active:scale-[0.98] shadow-2xs"
            >
              <Pencil className="w-3.5 h-3.5 text-gray-400" />
              첫 리뷰 작성하기
            </button>
          </div>
        )
      )}

      <Toast
        message={toastMessage}
        isVisible={showToast}
        onClose={() => setShowToast(false)}
        duration={3000}
      />
    </div>
  )
}
