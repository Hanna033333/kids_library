-- Add curation_tag column to childbook_items
ALTER TABLE childbook_items 
ADD COLUMN IF NOT EXISTS curation_tag TEXT;

-- Add comment
COMMENT ON COLUMN childbook_items.curation_tag IS 'Curation source tag (e.g. 어린이도서연구회)';
