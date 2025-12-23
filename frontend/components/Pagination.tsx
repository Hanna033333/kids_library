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
    <div className="px-4 py-8 flex justify-center">
      <div className="flex items-center gap-1">
        {/* 이전 페이지 버튼 */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1 || loading}
          className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          이전
        </button>

        {/* 페이지 번호 */}
        <div className="flex items-center gap-1 mx-1">
          {getPageNumbers().map((pageNum, index) => {
            if (pageNum === "...") {
              return (
                <span key={`ellipsis-${index}`} className="w-8 flex justify-center text-gray-300 text-xs">
                  ...
                </span>
              );
            }
            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum as number)}
                disabled={currentPage === pageNum}
                className={`min-w-[32px] h-8 px-1 flex items-center justify-center text-sm font-bold rounded-lg transition-all ${currentPage === pageNum
                  ? "bg-[#F59E0B] text-white shadow-md shadow-gray-200"
                  : "text-gray-500 hover:bg-gray-100 hover:text-gray-900"
                  } ${loading && currentPage !== pageNum ? "pointer-events-none" : ""}`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        {/* 다음 페이지 버튼 */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || loading}
          className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          다음
        </button>
      </div>
    </div>
  );
}






