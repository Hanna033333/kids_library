-- Add web_scraped_callno column to childbook_items table
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql

ALTER TABLE childbook_items 
ADD COLUMN IF NOT EXISTS web_scraped_callno TEXT;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'childbook_items' 
AND column_name = 'web_scraped_callno';
