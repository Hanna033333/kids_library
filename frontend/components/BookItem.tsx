import { Book, LoanStatus } from "@/lib/types";
import { BookOpen } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { getAgeDisplayLabel } from "@/lib/utils/age";
import { useLibrary } from "@/context/LibraryContext";
import { sendGAEvent } from "@/lib/analytics";
import { getOptimizedImageUrl } from "@/lib/utils/image";
import { useAuth } from "@/context/AuthContext";
import { parseCurationTags } from "@/lib/utils/curation-filter";

interface BookItemProps {
  book: Book;
  loanStatus?: LoanStatus;
  /** true이면 청구기호·대출 상태를 표시 (목록/검색 페이지), false면 깔끔 모드 (홈/추천 카드) */
  showLibraryInfo?: boolean;
  /** true이면 next/image priority 활성화 (첫 뷰포트 LCP 최적화용) */
  priority?: boolean;
  /** 섹션 타이틀과 중복되는 태그를 카드에서 제외 (예: 잠자리 섹션이면 '#잠자리' 제거) */
  excludeTag?: string;
}

export default function BookItem({ book, loanStatus, showLibraryInfo = false, priority = false, excludeTag }: BookItemProps) {
  const { user } = useAuth();
  const { selectedLibrary } = useLibrary();
  const displayAge = getAgeDisplayLabel(book.age);
  const [imgError, setImgError] = useState(false);

  // 청구기호 결정 로직 (showLibraryInfo이고 선호 도서관이 설정되었을 때만 연산)
  let displayCallNo = '청구기호 없음';
  if (showLibraryInfo && selectedLibrary) {
    if (selectedLibrary === '판교도서관') {
      if (book.pangyo_callno && book.pangyo_callno !== '없음') {
        displayCallNo = book.pangyo_callno;
      } else {
        const info = book.library_info?.find(l => l.library_name.includes('판교'));
        if (info) displayCallNo = info.callno;
      }
    } else {
      const info = book.library_info?.find(l => l.library_name === selectedLibrary || l.library_name.includes(selectedLibrary));
      if (info) {
        displayCallNo = info.callno;
      } else {
        displayCallNo = '보유 정보 없음';
      }
    }
  }

  // Normalize loan status (showLibraryInfo 및 selectedLibrary 존재 시에만 사용)
  const normalizedStatus = (() => {
    if (!showLibraryInfo || !selectedLibrary) return null;

    if (!displayCallNo || displayCallNo === '청구기호 없음' || displayCallNo === '보유 정보 없음') {
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

  // curation_tag 추출 (최대 2개) — SSOT: parseCurationTags 사용
  const rawTags = parseCurationTags(book.curation_tag, 3);
  const tags = excludeTag
    ? rawTags.filter((t) => t !== excludeTag).slice(0, 2)
    : rawTags.slice(0, 2);

  return (
    <Link
      href={`/book/${book.id}`}
      prefetch={true}
      className="flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transition-all h-full group active:scale-[0.98]"
      onClick={() => sendGAEvent('click_book_item', { book_id: book.id, book_title: book.title })}
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url && !imgError ? (
          <Image
            src={getOptimizedImageUrl(book.image_url, 'list')}
            alt={book.title}
            fill
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform duration-300 group-active:scale-105"
            loading={priority ? 'eager' : 'lazy'}
            priority={priority}
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-300">
            <BookOpen className="w-12 h-12 opacity-20" />
          </div>
        )}

        {/* 태그 (이미지 위에 오버레이 — 연령 단독 노출) */}
        <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
          {displayAge && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-black/65 text-white font-bold shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col justify-between bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.4] line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        {/* 바닥 영역 (여유 있는 mt-auto pt-3) */}
        <div className="mt-auto pt-3 flex flex-col gap-2.5 w-full">
          {/* 태그 (박스 테두리 제거로 깔끔하고 여유로운 텍스트 톤) */}
          {tags.length > 0 && (
            <div className="flex items-center gap-2 text-[13px] font-medium text-gray-500 flex-wrap">
              {tags.map((tag, idx) => (
                <span key={idx} className="text-gray-500">
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* 청구기호 & 대출 가능 상태 배지 (선호 도서관 설정 시에만 노출) */}
          {showLibraryInfo && user && selectedLibrary && (
            <div className="flex items-center justify-between gap-2 pt-0.5">
              <p className="text-[14px] font-extrabold text-[#F59E0B] tracking-tight truncate flex-1 min-w-0">
                {displayCallNo}
                {book.vol && `-${book.vol}`}
              </p>
              {normalizedStatus && normalizedStatus.status !== "확인중" && (
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
      </div>
    </Link>
  );
}
