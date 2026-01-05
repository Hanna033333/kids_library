import HomeClient from "@/components/HomeClient";
import { getBooksFromSupabase } from "@/lib/supabase-client";

// Enable ISR (Incremental Static Regeneration)
// The page will be cached and regenerated every hour
export const revalidate = 3600; // 1 hour

export default async function Home() {
  // SSG: Fetch initial data at build time from Supabase directly
  // This avoids waking up the Render backend on first visit
  const initialData = await getBooksFromSupabase(1, 24);

  return <HomeClient initialData={initialData} />;
}
