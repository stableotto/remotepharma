-- Add unique constraint on application_url to prevent duplicate jobs
-- Run this in Supabase SQL Editor

-- First, check if there are any duplicate application_urls
SELECT application_url, COUNT(*) as count
FROM jobs
WHERE application_url IS NOT NULL
GROUP BY application_url
HAVING COUNT(*) > 1;

-- If duplicates exist, you may want to clean them up first:
-- DELETE FROM jobs j1
-- USING jobs j2
-- WHERE j1.application_url = j2.application_url
--   AND j1.id < j2.id;

-- Add unique constraint (will fail if duplicates exist)
ALTER TABLE jobs
ADD CONSTRAINT jobs_application_url_unique UNIQUE (application_url);

-- Verify constraint was added
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'jobs'::regclass
AND conname = 'jobs_application_url_unique';

