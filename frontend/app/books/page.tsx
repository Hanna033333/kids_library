import HomeClient from "@/components/HomeClient";

// Force dynamic rendering to avoid build-time data fetching errors
export const dynamic = 'force-dynamic';

export default function BooksPage() {
    // Using CSR (Client-Side Rendering) until is_hidden column is stable
    return <HomeClient initialData={undefined} />;
}
