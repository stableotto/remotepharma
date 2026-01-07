-- Check what values are allowed for salary_type in your jobs table
-- Run this in Supabase SQL Editor to see the constraint

SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'jobs'::regclass
AND contype = 'c'
AND conname LIKE '%salary_type%';

-- Alternative: Check the table definition
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'jobs'
AND column_name = 'salary_type';

-- If you see a CHECK constraint, it will show the allowed values
-- Example output might show: CHECK (salary_type IN ('yearly', 'monthly', 'hourly'))
-- Or: CHECK (salary_type = ANY (ARRAY['yearly'::text, 'monthly'::text, 'hourly'::text]))

