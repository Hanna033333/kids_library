// Supabase 직접 조회 성능 테스트
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

async function testSupabasePerformance() {
    console.time('Supabase Direct');

    const { data, count } = await supabase
        .from('childbook_items')
        .select('*', { count: 'exact' })
        .range(0, 23)
        .order('pangyo_callno');

    console.timeEnd('Supabase Direct');
    console.log('Books fetched:', data?.length);
    console.log('Total count:', count);
}

async function testBackendAPI() {
    console.time('Backend API');

    const response = await fetch('https://kids-library-7gj8.onrender.com/api/books/list?page=1&limit=24');
    const result = await response.json();

    console.timeEnd('Backend API');
    console.log('Books fetched:', result.data?.length);
    console.log('Total count:', result.total);
}

// 실행
console.log('=== Performance Comparison ===\n');
await testSupabasePerformance();
console.log('');
await testBackendAPI();
