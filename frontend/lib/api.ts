import type { Book, BooksResponse, LoanStatus } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function searchBooks(
  query?: string,
  age?: string,
  sort?: string,
  page: number = 1,
  limit: number = 20
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (query) params.append("q", query);
  if (age) params.append("age", age);
  if (sort) params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE_URL}/api/books/search?${params}`);
  if (!response.ok) {
    throw new Error("Failed to fetch books");
  }
  return response.json();
}

export async function getBooks(
  age?: string,
  sort?: string,
  page: number = 1,
  limit: number = 20
): Promise<BooksResponse> {
  const params = new URLSearchParams();
  if (age) params.append("age", age);
  if (sort) params.append("sort", sort);
  params.append("page", page.toString());
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE_URL}/api/books/list?${params}`);
  if (!response.ok) {
    throw new Error("Failed to fetch books");
  }
  return response.json();
}

export async function fetchLoanStatuses(
  bookIds: number[]
): Promise<Record<number, LoanStatus>> {
  const response = await fetch(`${API_BASE_URL}/api/books/loan-status`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bookIds),
  });
  
  if (!response.ok) {
    throw new Error("Failed to fetch loan statuses");
  }
  
  return response.json();
}

