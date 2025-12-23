import { Book } from "@/lib/types";
import { ImageOff, Tags } from "lucide-react";
import Link from "next/link";

interface BookItemProps {
  book: Book;
}

// Helper to normalize age strings to standard ranges
function normalizeAge(rawAge: string): string {
  if (!rawAge) return "";
  const age = rawAge.replace(/\s/g, ""); // Remove spaces

  // 특수 케이스: "8~13세"는 초등으로 분류
  if (age.includes("8~13세")) return "8-12세";

  // 높은 연령부터 체크하여 하위 연령 문자열 포함 문제 해결 (예: "13세"에 "3세"가 포함되는 문제)
  if (["청소년", "13세", "14세", "15세", "16세", "17세", "18세", "성인"].some(k => age.includes(k))) return "13세+";
  if (["초등", "8세", "9세", "10세", "11세", "12세"].some(k => age.includes(k))) return "8-12세";
  if (["유아", "유치", "4세", "5세", "6세", "7세"].some(k => age.includes(k))) return "4-7세";
  if (["영유아", "0세", "1세", "2세", "3세"].some(k => age.includes(k))) return "0-3세";

  return rawAge; // Return original if no match
}

export default function BookItem({ book }: BookItemProps) {
  const displayAge = normalizeAge(book.age || "");

  return (
    <Link
      href={`/book/${book.id}`}
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
          <ImageOff className="w-8 h-8 mb-2 opacity-40" />
          <span className="text-[10px] uppercase tracking-wider font-medium opacity-60">No Image</span>
        </div>

        {/* 태그 (이미지 위에 오버레이) */}
        <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
          {book.category && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/90 text-gray-600 font-bold shadow-sm backdrop-blur-sm flex items-center gap-1">
              {book.category}
            </span>
          )}
          {displayAge && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-black/60 text-white font-medium shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col items-start bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight group-hover:text-blue-600 transition-colors">
          {book.title}
        </h3>

        <p className="text-[15px] font-extrabold text-[#F59E0B] tracking-tight mb-3 truncate">
          {book.pangyo_callno}
          {book.vol && `-${book.vol}`}
        </p>

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className="text-gray-400 truncate max-w-[60%]">{book.publisher}</span>
          {book.loan_status && (
            <span className={`px-2 py-1 rounded-full text-[11px] font-bold leading-none text-center ${book.loan_status.available === true
              ? "bg-green-100 text-green-700"
              : book.loan_status.available === false
                ? "bg-red-100 text-red-700"
                : "bg-gray-100 text-gray-500"
              }`}>
              {book.loan_status.status}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
