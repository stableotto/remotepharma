# Debug: Jobs Still Not Appearing

Let's debug this step by step.

## Step 1: Check GitHub Actions Logs

1. Go to: https://github.com/stableotto/remotepharma/actions
2. Click on the most recent workflow run
3. Click on "scrape-and-upload" job
4. Look for these messages:

**What to look for:**
- ✅ "Successfully uploaded X jobs to Supabase" - means script thinks it worked
- ❌ "Error uploading to Supabase:" - shows the actual error
- 📤 "Uploading X jobs to Supabase..." - shows it's trying
- Check the "Sample job keys" to see what fields are being sent

**Copy and share any error messages you see!**

## Step 2: Check Supabase Logs

1. Go to: https://supabase.com/dashboard/project/wfzfjvuxophuhtrgznid/logs/explorer
2. Filter by:
   - **Table:** `jobs`
   - **Time:** Last hour
3. Look for:
   - INSERT operations
   - Any error messages
   - 401/403 errors (permission issues)

## Step 3: Verify RLS Policies

Run this in Supabase SQL Editor:

```sql
-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'jobs';

-- Check existing policies
SELECT policyname, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'jobs';

-- Check if anon role can insert
SELECT has_table_privilege('anon', 'jobs', 'INSERT');
SELECT has_table_privilege('anon', 'jobs', 'UPDATE');
```

**If RLS is enabled but no insert policy exists, that's the problem!**

## Step 4: Test RLS Policies

Try inserting manually in Supabase SQL Editor:

```sql
-- This should work if RLS is configured correctly
INSERT INTO jobs (title, slug, description, status, posted_at, application_url)
VALUES (
    'Test Job',
    'test-job',
    'Test description',
    'pending',
    NOW(),
    'https://test.com/job'
)
ON CONFLICT (application_url) DO NOTHING;
```

**If this fails, RLS is blocking inserts!**

## Step 5: Check Table Structure

Verify your table has the required fields:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'jobs'
ORDER BY ordinal_position;
```

**Required fields for upsert:**
- `application_url` (or `slug`) - for conflict resolution
- `title`
- `description`
- `status`
- `posted_at`

## Step 6: Check for Unique Constraint

The script uses `application_url` for upsert. Check if it's unique:

```sql
-- Check if application_url has unique constraint
SELECT 
    constraint_name, 
    constraint_type
FROM information_schema.table_constraints 
WHERE table_name = 'jobs' 
AND constraint_type = 'UNIQUE';

-- Or check for unique index
SELECT indexname, indexdef
FROM pg_indexes 
WHERE tablename = 'jobs' 
AND indexdef LIKE '%application_url%';
```

**If `application_url` isn't unique, upsert might fail silently!**

## Step 7: Test Locally

Run the script locally to see exact errors:

```bash
cd /Users/randy/Downloads/JobSpy-main
export SUPABASE_URL="https://wfzfjvuxophuhtrgznid.supabase.co"
export SUPABASE_KEY="your-anon-key-here"
export SUPABASE_TABLE_NAME="jobs"
python search_pharmacist_jobs.py
```

**Watch for error messages!**

## Common Issues & Fixes

### Issue 1: RLS Blocking Inserts
**Fix:**
```sql
CREATE POLICY "Allow anon insert" ON jobs
    FOR INSERT 
    WITH CHECK (true);
```

### Issue 2: application_url Not Unique
**Fix:**
```sql
-- Make application_url unique
ALTER TABLE jobs 
ADD CONSTRAINT jobs_application_url_unique 
UNIQUE (application_url);
```

### Issue 3: Missing Required Fields
**Fix:** Check if your table has all required fields (see Step 5)

### Issue 4: Field Type Mismatch
**Fix:** Check if field types match (e.g., `salary_min` should be `int4`, not `text`)

## Quick Diagnostic Query

Run this to see everything:

```sql
-- 1. Check table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'jobs'
);

-- 2. Check RLS
SELECT rowsecurity FROM pg_tables WHERE tablename = 'jobs';

-- 3. Check policies
SELECT COUNT(*) as policy_count FROM pg_policies WHERE tablename = 'jobs';

-- 4. Check permissions
SELECT 
    has_table_privilege('anon', 'jobs', 'SELECT') as can_select,
    has_table_privilege('anon', 'jobs', 'INSERT') as can_insert,
    has_table_privilege('anon', 'jobs', 'UPDATE') as can_update;

-- 5. Check recent inserts
SELECT COUNT(*) as total_jobs, 
       MAX(posted_at) as latest_job,
       COUNT(*) FILTER (WHERE status = 'pending') as pending_jobs
FROM jobs;
```

## What to Share

Please share:
1. **GitHub Actions logs** - especially any error messages
2. **Results of Step 3** (RLS policies check)
3. **Results of Step 4** (manual insert test)
4. **Results of Step 6** (unique constraint check)

This will help identify the exact issue!

