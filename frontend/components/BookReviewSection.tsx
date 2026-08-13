'use client'

import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchBookReviews, createBookReview } from '@/lib/api'
import { BADGES, findBadge } from '@/lib/badge_constants'
import type { ReviewData } from '@/lib/types'
import { Star, MessageCircle, ChevronDown, ChevronUp, X } from 'lucide-react'
import { sendGAEvent } from '@/lib/analytics'
import { useAuth } from '@/context/AuthContext'

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
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <button
          key={i}
          type="button"
          onClick={() => onChange(i)}
          className="p-1 active:scale-110 transition-transform"
          aria-label={`${i}점`}
        >
          <Star
            className={`w-8 h-8 transition-colors ${i <= value ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
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
// 메인 컴포넌트
// ─────────────────────────────────────────────────
export default function BookReviewSection({ bookId, bookTitle }: BookReviewSectionProps) {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [showWriteForm, setShowWriteForm] = useState(false)
  const [showAllReviews, setShowAllReviews] = useState(false)

  // 폼 상태
  const [nickname, setNickname] = useState('')
  const [childAge, setChildAge] = useState('')
  const [rating, setRating] = useState(0)
  const [selectedBadges, setSelectedBadges] = useState<string[]>([])
  const [content, setContent] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formError, setFormError] = useState('')

  // 리뷰 데이터 로드
  const { data: reviewData, isLoading } = useQuery({
    queryKey: ['book-reviews', bookId],
    queryFn: () => fetchBookReviews(bookId),
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: false,
  })

  // 닉네임 / 아이 나이 초기화 (로그인 유저 정보 우선 -> 로컬스토리지 기억 복원)
  useEffect(() => {
    // 1. 로그인 유저의 닉네임 추출 (meta 데이터 또는 구글/카카오 이름)
    const userProfileName =
      user?.user_metadata?.full_name ||
      user?.user_metadata?.name ||
      user?.user_metadata?.nickname ||
      (user?.email ? user.email.split('@')[0] : '')

    if (userProfileName) {
      setNickname(userProfileName)
    } else {
      // 2. 비로그인 유저인 경우 이전 로컬스토리지 저장 닉네임 복원
      try {
        const saved = localStorage.getItem('checkjari_reviewer')
        if (saved) {
          const parsed = JSON.parse(saved)
          if (parsed.nickname) setNickname(parsed.nickname)
        }
      } catch { /* ignore */ }
    }

    // 아이 나이 로컬스토리지 복원
    try {
      const saved = localStorage.getItem('checkjari_reviewer')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed.childAge) setChildAge(parsed.childAge)
      }
    } catch { /* ignore */ }
  }, [user])

  const handleBadgeToggle = (badgeFull: string) => {
    setSelectedBadges((prev) =>
      prev.includes(badgeFull)
        ? prev.filter((b) => b !== badgeFull)
        : prev.length < 3
          ? [...prev, badgeFull]
          : prev // 최대 3개
    )
  }

  const resetForm = () => {
    setRating(0)
    setSelectedBadges([])
    setContent('')
    setFormError('')
    setShowWriteForm(false)
  }

  const handleSubmit = async () => {
    // 유효성 검증
    if (!nickname.trim()) {
      setFormError('닉네임을 입력해 주세요')
      return
    }
    if (rating === 0) {
      setFormError('별점을 선택해 주세요')
      return
    }

    setIsSubmitting(true)
    setFormError('')

    try {
      await createBookReview(bookId, {
        nickname: nickname.trim(),
        child_age: childAge.trim() || undefined,
        rating,
        selected_badges: selectedBadges,
        content: content.trim() || undefined,
      })

      // 닉네임/아이 나이 로컬 저장 (다음 리뷰 시 재사용)
      try {
        localStorage.setItem(
          'checkjari_reviewer',
          JSON.stringify({ nickname: nickname.trim(), childAge: childAge.trim() })
        )
      } catch { /* ignore */ }

      // GA 이벤트
      sendGAEvent('submit_book_review', {
        book_id: bookId,
        book_title: bookTitle,
        rating,
        badge_count: selectedBadges.length,
      })

      // 캐시 무효화 및 폼 리셋
      queryClient.invalidateQueries({ queryKey: ['book-reviews', bookId] })
      resetForm()
    } catch (err) {
      console.error('리뷰 등록 실패:', err)
      setFormError('등록에 실패했습니다. 다시 시도해 주세요.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const reviewCount = reviewData?.review_count || 0
  const avgRating = reviewData?.avg_rating
  const badgeCounts = reviewData?.badge_counts || {}
  const reviews = reviewData?.reviews || []
  const displayedReviews = showAllReviews ? reviews : reviews.slice(0, 3)

  // 뱃지 득표순 정렬
  const sortedBadgeCounts = Object.entries(badgeCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6) // 상위 6개만 노출

  return (
    <div className="mt-12 max-w-4xl mx-auto px-6">
      {/* ── 섹션 헤더 ── */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-black text-gray-900 flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-brand-primary" />
            부모님 한줄평
          </h3>
          {reviewCount > 0 && (
            <span className="text-sm text-gray-400 font-bold">{reviewCount}개</span>
          )}
        </div>
      </div>

      {/* ── 평점 요약 카드 ── */}
      {reviewCount > 0 && (
        <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-5 mb-5">
          <div className="flex items-center gap-4 mb-4">
            {/* 평균 별점 */}
            <div className="flex flex-col items-center gap-1">
              <span className="text-3xl font-black text-gray-900">
                {avgRating?.toFixed(1)}
              </span>
              <StarRating rating={avgRating || 0} size={14} />
            </div>

            {/* 구분선 */}
            <div className="w-px h-12 bg-gray-100" />

            {/* 뱃지 득표 Top */}
            <div className="flex-1 flex flex-wrap gap-1.5">
              {sortedBadgeCounts.map(([badge, count]) => {
                const badgeObj = findBadge(badge)
                return (
                  <span
                    key={badge}
                    className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 text-amber-800 rounded-full text-[11px] font-bold border border-amber-100"
                  >
                    {badgeObj?.emoji || '👍'} {badgeObj?.label || badge}
                    <span className="text-amber-500 ml-0.5">{count}</span>
                  </span>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── 한줄평 작성 버튼 ── */}
      {!showWriteForm && (
        <button
          onClick={() => setShowWriteForm(true)}
          className="w-full py-3.5 bg-brand-primary/5 text-brand-primary font-bold text-sm rounded-xl border border-brand-primary/10 active:bg-brand-primary/10 active:scale-[0.99] transition-all mb-5"
        >
          ✏️ 한줄평 남기기
        </button>
      )}

      {/* ── 한줄평 작성 폼 ── */}
      {showWriteForm && (
        <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] border border-gray-100 p-5 mb-5 animate-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-base font-black text-gray-900">한줄평 작성</h4>
            <button onClick={resetForm} className="p-1 text-gray-400 active:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* 별점 */}
          <div className="mb-4">
            <p className="text-xs font-bold text-gray-500 mb-2">별점</p>
            <StarInput value={rating} onChange={setRating} />
          </div>

          {/* 뱃지 선택 */}
          <div className="mb-4">
            <p className="text-xs font-bold text-gray-500 mb-2">이 책 어떠셨나요? (최대 3개)</p>
            <div className="flex flex-wrap gap-2">
              {BADGES.map((badge) => {
                const isSelected = selectedBadges.includes(badge.full)
                return (
                  <button
                    key={badge.full}
                    type="button"
                    onClick={() => handleBadgeToggle(badge.full)}
                    className={`inline-flex items-center gap-1 px-3 py-2 rounded-full text-[12px] font-bold border transition-all active:scale-[0.97] ${
                      isSelected
                        ? 'bg-brand-primary text-white border-brand-primary shadow-sm'
                        : 'bg-gray-50 text-gray-600 border-gray-200 active:bg-gray-100'
                    }`}
                  >
                    <span className="text-sm">{badge.emoji}</span>
                    {badge.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* 닉네임 + 아이 나이 */}
          <div className="flex gap-3 mb-3">
            <div className="flex-1">
              <p className="text-xs font-bold text-gray-500 mb-1.5">닉네임</p>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="예: 서아맘"
                maxLength={20}
                className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30"
              />
            </div>
            <div className="w-24">
              <p className="text-xs font-bold text-gray-500 mb-1.5">아이 나이</p>
              <input
                type="text"
                value={childAge}
                onChange={(e) => setChildAge(e.target.value)}
                placeholder="예: 3세"
                maxLength={10}
                className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30"
              />
            </div>
          </div>

          {/* 한줄평 입력 */}
          <div className="mb-4">
            <p className="text-xs font-bold text-gray-500 mb-1.5">한줄평 (선택)</p>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="이 책에 대한 솔직한 후기를 남겨주세요 ☺️"
              maxLength={500}
              rows={2}
              className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30 resize-none"
            />
          </div>

          {/* 에러 메시지 */}
          {formError && (
            <p className="text-xs text-red-500 font-bold mb-3">{formError}</p>
          )}

          {/* 등록 버튼 */}
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="w-full py-3 bg-brand-primary text-white font-bold text-sm rounded-xl active:bg-brand-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            등록하기
          </button>
        </div>
      )}

      {/* ── 한줄평 리스트 ── */}
      {displayedReviews.length > 0 ? (
        <div className="space-y-3">
          {displayedReviews.map((review: ReviewData) => (
            <div
              key={review.id}
              className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-4"
            >
              {/* 상단: 닉네임 + 별점 */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-gray-900">{review.nickname}</span>
                  {review.child_age && (
                    <span className="text-[11px] text-gray-400 font-medium">({review.child_age})</span>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  <StarRating rating={review.rating} size={12} />
                  <span className="text-xs text-gray-400">{timeAgo(review.created_at)}</span>
                </div>
              </div>

              {/* 선택한 뱃지 */}
              {review.selected_badges && review.selected_badges.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {review.selected_badges.map((badge) => {
                    const badgeObj = findBadge(badge)
                    return (
                      <span
                        key={badge}
                        className="inline-flex items-center gap-0.5 px-2 py-0.5 bg-amber-50 text-amber-700 rounded-md text-[10px] font-bold"
                      >
                        {badgeObj?.emoji} {badgeObj?.label || badge}
                      </span>
                    )
                  })}
                </div>
              )}

              {/* 본문 */}
              {review.content && (
                <p className="text-sm text-gray-700 leading-relaxed font-medium">{review.content}</p>
              )}
            </div>
          ))}

          {/* 더보기 / 접기 */}
          {reviews.length > 3 && (
            <button
              onClick={() => setShowAllReviews(!showAllReviews)}
              className="w-full py-3 flex items-center justify-center gap-1 text-sm font-bold text-gray-500 active:text-gray-700 transition-colors"
            >
              {showAllReviews ? (
                <>접기 <ChevronUp className="w-4 h-4" /></>
              ) : (
                <>한줄평 {reviews.length - 3}개 더보기 <ChevronDown className="w-4 h-4" /></>
              )}
            </button>
          )}
        </div>
      ) : (
        !isLoading && reviewCount === 0 && !showWriteForm && (
          <div className="text-center py-8">
            <p className="text-sm text-gray-400 font-medium mb-1">아직 한줄평이 없어요</p>
            <p className="text-xs text-gray-300">첫 번째 후기의 주인공이 되어주세요!</p>
          </div>
        )
      )}
    </div>
  )
}
