import { Book } from "@/lib/types";
import { ImageOff } from "lucide-react";

interface BookItemProps {
  book: Book;
}

// Helper to normalize age strings to standard ranges
function normalizeAge(rawAge: string): string {
  if (!rawAge) return "";
  const age = rawAge.replace(/\s/g, ""); // Remove spaces

  if (["0~3세", "영유아", "3세"].some(k => age.includes(k))) return "0-3세";
  if (["4~7세", "5세", "6세", "7세", "유아"].some(k => age.includes(k))) return "4-7세";
  if (["8~13세", "8세", "9세", "10세", "11세", "12세", "13세", "초등"].some(k => age.includes(k))) return "8-12세";
  if (["청소년", "13세+", "14세"].some(k => age.includes(k))) return "13세+";

  return rawAge; // Return original if no match
}

export default function BookItem({ book }: BookItemProps) {
  const displayAge = normalizeAge(book.age || "");

  return (
    <div className="flex flex-col bg-white rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-md h-full group">
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
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/90 text-gray-600 font-bold shadow-sm backdrop-blur-sm">
              {book.category}
            </span>
          )}
          {displayAge && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-black/60 text-white font-medium shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
          {/* 대출 상태 뱃지 */}
          {book.loan_status && (
            <span 
              className={`text-[11px] px-2 py-0.5 rounded-full font-bold shadow-sm backdrop-blur-sm ${
                book.loan_status.available === true
                  ? 'bg-green-500 text-white'
                  : book.loan_status.available === false
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-300 text-gray-600'
              }`}
            >
              {book.loan_status.status}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col items-start bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        {book.pangyo_callno && (
          <p className="text-[15px] font-extrabold text-[#F59E0B] tracking-tight mb-3 truncate">
            {book.pangyo_callno}
          </p>
        )}

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs text-gray-400 font-medium">
          <span className="truncate max-w-[50%]">{book.author}</span>
          <span className="truncate max-w-[40%]">{book.publisher}</span>
        </div>
      </div>
    </div>
  );
}
