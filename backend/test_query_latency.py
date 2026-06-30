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

def query_research_council_select(with_join=True, offset=0, limit=7):
    select_fields = 'id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, national_loan_count'
    if with_join:
        select_fields += ', library_info:book_library_info(library_name, callno)'
    return supabase.table('childbook_items')\
        .select(select_fields)\
        .eq('curation_tag', '어린이도서연구회')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('id')\
        .range(offset, offset + limit - 1)\
        .execute()

def query_books_by_age_select(age_values, with_join=True, offset=0, limit=7):
    select_fields = 'id, title, author, publisher, category, age, pangyo_callno, image_url, national_loan_count'
    if with_join:
        select_fields += ', library_info:book_library_info(library_name, callno)'
    return supabase.table('childbook_items')\
        .select(select_fields)\
        .in_('age', age_values)\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('id')\
        .range(offset, offset + limit - 1)\
        .execute()

def query_caldecott(with_join=True):
    select_fields = 'id, title, author, publisher, category, age, pangyo_callno, image_url, isbn, curation_tag'
    if with_join:
        select_fields += ', library_info:book_library_info(library_name, callno)'
    return supabase.table('childbook_items')\
        .select(select_fields)\
        .ilike('curation_tag', '%caldecott%')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('title', desc=False)\
        .execute()

def query_books_by_tag(tag, with_join=True, limit=7):
    select_fields = 'id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, curation_note, confidence_score, national_loan_count'
    if with_join:
        select_fields += ', library_info:book_library_info(library_name, callno)'
    return supabase.table('childbook_items')\
        .select(select_fields)\
        .ilike('curation_tag', f'%{tag}%')\
        .or_('is_hidden.is.null,is_hidden.eq.false')\
        .order('confidence_score', desc=True)\
        .limit(limit)\
        .execute()

async def main():
    print("=== Supabase Database Query Latency Test ===")
    
    age_values = ['5세부터', '7세부터', '유아']
    selected_tags = ['잠자리', '감정표현', '사회성']
    
    # 1. With Joins (Sequential)
    print("\n--- [WITH library_info JOIN] Sequential Execution ---")
    seq_start = time.perf_counter()
    await measure_query("RC Select (Join)", lambda: query_research_council_select(with_join=True, offset=5, limit=7))
    await measure_query("Age Select (Join)", lambda: query_books_by_age_select(age_values, with_join=True, offset=10, limit=7))
    await measure_query("Caldecott (Join)", lambda: query_caldecott(with_join=True))
    for tag in selected_tags:
        await measure_query(f"Tag [{tag}] (Join)", lambda t=tag: query_books_by_tag(t, with_join=True))
    seq_total = time.perf_counter() - seq_start
    print(f"Total time with join (sequential): {seq_total:.4f}s")
    
    # 2. Without Joins (Sequential)
    print("\n--- [WITHOUT library_info JOIN] Sequential Execution ---")
    seq_no_join_start = time.perf_counter()
    await measure_query("RC Select (No Join)", lambda: query_research_council_select(with_join=False, offset=5, limit=7))
    await measure_query("Age Select (No Join)", lambda: query_books_by_age_select(age_values, with_join=False, offset=10, limit=7))
    await measure_query("Caldecott (No Join)", lambda: query_caldecott(with_join=False))
    for tag in selected_tags:
        await measure_query(f"Tag [{tag}] (No Join)", lambda t=tag: query_books_by_tag(t, with_join=False))
    seq_no_join_total = time.perf_counter() - seq_no_join_start
    print(f"Total time without join (sequential): {seq_no_join_total:.4f}s")

    # 3. Parallel Comparison
    print("\n--- Parallel Comparison (Simulating Promise.all) ---")
    
    # Parallel WITH Joins
    par_join_start = time.perf_counter()
    tasks_join = [
        asyncio.create_task(measure_query("RC (Join)", lambda: query_research_council_select(with_join=True, offset=5, limit=7))),
        asyncio.create_task(measure_query("Age (Join)", lambda: query_books_by_age_select(age_values, with_join=True, offset=10, limit=7))),
        asyncio.create_task(measure_query("Caldecott (Join)", lambda: query_caldecott(with_join=True))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[0]}] (Join)", lambda: query_books_by_tag(selected_tags[0], with_join=True))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[1]}] (Join)", lambda: query_books_by_tag(selected_tags[1], with_join=True))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[2]}] (Join)", lambda: query_books_by_tag(selected_tags[2], with_join=True)))
    ]
    await asyncio.gather(*tasks_join)
    par_join_total = time.perf_counter() - par_join_start
    print(f"Parallel with join: {par_join_total:.4f}s")

    # Parallel WITHOUT Joins
    par_no_join_start = time.perf_counter()
    tasks_no_join = [
        asyncio.create_task(measure_query("RC (No Join)", lambda: query_research_council_select(with_join=False, offset=5, limit=7))),
        asyncio.create_task(measure_query("Age (No Join)", lambda: query_books_by_age_select(age_values, with_join=False, offset=10, limit=7))),
        asyncio.create_task(measure_query("Caldecott (No Join)", lambda: query_caldecott(with_join=False))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[0]}] (No Join)", lambda: query_books_by_tag(selected_tags[0], with_join=False))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[1]}] (No Join)", lambda: query_books_by_tag(selected_tags[1], with_join=False))),
        asyncio.create_task(measure_query(f"Tag [{selected_tags[2]}] (No Join)", lambda: query_books_by_tag(selected_tags[2], with_join=False)))
    ]
    await asyncio.gather(*tasks_no_join)
    par_no_join_total = time.perf_counter() - par_no_join_start
    print(f"Parallel without join: {par_no_join_total:.4f}s")
    
if __name__ == "__main__":
    asyncio.run(main())
