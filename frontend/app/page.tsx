import HomeClient from "@/components/HomeClient";

// Enable ISR (Incremental Static Regeneration)
// The page will be cached and regenerated every hour
export const revalidate = 3600; // 1 hour

export default function Home() {
  // Temporarily disabled SSG due to build errors
  // Will re-enable after is_hidden column is confirmed in production DB
  return <HomeClient initialData={undefined} />;
}
