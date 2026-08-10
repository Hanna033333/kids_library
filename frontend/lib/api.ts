import type { Book, BooksResponse, LoanStatus, ReviewsResponse } from "./types";

if (process.env.NODE_ENV === 'production' && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("FAIL-FAST: NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다. 빌드 또는 배포 설정을 확인하세요.");
}
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/books/search?${params}`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (!response.ok) {
      throw new Error("Failed to fetch books");
    }
    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
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

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/books/list?${params}`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (!response.ok) {
      throw new Error("Failed to fetch books");
    }
    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

export async function fetchLoanStatuses(
  bookIds: number[],
  libraryName?: string
): Promise<Record<number, LoanStatus>> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

  try {
    const response = await fetch(`${API_BASE_URL}/api/books/loan-status`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        book_ids: bookIds,
        library_name: libraryName || "판교도서관"
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error("Failed to fetch loan statuses");
    }

    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

export async function getBooksByIds(bookIds: number[]): Promise<Book[]> {
  if (bookIds.length === 0) return [];
  const response = await fetch(`${API_BASE_URL}/api/books/by-ids`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bookIds),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch books by ids");
  }

  return response.json();
}

export async function getBookById(id: number): Promise<Book | null> {
  const response = await fetch(`${API_BASE_URL}/api/books/${id}`);
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error("Failed to fetch book detail");
  }
  return response.json();
}

export async function fetchBookReviews(bookId: number): Promise<ReviewsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/books/${bookId}/reviews`);
  if (!response.ok) {
    throw new Error("Failed to fetch reviews");
  }
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
  }
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/books/${bookId}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(review),
  });
  if (!response.ok) {
    throw new Error("Failed to create review");
  }
}
