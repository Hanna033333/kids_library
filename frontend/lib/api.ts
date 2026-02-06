import type { Book, BooksResponse, LoanStatus } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function searchBooks(
  query?: string,
  age?: string,
  category?: string,
  sort?: string,
  page: number = 1,
  limit: number = 20
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (query) params.append("q", query);
  if (age) params.append("age", age);
  if (category && category !== "전체") params.append("category", category);
  if (sort) params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", limit.toString());

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
  limit: number = 20
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (age) params.append("age", age);
  if (category && category !== "전체") params.append("category", category);
  if (sort) params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", limit.toString());

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
  libCode?: string
): Promise<Record<number, LoanStatus>> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30초 타임아웃

  try {
    const response = await fetch(`${API_BASE_URL}/api/books/loan-status`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ book_ids: bookIds, lib_code: libCode }),
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

