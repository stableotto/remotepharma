# Debug: Jobs Not Appearing in Supabase

## Quick Checks

### 1. Check Table Name

The script defaults to `pharmacist_jobs`. Verify:

**In Supabase:**
- Go to Table Editor
- What is your exact table name? (case-sensitive)

**If different, add GitHub Secret:**
- Name: `SUPABASE_TABLE_NAME`
- Value: Your actual table name

### 2. Check RLS (Row Level Security) Policies

**In Supabase SQL Editor, run:**

```sql
-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'your_table_name';

-- Check existing policies
SELECT * FROM pg_policies 
WHERE tablename = 'your_table_name';
```

**If RLS is blocking inserts, create/update policy:**

```sql
-- Allow anon role to insert
CREATE POLICY "Allow anon insert" ON your_table_name
    FOR INSERT 
    WITH CHECK (true);

-- Allow anon role to update
CREATE POLICY "Allow anon update" ON your_table_name
    FOR UPDATE 
    USING (true);
```

### 3. Check Workflow Logs

In GitHub Actions, look for:
- ✅ "Successfully uploaded X jobs to Supabase" - means script thinks it worked
- ❌ Any error messages about Supabase
- Check the exact table name mentioned in logs

### 4. Test Directly in Supabase

**Try inserting a test row:**

```sql
INSERT INTO your_table_name (job_url, title, company, scraped_at)
VALUES ('https://test.com/job', 'Test Job', 'Test Company', NOW());
```

If this fails, it's an RLS/permissions issue.

### 5. Check Field Names

**Compare script fields with your table:**

Script sends these fields (see `SCHEMA_ALIGNMENT.md`):
- `id`, `site`, `job_url`, `title`, `company`, etc.

**Check your table columns:**

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

**If field names differ, add mapping:**

GitHub Secret:
- Name: `SUPABASE_FIELD_MAPPING`
- Value: `{"job_url":"url","company":"company_name"}` (adjust as needed)

### 6. Check Supabase Logs

**In Supabase Dashboard:**
- Go to Logs → API Logs
- Look for recent requests
- Check for 401/403 errors (permission issues)
- Check for 400 errors (bad request - field mismatch)

## Common Issues & Solutions

### Issue: RLS Blocking Inserts
**Solution:** Create insert policy (see #2 above)

### Issue: Wrong Table Name
**Solution:** Add `SUPABASE_TABLE_NAME` secret

### Issue: Field Name Mismatch
**Solution:** Add `SUPABASE_FIELD_MAPPING` secret

### Issue: Missing Required Fields
**Solution:** Check if your table has `job_url` as UNIQUE constraint
- Script uses `on_conflict="job_url"` for upserts
- If your table uses different field, update script or add mapping

## Quick Test

Run this locally to see exact error:

```bash
cd /Users/randy/Downloads/JobSpy-main
export SUPABASE_URL="https://wfzfjvuxophuhtrgznid.supabase.co"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_TABLE_NAME="your_table_name"  # if different
python search_pharmacist_jobs.py
```

Watch for error messages!

