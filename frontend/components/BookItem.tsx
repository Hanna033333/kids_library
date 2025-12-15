import { Book } from "@/lib/types";

interface BookItemProps {
  book: Book;
}

export default function BookItem({ book }: BookItemProps) {
  return (
    <div className="p-5 border-b border-border bg-card/50 hover:bg-accent/30 transition-colors">
      {/* 1. 상단 태그 (분류, 연령) */}
      <div className="flex gap-2 mb-2">
        {book.category && (
          <span className="text-[11px] px-1.5 py-0.5 rounded-sm bg-muted text-muted-foreground font-medium">
            {book.category}
          </span>
        )}
        {book.age && (
          <span className="text-[11px] px-1.5 py-0.5 rounded-sm bg-muted text-muted-foreground font-medium">
            {book.age}
          </span>
        )}
      </div>

      {/* 2. 메인 정보 (제목, 청구기호) */}
      <div className="mb-3">
        <h3 className="text-xl font-bold text-foreground leading-tight mb-1">
          {book.title}
        </h3>
        {book.pangyo_callno && (
          <p className="text-lg font-bold text-primary-foreground tracking-tight">
            {book.pangyo_callno}
          </p>
        )}
      </div>

      {/* 3. 하단 메타 정보 (저자, 출판사) */}
      <div className="flex items-center text-sm text-muted-foreground gap-2">
        <span className="truncate max-w-[150px]">{book.author}</span>
        <span className="w-px h-3 bg-border"></span>
        <span className="truncate">{book.publisher}</span>
      </div>
    </div>
  );
}

