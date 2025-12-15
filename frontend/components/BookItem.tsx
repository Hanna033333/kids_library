import { Book } from "@/lib/types";

interface BookItemProps {
  book: Book;
}

export default function BookItem({ book }: BookItemProps) {
  return (
    <div className="p-4 border-b border-border hover:bg-accent/50 transition-colors">
      {/* 책 제목 */}
      <h3 className="text-base font-semibold text-foreground mb-2">
        {book.title}
      </h3>

      {/* 책 정보 */}
      <div className="space-y-1">
        {book.author && (
          <p className="text-sm text-muted-foreground">저자: {book.author}</p>
        )}
        {book.publisher && (
          <p className="text-sm text-muted-foreground">출판사: {book.publisher}</p>
        )}
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
          {book.age && (
            <span className="text-xs text-muted-foreground font-medium">연령: {book.age}</span>
          )}
          {book.category && (
            <span className="text-xs text-muted-foreground font-medium">분류: {book.category}</span>
          )}
          {book.pangyo_callno && (
            <span className="text-xs text-muted-foreground font-medium">
              청구기호: {book.pangyo_callno}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

