-- Check ALL check constraints on jobs table
-- Run this to see what values are allowed for each field

SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'jobs'::regclass
AND contype = 'c'
ORDER BY conname;

-- This will show you ALL check constraints and their allowed values
-- Example output might show:
-- jobs_job_type_check: CHECK (job_type = ANY (ARRAY['full-time'::text, 'part-time'::text, ...]))
-- jobs_salary_type_check: CHECK (salary_type = ANY (ARRAY['hourly'::text, 'yearly'::text]))

