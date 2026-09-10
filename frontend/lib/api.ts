import type { Book, BooksResponse, LoanStatus, ReviewsResponse, MyReviewsResponse } from "./types";

const isLocal = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  : process.env.NODE_ENV === 'development';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (isLocal ? "http://127.0.0.1:8000" : "https://api.checkjari.com");

/** 외부 API 응답 지연 시 무한 대기를 막기 위한 공통 타임아웃 (project_plan 타임아웃 처리 원칙) */
const DEFAULT_TIMEOUT_MS = 30000;

interface ApiFetchOptions {
  method?: string;
  /** JSON 본문. 지정 시 Content-Type 헤더가 자동으로 붙는다. */
  body?: unknown;
  /** Supabase 액세스 토큰. 지정 시 Authorization 헤더가 자동으로 붙는다. */
  accessToken?: string;
  /** 실패 시 사용할 기본 에러 메시지 */
  errorMessage: string;
  /**
   * true면 응답 본문의 `detail` 필드를 우선 사용한다.
   * 리뷰 작성/수정/삭제는 이 메시지가 그대로 사용자에게 노출되므로(BookReviewSection) 반드시 유지한다.
   */
  useServerDetail?: boolean;
  /** 에러로 취급하지 않고 그대로 반환할 상태 코드 (예: 404를 null로 처리) */
  allowStatus?: number[];
  timeoutMs?: number;
}

/**
 * 백엔드 API 호출 공통 래퍼.
 * 타임아웃·헤더 구성·에러 변환을 한 곳에서 처리한다.
 */
async function apiFetch(path: string, options: ApiFetchOptions): Promise<Response> {
  const {
    method = "GET",
    body,
    accessToken,
    errorMessage,
    useServerDetail = false,
    allowStatus = [],
    timeoutMs = DEFAULT_TIMEOUT_MS,
  } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      ...(Object.keys(headers).length > 0 ? { headers } : {}),
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
      signal: controller.signal,
    });

    if (!response.ok && !allowStatus.includes(response.status)) {
      if (useServerDetail) {
        const errorData = await response.json().catch(() => ({} as { detail?: string }));
        throw new Error(errorData.detail || errorMessage);
      }
      throw new Error(errorMessage);
    }

    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function searchBooks(
  query?: string,
  age?: string,
  category?: string,
  sort?: string,
  page: number = 1,
  limit: number = 20,
  curation?: string,
  includeLibraryInfo: boolean = false
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (query) params.append("q", query);
  if (age) params.append("age", age);
  if (category && category !== "전체") params.append("category", category);
  if (sort) params.append("sort", sort);
  if (curation) params.append("curation", curation);
  params.append("page", page.toString());
  params.append("limit", limit.toString());
  params.append("include_library_info", includeLibraryInfo.toString());

  const response = await apiFetch(`/api/books/search?${params}`, {
    errorMessage: "Failed to fetch books",
  });
  return response.json();
}

export async function getBooks(
  age?: string,
  category?: string,
  sort?: string,
  page: number = 1,
  limit: number = 20,
  includeLibraryInfo: boolean = false
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (age) params.append("age", age);
  if (category && category !== "전체") params.append("category", category);
  if (sort) params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", limit.toString());
  params.append("include_library_info", includeLibraryInfo.toString());

  const response = await apiFetch(`/api/books/list?${params}`, {
    errorMessage: "Failed to fetch books",
  });
  return response.json();
}

export async function fetchLoanStatuses(
  bookIds: number[],
  libraryName?: string
): Promise<Record<number, LoanStatus>> {
  const response = await apiFetch("/api/books/loan-status", {
    method: "POST",
    body: {
      book_ids: bookIds,
      library_name: libraryName || "판교도서관",
    },
    errorMessage: "Failed to fetch loan statuses",
  });
  return response.json();
}

export async function getBooksByIds(bookIds: number[]): Promise<Book[]> {
  if (bookIds.length === 0) return [];
  const response = await apiFetch("/api/books/by-ids", {
    method: "POST",
    body: bookIds,
    errorMessage: "Failed to fetch books by ids",
  });
  return response.json();
}

export async function getBookById(id: number): Promise<Book | null> {
  const response = await apiFetch(`/api/books/${id}`, {
    errorMessage: "Failed to fetch book detail",
    allowStatus: [404],
  });
  if (response.status === 404) return null;
  return response.json();
}

export async function fetchBookReviews(bookId: number): Promise<ReviewsResponse> {
  const response = await apiFetch(`/api/books/${bookId}/reviews`, {
    errorMessage: "Failed to fetch reviews",
  });
  return response.json();
}

export async function createBookReview(
  bookId: number,
  review: {
    nickname: string;
    child_age?: string;
    rating: number;
    selected_badges: string[];
    content?: string;
  },
  accessToken: string
): Promise<void> {
  await apiFetch(`/api/books/${bookId}/reviews`, {
    method: "POST",
    body: review,
    accessToken,
    errorMessage: "Failed to create review",
    useServerDetail: true,
  });
}

export async function updateBookReview(
  bookId: number,
  reviewId: string,
  update: {
    child_age?: string;
    rating?: number;
    selected_badges?: string[];
    content?: string;
  },
  accessToken: string
): Promise<void> {
  await apiFetch(`/api/books/${bookId}/reviews/${reviewId}`, {
    method: "PATCH",
    body: update,
    accessToken,
    errorMessage: "Failed to update review",
    useServerDetail: true,
  });
}

export async function deleteBookReview(
  bookId: number,
  reviewId: string,
  accessToken: string
): Promise<void> {
  await apiFetch(`/api/books/${bookId}/reviews/${reviewId}`, {
    method: "DELETE",
    accessToken,
    errorMessage: "Failed to delete review",
    useServerDetail: true,
  });
}

export async function getMyRatedBooks(accessToken: string): Promise<MyReviewsResponse> {
  const response = await apiFetch("/api/books/my-reviews", {
    accessToken,
    errorMessage: "Failed to fetch rated books",
    useServerDetail: true,
  });
  return response.json();
}
