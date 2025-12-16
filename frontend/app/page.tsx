import HomeClient from "@/components/HomeClient";
import { BooksResponse } from "@/lib/types";

// Force dynamic rendering since we are fetching data
export const dynamic = "force-dynamic";

async function getInitialBooks(): Promise<BooksResponse> {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    console.log(`Fetching initial books from ${API_URL}...`);

    // Server-side fetch needs absolute URL
    // Also ensuring no-cache to get fresh data or handling revalidation
    const res = await fetch(`${API_URL}/api/books/list?page=1&limit=24&sort=pangyo_callno`, {
      cache: 'no-store', // Always fetch fresh data for now, or use revalidate
    });

    if (!res.ok) {
      console.error("Failed to fetch initial books:", res.status, res.statusText);
      // Return empty structure on failure to prevent crash
      return { data: [], total: 0, page: 1, limit: 10, total_pages: 0 };
    }

    return res.json();
  } catch (error) {
    console.error("Error fetching initial books:", error);
    return { data: [], total: 0, page: 1, limit: 10, total_pages: 0 };
  }
}

export default async function Home() {
  const initialData = await getInitialBooks();

  return <HomeClient initialData={initialData} />;
}
