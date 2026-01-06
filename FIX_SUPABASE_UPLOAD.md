# Fix: Jobs Not Appearing in Supabase

## Most Common Issue: RLS Policies

The workflow says "Successfully uploaded" but jobs don't appear. This is usually because **Row Level Security (RLS) is blocking the inserts**.

## Quick Fix: Update RLS Policies

### Step 1: Check Your Table Name

In Supabase Table Editor, what's your exact table name?
- Is it `pharmacist_jobs`? (script default)
- Or something else?

### Step 2: Fix RLS Policies

Go to Supabase SQL Editor and run this (replace `your_table_name` with your actual table name):

```sql
-- First, check current policies
SELECT * FROM pg_policies 
WHERE tablename = 'your_table_name';

-- Drop existing anon policy if it exists (optional)
DROP POLICY IF EXISTS "Allow anon insert/update" ON your_table_name;

-- Create new policy that allows anon role to insert
CREATE POLICY "Allow anon insert" ON your_table_name
    FOR INSERT 
    WITH CHECK (true);

-- Create policy that allows anon role to update
CREATE POLICY "Allow anon update" ON your_table_name
    FOR UPDATE 
    USING (true);

-- Verify policies
SELECT * FROM pg_policies 
WHERE tablename = 'your_table_name';
```

### Step 3: Test Again

1. Go to GitHub Actions
2. Run the workflow again
3. Check Supabase table

## Alternative: Disable RLS (Not Recommended for Production)

If you want to disable RLS temporarily for testing:

```sql
ALTER TABLE your_table_name DISABLE ROW LEVEL SECURITY;
```

**⚠️ Warning:** This removes all security. Only use for testing!

## Other Common Issues

### Issue 2: Wrong Table Name

**Check workflow logs:**
- Look for: `Table: pharmacist_jobs`
- Does it match your actual table name?

**If different, add GitHub Secret:**
- Name: `SUPABASE_TABLE_NAME`
- Value: Your actual table name

### Issue 3: Field Name Mismatch

**Check if your table uses different field names:**

```sql
-- See your table columns
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

**Compare with script fields:**
- Script sends: `job_url`, `company`, `title`, etc.
- If your table uses different names, add mapping:

**GitHub Secret:**
- Name: `SUPABASE_FIELD_MAPPING`
- Value: `{"job_url":"url","company":"company_name"}` (adjust as needed)

### Issue 4: Check Workflow Logs for Errors

In GitHub Actions:
1. Click on the workflow run
2. Expand "Run job scraper and upload to Supabase"
3. Look for:
   - ❌ "Error uploading to Supabase: ..."
   - Any red error messages
   - Check the exact error text

### Issue 5: Test Locally

Run locally to see exact error:

```bash
cd /Users/randy/Downloads/JobSpy-main
export SUPABASE_URL="https://wfzfjvuxophuhtrgznid.supabase.co"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_TABLE_NAME="your_table_name"  # if different
python search_pharmacist_jobs.py
```

Watch for error messages!

## Quick Diagnostic Query

Run this in Supabase SQL Editor to check everything:

```sql
-- 1. Check if table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%pharmacist%' OR table_name LIKE '%job%';

-- 2. Check RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'your_table_name';

-- 3. Check policies
SELECT policyname, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'your_table_name';

-- 4. Try manual insert (to test permissions)
INSERT INTO your_table_name (job_url, title, company, scraped_at)
VALUES ('https://test.com/job', 'Test Job', 'Test Company', NOW())
ON CONFLICT (job_url) DO NOTHING;
```

If the manual insert fails, it's an RLS/permissions issue.

## Most Likely Solution

**90% of the time, it's RLS policies.** Run the SQL from Step 2 above to fix it!

