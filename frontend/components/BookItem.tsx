import { Book, LoanStatus } from "@/lib/types";
import { ImageOff, Tags, BookOpen } from "lucide-react";
import Link from "next/link";

interface BookItemProps {
  book: Book;
  loanStatus?: LoanStatus;
  isLoanError?: boolean;
}

// Helper to normalize age strings to standard ranges
function normalizeAge(rawAge: string): string {
  if (!rawAge) return "";
  const age = rawAge.replace(/\s/g, ""); // Remove spaces

  // 특수 케이스: "8~13세"는 초등으로 분류
  if (age.includes("8~13세")) return "8~12세";

  // 높은 연령부터 체크하여 하위 연령 문자열 포함 문제 해결 (예: "13세"에 "3세"가 포함되는 문제)
  if (["청소년", "13세", "14세", "15세", "16세", "17세", "18세", "성인"].some(k => age.includes(k))) return "13세+";
  if (["초등", "8세", "9세", "10세", "11세", "12세"].some(k => age.includes(k))) return "8~12세";
  if (["유아", "유치", "4세", "5세", "6세", "7세"].some(k => age.includes(k))) return "4~7세";
  if (["영유아", "0세", "1세", "2세", "3세"].some(k => age.includes(k))) return "0~3세";

  return rawAge; // Return original if no match
}

import { sendGAEvent } from "@/lib/analytics";

export default function BookItem({ book, loanStatus, isLoanError }: BookItemProps) {
  const displayAge = normalizeAge(book.age || "");

  // Normalize loan status to show 4 states: 대출가능, 대출중, 미소장, 확인불가
  const normalizedStatus = (() => {
    // 1. 청구기호 없으면 무조건 '미소장'
    if (!book.pangyo_callno) {
      return { status: "미소장", available: null };
    }

    // 2. 대출 상태 정보가 있으면 표시
    if (loanStatus) {
      const status = loanStatus.status;
      // Map "시간초과" to "확인불가"
      if (status === "시간초과") {
        return { ...loanStatus, status: "확인불가", available: null };
      }
      // Map "정보없음" to "확인중" (API가 정보없음이면 재확인 필요 상태로 표시)
      if (status === "정보없음") {
        return { ...loanStatus, status: "확인중", available: null };
      }
      // 청구기호가 있는데 API가 "미소장"이라고 하는 경우 -> 데이터 불일치이므로 "확인중"으로 표시 (사용자 요청)
      if (status === "미소장") {
        return { ...loanStatus, status: "확인중", available: null };
      }
      return loanStatus;
    }

    // 3. 에러 발생 시 (그리고 데이터가 없을 때)
    if (isLoanError) {
      return { status: "확인중", available: null };
    }

    return undefined;
  })();

  return (
    <Link
      href={`/book/${book.id}`}
      prefetch={true}
      className="flex flex-col bg-white rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-md h-full group"
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url ? (
          <img
            src={book.image_url}
            alt={book.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextElementSibling?.classList.remove('hidden');
            }}
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
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight group-hover:text-gray-700 transition-colors">
          {book.title}
        </h3>

        <p className="text-[15px] font-extrabold text-[#F59E0B] tracking-tight mb-3 line-clamp-2 break-all">
          {book.pangyo_callno}
          {book.vol && `-${book.vol}`}
        </p>

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className="text-gray-400 truncate max-w-[50%]">{book.publisher}</span>
          {normalizedStatus && (
            <span className={`px-2 py-1 rounded-full text-[11px] font-bold leading-none text-center ${normalizedStatus.available === true
              ? "bg-green-100 text-green-700"
              : normalizedStatus.available === false
                ? "bg-red-100 text-red-700"
                : normalizedStatus.status === "미소장"
                  ? "bg-gray-100 text-gray-700"
                  : normalizedStatus.status === "확인중"
                    ? "bg-orange-50 text-orange-600 border border-orange-200"
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
