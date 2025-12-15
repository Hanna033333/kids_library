/**
 * 공통 타입 정의
 */

export interface Book {
  id: number;
  title: string;
  author: string | null;
  publisher: string | null;
  isbn: string | null;
  pangyo_callno: string | null;
  age: string | null;
  category: string | null;
}

export interface BooksResponse {
  data: Book[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface SearchParams {
  q?: string;
  age?: string;
  sort?: string;
  page?: number;
  limit?: number;
}

