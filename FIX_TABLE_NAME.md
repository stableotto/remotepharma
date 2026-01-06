# Fix: Table Name is `jobs` (not `pharmacist_jobs`)

## Your Table: `public.jobs`

The script defaults to `pharmacist_jobs`, but your table is `jobs`.

## Solution: Add GitHub Secret

### Step 1: Add Table Name Secret

1. Go to: https://github.com/stableotto/remotepharma/settings/secrets/actions
2. Click **"New repository secret"**
3. Add:
   - **Name:** `SUPABASE_TABLE_NAME`
   - **Value:** `jobs`
4. Click **"Add secret"**

### Step 2: Fix RLS Policies for `jobs` Table

Go to Supabase SQL Editor and run:

```sql
-- Allow anon role to insert into jobs table
CREATE POLICY "Allow anon insert" ON jobs
    FOR INSERT 
    WITH CHECK (true);

-- Allow anon role to update jobs table
CREATE POLICY "Allow anon update" ON jobs
    FOR UPDATE 
    USING (true);
```

If policies already exist, drop them first:

```sql
DROP POLICY IF EXISTS "Allow anon insert" ON jobs;
DROP POLICY IF EXISTS "Allow anon update" ON jobs;
DROP POLICY IF EXISTS "Allow anon insert/update" ON jobs;

-- Then create new ones
CREATE POLICY "Allow anon insert" ON jobs
    FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow anon update" ON jobs
    FOR UPDATE 
    USING (true);
```

### Step 3: Verify Your Table Schema

Make sure your `jobs` table has the required fields. Check:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'jobs'
ORDER BY ordinal_position;
```

**Required fields the script sends:**
- `job_url` (must be UNIQUE for upsert to work)
- `id`, `site`, `title`, `company`, `location`, `date_posted`, etc.
- `scraped_at` (timestamp)

**If field names differ, add mapping:**

GitHub Secret:
- Name: `SUPABASE_FIELD_MAPPING`
- Value: `{"job_url":"url","company":"company_name"}` (adjust based on your schema)

### Step 4: Test Again

1. Go to GitHub Actions
2. Run the workflow again
3. Check your `jobs` table in Supabase

## Quick Checklist

- [ ] Added `SUPABASE_TABLE_NAME` secret = `jobs`
- [ ] Created RLS policies for `jobs` table
- [ ] Verified `job_url` field exists and is UNIQUE
- [ ] Ran workflow again
- [ ] Checked `jobs` table for new data

## Verify It's Working

After running the workflow, check:

```sql
-- Count total jobs
SELECT COUNT(*) FROM jobs;

-- See recent jobs
SELECT title, company, job_url, scraped_at 
FROM jobs 
ORDER BY scraped_at DESC 
LIMIT 10;
```

