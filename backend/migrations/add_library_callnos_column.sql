-- Add library_callnos column specific libraries
-- Usage: Used to store call numbers for different libraries Key-Value pair
-- Format: {"library_name": "call_number"}
-- Example: {"판교도서관": "813.8-김12ㄱ", "분당도서관": "813.8-김12ㄴ"}

ALTER TABLE childbook_items 
ADD COLUMN IF NOT EXISTS library_callnos JSONB DEFAULT '{}'::jsonb;

-- Comment on column
COMMENT ON COLUMN childbook_items.library_callnos IS 'Library specific call numbers stored as JSON (e.g., {"판교도서관": "...", "분당도서관": "..."})';
