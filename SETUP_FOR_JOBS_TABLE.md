# Setup for Your `jobs` Table Schema

## ✅ Script Updated!

I've updated the script to work with your custom `jobs` table schema. Here's what to do:

## Step 1: Add GitHub Secrets

Go to: https://github.com/stableotto/remotepharma/settings/secrets/actions

### Secret 1: Table Name
- **Name:** `SUPABASE_TABLE_NAME`
- **Value:** `jobs`

### Secret 2: Field Mapping (Optional - script handles most automatically)
- **Name:** `SUPABASE_FIELD_MAPPING`
- **Value:** `{}` (empty - script handles mapping automatically)

## Step 2: Fix RLS Policies

Go to Supabase SQL Editor and run:

```sql
-- Allow anon role to insert
CREATE POLICY "Allow anon insert" ON jobs
    FOR INSERT 
    WITH CHECK (true);

-- Allow anon role to update
CREATE POLICY "Allow anon update" ON jobs
    FOR UPDATE 
    USING (true);
```

If policies exist, drop them first:
```sql
DROP POLICY IF EXISTS "Allow anon insert" ON jobs;
DROP POLICY IF EXISTS "Allow anon update" ON jobs;
DROP POLICY IF EXISTS "Allow anon insert/update" ON jobs;
```

## Step 3: Verify Upsert Key

The script will use `application_url` for upserts (to avoid duplicates).

**Make sure `application_url` is unique or has a unique constraint:**

```sql
-- Check if application_url is unique
SELECT application_url, COUNT(*) 
FROM jobs 
WHERE application_url IS NOT NULL
GROUP BY application_url 
HAVING COUNT(*) > 1;

-- If duplicates exist, you may want to add a unique constraint
-- (Only if you're sure application_url should be unique)
-- ALTER TABLE jobs ADD CONSTRAINT jobs_application_url_unique UNIQUE (application_url);
```

## Step 4: Test the Workflow

1. Go to GitHub Actions
2. Run the workflow
3. Check your `jobs` table

## What the Script Does Automatically

The script now:
- ✅ Maps `title` → `title`
- ✅ Maps `description` → `description`
- ✅ Maps `job_type` → `job_type` (normalizes "fulltime" → "full-time")
- ✅ Maps `min_amount` → `salary_min`
- ✅ Maps `max_amount` → `salary_max`
- ✅ Maps `interval` → `salary_type` (normalizes to "yearly", "monthly", "hourly")
- ✅ Maps `date_posted` → `posted_at`
- ✅ Maps `job_url` → `application_url`
- ✅ Generates `slug` from `title` automatically
- ✅ Sets `status` = "pending" for new jobs
- ✅ Uses `application_url` for upsert conflict (prevents duplicates)
- ✅ Removes fields that don't exist in your table

## Fields Not Mapped (Your table has these, script doesn't send)

- `company_id` - Will be NULL (you'd need to create companies separately)
- `requirements` - Not in script output
- `benefits` - Not in script output
- `experience_level` - Not in script output
- `schedule_flexibility` - Not in script output
- `application_email` - Not in script output
- `posted_by` - Will be NULL
- `approved_at` - Will be NULL (jobs start as "pending")
- `expires_at` - Will be NULL

These fields will remain NULL/empty. You can fill them manually or extend the script later.

## Important Notes

1. **Company Handling:** The script sends `company` (text) but your table uses `company_id` (UUID FK). For now, `company_id` will be NULL. You could:
   - Create a companies table lookup
   - Add a `company_name` text field to jobs table
   - Handle companies separately

2. **Upsert Key:** Uses `application_url` to prevent duplicate jobs. If a job with the same URL exists, it will update it.

3. **Status:** New jobs are set to `"pending"`. You'll need to approve them manually or add auto-approval logic.

## Test Query

After running the workflow, check:

```sql
-- See recent jobs
SELECT title, salary_min, salary_max, salary_type, status, posted_at, application_url
FROM jobs 
ORDER BY posted_at DESC 
LIMIT 10;

-- Count by status
SELECT status, COUNT(*) 
FROM jobs 
GROUP BY status;
```

## Next Steps

1. Add the GitHub secrets
2. Fix RLS policies
3. Run the workflow
4. Check your `jobs` table!

