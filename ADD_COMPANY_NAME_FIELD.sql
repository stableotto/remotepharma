-- Add company_name field to jobs table to store company names
-- Run this in Supabase SQL Editor if your jobs table doesn't have company_name

-- Check if company_name column already exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'jobs' 
AND column_name = 'company_name';

-- If it doesn't exist, add it:
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS company_name TEXT;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name);

-- Verify it was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'jobs' 
AND column_name IN ('company_name', 'company_id')
ORDER BY column_name;

