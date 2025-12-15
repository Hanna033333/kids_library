-- Performance Optimization: Add indexes for faster queries
-- Run this in Supabase Dashboard > SQL Editor

-- 1. Index for pangyo_callno sorting (with NULL filtering)
-- This speeds up the default sort order
CREATE INDEX IF NOT EXISTS idx_childbook_pangyo_callno 
ON childbook_items(pangyo_callno) 
WHERE pangyo_callno IS NOT NULL AND pangyo_callno != '없음';

-- 2. Index for title sorting
-- This speeds up sorting by title
CREATE INDEX IF NOT EXISTS idx_childbook_title 
ON childbook_items(title);

-- 3. Index for case-insensitive title search
-- This speeds up ILIKE queries on title
CREATE INDEX IF NOT EXISTS idx_childbook_title_lower 
ON childbook_items(LOWER(title));

-- 4. Index for case-insensitive author search
-- This speeds up ILIKE queries on author
CREATE INDEX IF NOT EXISTS idx_childbook_author_lower 
ON childbook_items(LOWER(author));

-- 5. Index for age filtering
-- This speeds up age-based filtering
CREATE INDEX IF NOT EXISTS idx_childbook_age 
ON childbook_items(age);

-- 6. Composite index for common query patterns
-- This speeds up queries that filter by pangyo_callno existence and sort
CREATE INDEX IF NOT EXISTS idx_childbook_pangyo_title 
ON childbook_items(pangyo_callno, title) 
WHERE pangyo_callno IS NOT NULL AND pangyo_callno != '없음';

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'childbook_items'
ORDER BY indexname;
