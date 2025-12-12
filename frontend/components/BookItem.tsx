import { Book } from "@/lib/api";

interface BookItemProps {
  book: Book;
}

export default function BookItem({ book }: BookItemProps) {
  return (
    <div className="p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors">
      {/* 책 제목 */}
      <h3 className="text-base font-semibold text-gray-900 mb-2">
        {book.title}
      </h3>
      
      {/* 책 정보 */}
      <div className="space-y-1">
        {book.author && (
          <p className="text-sm text-gray-600">저자: {book.author}</p>
        )}
        {book.publisher && (
          <p className="text-sm text-gray-600">출판사: {book.publisher}</p>
        )}
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
          {book.age && (
            <span className="text-xs text-blue-600">연령: {book.age}</span>
          )}
          {book.pangyo_callno && (
            <span className="text-xs text-gray-500 font-mono">
              청구기호: {book.pangyo_callno}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

