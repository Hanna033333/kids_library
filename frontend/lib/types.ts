/**
 * 공통 타입 정의
 */

export interface LibraryInfo {
  library_name: string;
  callno: string;
}

export interface Book {
  id: number;
  title: string;
  author: string | null;
  publisher: string | null;
  isbn: string | null;
  pangyo_callno: string | null;
  web_scraped_callno?: string | null;
  library_info?: LibraryInfo[];
  vol: string | null;
  age: string | null;
  category: string | null;
  image_url: string | null;
  description: string | null;
  save_count?: number;
  national_loan_count?: number | null;
  loan_status?: LoanStatus | null;
  curation_tag?: string | null;
  curation_note?: string | null;
  confidence_score?: number | null;
  page_count?: number | null;
  text_level?: string | null;
  preview_urls?: string[] | null;
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
  author?: string;
  sort?: string;
  page?: number;
  limit?: number;
}

export interface ReviewData {
  id: string;
  book_id: number;
  nickname: string;
  child_age: string | null;
  rating: number;
  selected_badges: string[];
  content: string | null;
  is_ai_generated: boolean;
  created_at: string;
  user_id: string | null;
}

export interface RatedBook extends Book {
  review_id: string;
  rating: number;
  created_at: string;
}

export interface MyReviewsResponse {
  rated_books: RatedBook[];
}

export interface ReviewsResponse {
  avg_rating: number | null;
  review_count: number;
  badge_counts: Record<string, number>;
  reviews: ReviewData[];
}

