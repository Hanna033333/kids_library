import { Book, LoanStatus } from "@/lib/types";
import { ImageOff, Tags, BookOpen } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { getAgeDisplayLabel } from "@/lib/utils/age";
import { useLibrary } from "@/context/LibraryContext";

interface BookItemProps {
  book: Book;
  loanStatus?: LoanStatus;
}

import { sendGAEvent } from "@/lib/analytics";
import { getOptimizedImageUrl } from "@/lib/utils/image";
import { useAuth } from "@/context/AuthContext";

export default function BookItem({ book, loanStatus }: BookItemProps) {
  const { user } = useAuth();
  const { selectedLibrary } = useLibrary();
  const displayAge = getAgeDisplayLabel(book.age);

  // 청구기호 결정 로직
  let displayCallNo = '청구기호 없음';
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

  // Normalize loan status to show 4 states: 대출가능, 대출중, 미소장, 확인불가
  const normalizedStatus = (() => {
    // 1. 청구기호가 없거나 보유 정보가 없는 경우 무조건 '미소장' 처리 (상세페이지 정책과 일치)
    if (!displayCallNo || displayCallNo === '청구기호 없음' || displayCallNo === '보유 정보 없음') {
      return { status: "미소장", available: null };
    }

    if (loanStatus) {
      const status = loanStatus.status;
      // Map "시간초과" to "확인불가"
      if (status === "시간초과") {
        return { ...loanStatus, status: "확인불가", available: null };
      }
      // Map "정보없음" to "확인중"
      if (status === "정보없음") {
        return { ...loanStatus, status: "확인중", available: null };
      }
      // Map "미소장" to "확인중" (청구기호가 존재하는데 API가 미소장이라고 반환한 경우)
      if (status === "미소장") {
        return { ...loanStatus, status: "확인중", available: null };
      }
      return loanStatus;
    }
    // API 조회 완료 전에는 기본적으로 '확인중' 노출
    return { status: "확인중", available: null };
  })();

  return (
    <Link
      href={`/book/${book.id}`}
      prefetch={true}
      className="flex flex-col bg-white rounded-lg border border-gray-100 overflow-hidden transition-all h-full group"
      onClick={() => sendGAEvent('click_book_item', { book_id: book.id, book_title: book.title })}
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url ? (
          <Image
            src={getOptimizedImageUrl(book.image_url, 'list')}
            alt={book.title}
            fill
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : null}

        {/* Fallback for No Image */}
        <div className={`flex flex-col items-center justify-center w-full h-full text-gray-300 ${book.image_url ? 'hidden' : ''}`}>
          <BookOpen className="w-12 h-12 opacity-20" />
        </div>

        {/* 태그 (이미지 위에 오버레이) */}
        <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
          {book.category && (
            <span className="text-[11px] px-3 py-1.5 rounded-full bg-white/90 text-gray-600 font-bold shadow-sm backdrop-blur-sm flex items-center gap-1">
              {book.category}
            </span>
          )}
          {displayAge && (
            <span className="text-[11px] px-3 py-1.5 rounded-full bg-black/60 text-white font-medium shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col items-start bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        {user && (
          <p className="text-[15px] font-extrabold text-[#F59E0B] tracking-tight mb-3 line-clamp-2 break-all">
            {displayCallNo}
            {book.vol && `-${book.vol}`}
          </p>
        )}

        {/*
        {book.national_loan_count ? (
          <div className="flex items-center gap-1 text-[11px] text-gray-500 font-semibold mb-2 bg-gray-50 px-2.5 py-1 rounded">
            <span>📊 전국 도서관 대출 {book.national_loan_count >= 1000 ? `${(book.national_loan_count / 1000).toFixed(1)}k` : book.national_loan_count.toLocaleString()}회</span>
          </div>
        ) : null}
        */}

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className={`text-gray-400 truncate ${user && normalizedStatus ? 'max-w-[50%]' : 'max-w-full'}`}>{book.publisher}</span>
          {user && normalizedStatus && (
            <span className={`px-2 py-1 rounded-full text-[11px] font-bold leading-none text-center ${normalizedStatus.available === true
              ? "bg-green-100 text-green-700"
              : normalizedStatus.available === false
                ? "bg-red-100 text-red-700"
                : normalizedStatus.status === "미소장"
                  ? "bg-gray-100 text-gray-700"
                  : normalizedStatus.status === "확인중"
                    ? "bg-orange-100 text-orange-700"
                    : "bg-white text-gray-600 border border-gray-300"
              }`}>
              {normalizedStatus.status}
            </span>
          )}

        </div>
      </div>
    </Link>
  );
}
