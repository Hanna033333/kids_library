import HomeClient from "@/components/HomeClient";
import { BooksResponse } from "@/lib/types";

// Enable ISR (Incremental Static Regeneration)
// The shell will be cached and served instantly
export const revalidate = 3600; // 1 hour

export default function Home() {
  // Pass undefined as initialData to trigger CSR immediately
  return <HomeClient initialData={undefined} />;
}
