import type { Book, BooksResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

