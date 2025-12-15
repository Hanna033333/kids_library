/**
 * 페이지네이션 컴포넌트
 */
"use client";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  loading = false,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7; // 최대 표시할 페이지 번호 개수

    if (totalPages <= maxVisible) {
      // 전체 페이지가 적으면 모두 표시
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // 많으면 생략 표시 추가
      if (currentPage <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push("...");
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1);
        pages.push("...");
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push("...");
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push("...");
        pages.push(totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="px-4 py-6 bg-background border-t border-border">
      <div className="flex justify-center items-center gap-2 flex-wrap">
        {/* 이전 페이지 버튼 */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1 || loading}
          className="px-3 py-2 text-sm font-medium border border-input text-foreground bg-background rounded-md hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          이전
        </button>

        {/* 페이지 번호 */}
        {getPageNumbers().map((pageNum, index) => {
          if (pageNum === "...") {
            return (
              <span key={`ellipsis-${index}`} className="px-2 text-muted-foreground">
                ...
              </span>
            );
          }
          return (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum as number)}
              disabled={currentPage === pageNum}
              className={`px-3 py-2 text-sm font-medium border rounded-md transition-colors ${currentPage === pageNum
                ? "bg-primary text-primary-foreground border-primary cursor-default"
                : "border-input text-foreground bg-background hover:bg-accent active:bg-accent"
                } ${loading && currentPage !== pageNum ? "pointer-events-none" : ""}`}
            >
              {pageNum}
            </button>
          );
        })}

        {/* 다음 페이지 버튼 */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || loading}
          className="px-3 py-2 text-sm font-medium border border-input text-foreground bg-background rounded-md hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          다음
        </button>
      </div>
    </div>
  );
}

