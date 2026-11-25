import { Book, LoanStatus } from "@/lib/types";
import { BookOpen, Heart } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useState, useEffect } from "react";
import { getAgeDisplayLabel } from "@/lib/utils/age";
import { useLibrary } from "@/context/LibraryContext";
import { sendGAEvent } from "@/lib/analytics";
import { getOptimizedImageUrl } from "@/lib/utils/image";
import { useAuth } from "@/context/AuthContext";
import { parseCurationTags, formatCurationTag, isGradeTag } from "@/lib/utils/curation-filter";

interface BookItemProps {
  book: Book;
  loanStatus?: LoanStatus;
  /** true이면 대출 가능 상태 배지를 표시 (목록/검색 페이지), false면 깔끔 모드 (홈/추천 카드) */
  showLibraryInfo?: boolean;
  /** true이면 next/image priority 활성화 (첫 뷰포트 LCP 최적화용) */
  priority?: boolean;
  /** 섹션 타이틀과 중복되는 태그를 카드에서 제외 (예: 잠자리 섹션이면 '#잠자리' 제거) */
  excludeTag?: string;
  /** 도서 찜 여부 (목록 카드에서 하트 표시용) */
  isSaved?: boolean;
  /** 도서 찜 토글 핸들러 (제공 시 표지 우상단에 하트 버튼 노출) */
  onToggleSave?: (book: Book, e: React.MouseEvent) => void;
}

export default function BookItem({ book, loanStatus, showLibraryInfo = false, priority = false, excludeTag, isSaved = false, onToggleSave }: BookItemProps) {
  const { user } = useAuth();
  const { selectedLibrary } = useLibrary();
  const initialCoverUrl = getOptimizedImageUrl(book.image_url, 'list');
  const [imgSrc, setImgSrc] = useState<string>(initialCoverUrl);
  const [imgError, setImgError] = useState(!initialCoverUrl);

  // book.id 또는 image_url 변경 시 이미지 에러 상태 및 src 리셋 (SPA 이동/재사용 시 이미지 증발 방지)
  useEffect(() => {
    const nextUrl = getOptimizedImageUrl(book.image_url, 'list');
    setImgSrc(nextUrl);
    setImgError(!nextUrl);
  }, [book.id, book.image_url]);

  const handleImageError = () => {
    // 1단계: cover200 실패 시 원본 image_url로 폴백
    const fallback = book.image_url?.trim() || '';
    if (fallback && imgSrc !== fallback) {
      setImgSrc(fallback);
    } else {
      // 2단계: 원본도 실패 시 플레이스홀더 표시
      setImgError(true);
    }
  };

  // 1. 이미지 위 메타 뱃지 (구체적인 학년 태그가 있으면 학년으로, 없으면 연령 라벨)
  const rawCurationTags = parseCurationTags(book.curation_tag);
  const gradeTag = rawCurationTags.find((t) => isGradeTag(t));
  const displayBadge = gradeTag ? formatCurationTag(gradeTag) : getAgeDisplayLabel(book.age);

  // 선호 도서관 소장 여부 판별 (showLibraryInfo이고 선호 도서관이 설정되었을 때만 연산 — book_library_info 단일 테이블 기준)
  const hasHolding = (() => {
    if (!showLibraryInfo || !selectedLibrary) return false;
    const info = book.library_info?.find(
      (l) => l.library_name === selectedLibrary || l.library_name.includes(selectedLibrary)
    );
    return Boolean(info && info.callno && info.callno !== '없음');
  })();

  // Normalize loan status (showLibraryInfo 및 selectedLibrary 존재 시에만 사용)
  const normalizedStatus = (() => {
    if (!showLibraryInfo || !selectedLibrary) return null;

    if (!hasHolding) {
      return { status: "미소장", available: null };
    }

    if (loanStatus) {
      const status = loanStatus.status;
      if (status === "시간초과" || status === "확인불가" || status === "확인중") {
        return { ...loanStatus, status: "확인중", available: null };
      }
      if (status === "정보없음" || status === "미소장") {
        return { ...loanStatus, status: "미소장", available: null };
      }
      return loanStatus;
    }
    return { status: "확인중", available: null };
  })();

  // curation_tag 추출 (최대 2개) — 상단 뱃지로 노출된 학년 태그 및 excludeTag 제외
  const nonGradeTags = rawCurationTags.filter((t) => !isGradeTag(t));
  const tags = excludeTag
    ? nonGradeTags.filter((t) => t !== excludeTag).slice(0, 2)
    : nonGradeTags.slice(0, 2);

  return (
    <Link
      href={`/book/${book.id}`}
      prefetch={true}
      className="flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transition-all h-full group active:scale-[0.98]"
      onClick={() => sendGAEvent('click_book_item', { book_id: book.id, book_title: book.title })}
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {imgSrc && !imgError ? (
          <Image
            key={`${book.id}-${imgSrc}`}
            src={imgSrc}
            alt={book.title}
            fill
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform duration-300 group-active:scale-105"
            loading={priority ? 'eager' : 'lazy'}
            priority={priority}
            onError={handleImageError}
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-300">
            <BookOpen className="w-12 h-12 opacity-20" />
          </div>
        )}

        {/* 태그 (이미지 위에 오버레이 — 학년 우선, 없으면 연령 단독 노출) */}
        <div className="absolute top-2.5 left-2.5 sm:top-3 sm:left-3 flex gap-1.5 flex-wrap">
          {displayBadge && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-black/65 text-white font-bold shadow-sm backdrop-blur-sm">
              {displayBadge}
            </span>
          )}
        </div>

        {/* 찜하기(장바구니) 하트 버튼 (우측 상단 오버레이) */}
        {onToggleSave && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggleSave(book, e);
            }}
            aria-label={isSaved ? "내 책장에서 빼기" : "내 책장에 담기"}
            className="absolute top-2.5 right-2.5 z-10 w-10 h-10 rounded-full bg-white/90 backdrop-blur-xs shadow-sm flex items-center justify-center active:scale-95 transition-transform outline-none focus:outline-none"
          >
            <Heart
              className={`w-5 h-5 transition-colors ${isSaved ? "fill-[#F59E0B] text-[#F59E0B]" : "text-gray-400"
                }`}
            />
          </button>
        )}
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-3 sm:p-4 flex flex-col justify-between bg-white">
        <h3 className="text-[15px] sm:text-base font-bold text-gray-900 leading-[1.35] sm:leading-[1.4] line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        {/* 바닥 영역: 큐레이션 태그(좌) + 대출 가능 상태 배지(우) */}
        {(tags.length > 0 || (showLibraryInfo && user && selectedLibrary && normalizedStatus && normalizedStatus.status !== "확인중")) && (
          <div className={`mt-auto pt-2.5 sm:pt-3 flex items-center gap-2 w-full ${tags.length > 0 ? "justify-between" : "justify-start"}`}>
            {/* 태그 (공간이 좁으면 자연스럽게 2줄로 줄바꿈) */}
            {tags.length > 0 && (
              <div className="flex items-center gap-x-1.5 gap-y-0.5 sm:gap-x-2 text-[12.5px] sm:text-[13px] font-medium text-gray-500 flex-wrap flex-1 min-w-0 leading-[1.35]">
                {tags.map((tag, idx) => (
                  <span key={idx} className="text-gray-500">
                    #{formatCurationTag(tag)}
                  </span>
                ))}
              </div>
            )}

            {/* 대출 가능 상태 배지 (선호 도서관 설정 시에만 노출 — 청구기호는 도서 상세에서 제공) */}
            {showLibraryInfo && user && selectedLibrary && normalizedStatus && normalizedStatus.status !== "확인중" && (
              <span className={`shrink-0 inline-flex items-center justify-center px-2.5 py-1 rounded-full text-xs font-bold leading-none text-center ${normalizedStatus.available === true
                ? "bg-[#ECFDF5] text-[#059669] border border-emerald-200"
                : normalizedStatus.available === false
                  ? "bg-red-50 text-red-600 border border-red-200"
                  : normalizedStatus.status === "미소장"
                    ? "bg-[#F3F4F6] text-[#6B7280]"
                    : "bg-white text-gray-600 border border-gray-300"
                }`}>
                {normalizedStatus.status}
              </span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}
