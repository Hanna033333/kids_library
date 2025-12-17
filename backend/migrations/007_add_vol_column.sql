-- Add vol (volume) column to childbook_items table
BEGIN;

-- Add vol column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'childbook_items' AND column_name = 'vol'
    ) THEN
        ALTER TABLE childbook_items ADD COLUMN vol TEXT;
        RAISE NOTICE 'Added vol column to childbook_items';
    ELSE
        RAISE NOTICE 'vol column already exists';
    END IF;
END $$;

-- Create index on vol for faster searches
CREATE INDEX IF NOT EXISTS idx_childbook_items_vol ON childbook_items(vol);

COMMIT;
