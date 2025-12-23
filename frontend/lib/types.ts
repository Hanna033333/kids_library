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
  vol: string | null;
  age: string | null;
  category: string | null;
  image_url: string | null;
  description: string | null;
  save_count?: number;
  loan_status?: LoanStatus | null;
}

export interface LoanStatus {
  available: boolean | null;
  status: string;
  updated_at?: string;
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

