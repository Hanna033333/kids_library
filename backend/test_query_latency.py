import time
import asyncio
from supabase_client import supabase

async def measure_query(name, query_func):
    start = time.perf_counter()
    try:
        res = await asyncio.to_thread(query_func)
        latency = time.perf_counter() - start
        count = len(res.data) if hasattr(res, 'data') and res.data else 0
        if hasattr(res, 'count') and res.count is not None:
            count = res.count
        print(f"[{name}] Completed in {latency:.4f}s - {count} rows")
        return latency, count
    except Exception as e:
        latency = time.perf_counter() - start
        print(f"[{name}] FAILED in {latency:.4f}s - Error: {e}")
        return latency, None

def query_research_council_count():
    return supabase.table('childbook_items')\
        .select('id', count='exact')\
        .eq('curation_tag', '어린이도서연구회')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .execute()

def query_research_council_select(offset=0, limit=7):
    # book_library_info 조인 포함
    return supabase.table('childbook_items')\
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, national_loan_count, library_info:book_library_info(library_name, callno)')\
        .eq('curation_tag', '어린이도서연구회')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('id')\
        .range(offset, offset + limit - 1)\
        .execute()

def query_books_by_age_count(age_values):
    return supabase.table('childbook_items')\
        .select('id', count='exact')\
        .in_('age', age_values)\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .execute()

def query_books_by_age_select(age_values, offset=0, limit=7):
    # book_library_info 조인 포함
    return supabase.table('childbook_items')\
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, national_loan_count, library_info:book_library_info(library_name, callno)')\
        .in_('age', age_values)\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('id')\
        .range(offset, offset + limit - 1)\
        .execute()

def query_caldecott():
    # book_library_info 조인 포함
    return supabase.table('childbook_items')\
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, isbn, curation_tag, library_info:book_library_info(library_name, callno)')\
        .ilike('curation_tag', '%caldecott%')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('title', desc=False)\
        .execute()

def query_books_by_tag(tag, limit=7):
    # book_library_info 조인 포함
    return supabase.table('childbook_items')\
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, curation_note, confidence_score, national_loan_count, library_info:book_library_info(library_name, callno)')\
        .ilike('curation_tag', f'%{tag}%')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('confidence_score', desc=True)\
        .limit(limit)\
        .execute()

async def main():
    print("=== Supabase Database Query Latency Test ===")
    
    # 4-7세 연령값들
    age_values = ['5세부터', '7세부터', '유아']
    
    # 임의의 dynamic 큐레이션 태그 3개
    selected_tags = ['잠자리', '감정표현', '사회성']
    
    # 1. 개별 동기식 실행 측정
    print("\n--- Running queries sequentially (Synchronous) ---")
    seq_start = time.perf_counter()
    
    # Research Council (Count + Select)
    await measure_query("Research Council Count", query_research_council_count)
    await measure_query("Research Council Select", lambda: query_research_council_select(offset=5, limit=7))
    
    # Books by Age (Count + Select)
    await measure_query("Books by Age Count", lambda: query_books_by_age_count(age_values))
    await measure_query("Books by Age Select", lambda: query_books_by_age_select(age_values, offset=10, limit=7))
    
    # Caldecott
    await measure_query("Caldecott Books Select", query_caldecott)
    
    # Dynamic Tags
    for tag in selected_tags:
        await measure_query(f"Books by Tag [{tag}]", lambda t=tag: query_books_by_tag(t))
        
    seq_total = time.perf_counter() - seq_start
    print(f"Total sequential execution time: {seq_total:.4f}s")
    
    # 2. 병렬식 실행 측정 (Next.js Promise.all과 모사)
    print("\n--- Running queries in parallel (Simulating Next.js Promise.all) ---")
    par_start = time.perf_counter()
    
    tasks = [
        # Count와 Select를 같이 실행하는 것 대신, home-api logic을 최대한 따라갑니다.
        # 실제 HomePage의 Promise.all에서는 getResearchCouncilBooks, getBooksByAge, getCaldecottBooks, getBooksByTag가 병렬로 실행됩니다.
        # 하지만 getResearchCouncilBooks와 getBooksByAge 내부에서는 Count를 한 뒤 Select를 하므로,
        # 이 두 함수는 각각 내부에서 await count를 한 뒤 await select를 합니다. 즉, count와 select는 직렬로 수행되고,
        # 각각의 함수들은 서로 병렬로 수행됩니다.
        
        # Helper task for Research Council
        asyncio.create_task(measure_query("Research Council Full (Sequential within task)", lambda: (
            query_research_council_count(),
            query_research_council_select(offset=5, limit=7)
        ))),
        # Helper task for Age Books
        asyncio.create_task(measure_query("Books by Age Full (Sequential within task)", lambda: (
            query_books_by_age_count(age_values),
            query_books_by_age_select(age_values, offset=10, limit=7)
        ))),
        # Caldecott
        asyncio.create_task(measure_query("Caldecott", query_caldecott)),
        # Dynamic Tags
        asyncio.create_task(measure_query(f"Tag [{selected_tags[0]}]", lambda: query_books_by_tag(selected_tags[0]))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[1]}]", lambda: query_books_by_tag(selected_tags[1]))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[2]}]", lambda: query_books_by_tag(selected_tags[2])))
    ]
    
    await asyncio.gather(*tasks)
    par_total = time.perf_counter() - par_start
    print(f"Total parallel execution time: {par_total:.4f}s")
    
if __name__ == "__main__":
    asyncio.run(main())
