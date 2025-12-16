-- Add image_url column to childbook_items
ALTER TABLE childbook_items ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Create index for faster checking of items without images
CREATE INDEX IF NOT EXISTS idx_childbook_image_url_null 
ON childbook_items(id) 
WHERE image_url IS NULL;
