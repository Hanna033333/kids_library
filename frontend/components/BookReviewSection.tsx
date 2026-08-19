'use client'

import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchBookReviews, createBookReview } from '@/lib/api'
import { BADGES, BADGE_CATEGORIES, findBadge } from '@/lib/badge_constants'
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
// 메인 컴포넌트
// ─────────────────────────────────────────────────
export default function BookReviewSection({ bookId, bookTitle }: BookReviewSectionProps) {
  // 리뷰 및 별점 기능 미완성으로 인한 UI 가림 처리
  return null;

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
    '책자리부모님'
  ).replace(/\s+/g, '')

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
    setShowWriteForm(false)
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

    setIsSubmitting(true)
    setFormError('')

    try {
      await createBookReview(bookId, {
        nickname: effectiveNickname,
        child_age: childAge.trim() || undefined,
        rating,
        selected_badges: selectedBadges,
        content: content.trim() || undefined,
      })

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

      // 쿼리 갱신 & 폼 닫기
      queryClient.invalidateQueries({ queryKey: ['book-reviews', bookId] })
      resetForm()
    } catch (err) {
      console.error('Failed to submit review:', err)
      setFormError('리뷰 등록 중 오류가 발생했습니다. 다시 시도해 주세요.')
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
              {sortedBadgeCounts.slice(0, 6).map(([badge, count]) => {
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

      {/* ── 리뷰 작성 버튼 ── */}
      {!showWriteForm && (
        <button
          onClick={() => setShowWriteForm(true)}
          className="w-full py-3.5 bg-brand-primary/5 text-brand-primary font-bold text-sm rounded-xl border border-brand-primary/10 active:bg-brand-primary/10 active:scale-[0.99] transition-all mb-5"
        >
          리뷰 남기기
        </button>
      )}

      {/* ── 리뷰 작성 폼 ── */}
      {showWriteForm && (
        <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] border border-gray-100 p-5 mb-5 animate-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between mb-5">
            <h4 className="text-base font-black text-gray-900">리뷰 작성</h4>
            <button onClick={resetForm} className="p-1 text-gray-400 active:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* 1. 책에 만족하셨나요? (별점) */}
          <div className="bg-gray-50/80 rounded-2xl p-4 mb-4 border border-gray-100/80">
            <div className="flex items-center gap-2 mb-2">
              <h4 className="text-sm font-extrabold text-gray-900">책에 만족하셨나요?</h4>
              <span className="px-1.5 py-0.5 text-[10px] font-extrabold text-white bg-gray-900 rounded-md">필수</span>
            </div>
            <div className="flex justify-center py-2">
              <StarInput value={rating} onChange={setRating} />
            </div>
          </div>

          {/* 2. 어떤 점이 좋았나요? (2단 카드 레이아웃) */}
          <div className="bg-gray-50/80 rounded-2xl p-4 mb-4 border border-gray-100/80">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-extrabold text-gray-900">어떤 점이 좋았나요?</h4>
              <span className="px-1.5 py-0.5 text-[10px] font-extrabold text-white bg-gray-900 rounded-md">필수</span>
            </div>
            <p className="text-xs font-semibold text-gray-400 mb-4">
              이 책에 어울리는 키워드를 골라주세요. (1개~5개)
            </p>

            {/* 좌우 2단 병렬 카테고리 카드 */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              {BADGE_CATEGORIES.map((cat) => {
                const catBadges = BADGES.filter((b) => b.category === cat)
                return (
                  <div key={cat} className="bg-white rounded-2xl p-3 border border-gray-100 shadow-xs flex flex-col justify-between">
                    <div>
                      <h5 className="text-xs font-black text-gray-800 mb-3 px-0.5 flex items-center justify-between">
                        <span>{cat}</span>
                      </h5>
                      <div className="flex flex-col gap-2">
                        {catBadges.map((badge) => {
                          const isSelected = selectedBadges.includes(badge.full)
                          return (
                            <button
                              key={badge.full}
                              type="button"
                              onClick={() => handleBadgeToggle(badge.full)}
                              className={`w-full flex items-center justify-start gap-1.5 px-2.5 py-2.5 rounded-2xl text-[11px] sm:text-xs font-bold border transition-all active:scale-[0.97] text-left leading-tight ${
                                isSelected
                                  ? 'bg-amber-50 text-amber-900 border-amber-300 shadow-xs ring-1 ring-amber-400/30 font-extrabold'
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
            <p className="text-xs font-bold text-gray-500 mb-1.5">리뷰 내용 (선택)</p>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="이 책에 대한 솔직한 후기를 남겨주세요 ☺️"
              maxLength={500}
              rows={2}
              className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30 resize-none"
            />
          </div>

          {/* 아이 나이 */}
          <div className="mb-4">
            <p className="text-xs font-bold text-gray-500 mb-1.5">아이 나이 (선택)</p>
            <div className="relative">
              <select
                value={childAge}
                onChange={(e) => setChildAge(e.target.value)}
                className={`w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium appearance-none focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/30 cursor-pointer ${
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
            className="w-full py-3 bg-brand-primary text-white font-bold text-sm rounded-xl active:bg-brand-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            등록하기
          </button>
        </div>
      )}

      {/* ── 리뷰 리스트 ── */}
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
                <>리뷰 {reviews.length - 3}개 더보기 <ChevronDown className="w-4 h-4" /></>
              )}
            </button>
          )}
        </div>
      ) : (
        !isLoading && reviewCount === 0 && !showWriteForm && (
          <div className="text-center py-8">
            <p className="text-sm text-gray-400 font-medium mb-1">아직 작성된 리뷰가 없어요</p>
            <p className="text-xs text-gray-300">첫 번째 후기의 주인공이 되어주세요!</p>
          </div>
        )
      )}
    </div>
  )
}
