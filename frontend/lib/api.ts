import type { Book, BooksResponse, LoanStatus, NationalLibrary, ReviewsResponse, MyReviewsResponse } from "./types";

const isLocal = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  : process.env.NODE_ENV === 'development';

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || (isLocal ? "http://127.0.0.1:8000" : "https://api.checkjari.com");
// macOS에서 localhost가 IPv6(::1)로 먼저 해석되어 IPv4 전용 로컬 백엔드(127.0.0.1:8000) 연결 지연이 발생하는 현상 방지
const API_BASE_URL = rawApiUrl.replace("://localhost:", "://127.0.0.1:");

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
        const errorData = await response.json().catch(() => ({} as { detail?: unknown }));
        const serverDetail = typeof errorData.detail === "string" && errorData.detail.trim()
          ? errorData.detail
          : null;
        throw new Error(serverDetail || errorMessage);
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
  includeLibraryInfo: boolean = false,
  tag?: string,
  library?: string
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (query) params.append("q", query);
  if (age) params.append("age", age);
  if (category && category !== "전체") params.append("category", category);
  if (sort) params.append("sort", sort);
  if (curation) params.append("curation", curation);
  if (tag) params.append("tag", tag);
  if (library) params.append("library", library);
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

const MAX_BATCH_BOOK_IDS = 50;
const BATCH_CONCURRENCY = 3;

function dedupeAndChunkIds(bookIds: number[], chunkSize: number = MAX_BATCH_BOOK_IDS): number[][] {
  const uniqueIds = Array.from(new Set(bookIds.filter((id) => Number.isFinite(id))));
  const chunks: number[][] = [];
  for (let i = 0; i < uniqueIds.length; i += chunkSize) {
    chunks.push(uniqueIds.slice(i, i + chunkSize));
  }
  return chunks;
}

async function mapWithConcurrency<T, R>(
  items: T[],
  concurrency: number,
  worker: (item: T) => Promise<R>
): Promise<R[]> {
  if (items.length === 0) return [];
  const results: R[] = new Array(items.length);
  let nextIndex = 0;

  const runWorker = async () => {
    while (nextIndex < items.length) {
      const currentIndex = nextIndex++;
      results[currentIndex] = await worker(items[currentIndex]);
    }
  };

  const workerCount = Math.min(concurrency, items.length);
  await Promise.all(Array.from({ length: workerCount }, () => runWorker()));
  return results;
}

export async function fetchLibraries(params: {
  q?: string;
  region?: string;
  lat?: number;
  lng?: number;
  limit?: number;
}): Promise<{ libraries: NationalLibrary[]; total: number }> {
  const search = new URLSearchParams();
  if (params.q && params.q.trim()) search.append("q", params.q.trim());
  if (params.region && params.region !== "전체") search.append("region", params.region);
  if (params.lat !== undefined && params.lng !== undefined) {
    search.append("lat", params.lat.toString());
    search.append("lng", params.lng.toString());
  }
  search.append("limit", (params.limit ?? 30).toString());

  const response = await apiFetch(`/api/libraries?${search.toString()}`, {
    errorMessage: "도서관 목록을 불러오지 못했습니다.",
    timeoutMs: 10000,
  });
  return response.json();
}

export async function fetchLoanStatuses(
  bookIds: number[],
  libraryName?: string,
  options?: { libCode?: string | null; includeCallno?: boolean }
): Promise<Record<number, LoanStatus>> {
  const chunks = dedupeAndChunkIds(bookIds);
  if (chunks.length === 0) return {};

  const targetLibrary = libraryName || "판교도서관";
  const chunkResults = await mapWithConcurrency(
    chunks,
    BATCH_CONCURRENCY,
    async (chunk) => {
      const response = await apiFetch("/api/books/loan-status", {
        method: "POST",
        body: {
          book_ids: chunk,
          library_name: targetLibrary,
          ...(options?.libCode ? { lib_code: options.libCode } : {}),
          ...(options?.includeCallno ? { include_callno: true } : {}),
        },
        errorMessage: "Failed to fetch loan statuses",
      });
      return response.json() as Promise<Record<number, LoanStatus>>;
    }
  );

  return Object.assign({}, ...chunkResults);
}

export async function getBooksByIds(bookIds: number[]): Promise<Book[]> {
  const chunks = dedupeAndChunkIds(bookIds);
  if (chunks.length === 0) return [];

  const chunkResults = await mapWithConcurrency(
    chunks,
    BATCH_CONCURRENCY,
    async (chunk) => {
      const response = await apiFetch("/api/books/by-ids", {
        method: "POST",
        body: chunk,
        errorMessage: "Failed to fetch books by ids",
      });
      return response.json() as Promise<Book[]>;
    }
  );

  const bookMap = new Map<number, Book>();
  for (const books of chunkResults) {
    for (const book of books) {
      bookMap.set(book.id, book);
    }
  }

  const seen = new Set<number>();
  const orderedBooks: Book[] = [];
  for (const id of bookIds) {
    if (seen.has(id)) continue;
    seen.add(id);
    const book = bookMap.get(id);
    if (book) orderedBooks.push(book);
  }
  return orderedBooks;
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
