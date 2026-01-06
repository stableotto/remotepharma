# Schema Alignment Options

Since you already have a Supabase schema in another folder, here are your options:

## Option 1: Use Your Existing Schema (Recommended)

**Best if:** Your existing schema is close to what the script sends

### Steps:
1. **Check field names** - Compare your existing schema with the fields the script sends (see `SCHEMA_ALIGNMENT.md`)
2. **Update table name** - Set environment variable:
   ```bash
   export SUPABASE_TABLE_NAME="your_table_name"
   ```
   Or in GitHub Actions, add it as a secret.
3. **Map fields if needed** - If field names differ, use field mapping:

   **Option A:** Edit `search_pharmacist_jobs.py` and set `FIELD_MAPPING`:
   ```python
   FIELD_MAPPING = {
       "job_url": "url",  # If your table uses "url"
       "company": "company_name",  # If your table uses "company_name"
   }
   ```

   **Option B:** Set via environment variable (JSON):
   ```bash
   export SUPABASE_FIELD_MAPPING='{"job_url":"url","company":"company_name"}'
   ```

4. **Add missing columns** - If your schema is missing any fields, add them:
   ```sql
   ALTER TABLE your_table_name 
   ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
   ```

## Option 2: Use the New Schema

**Best if:** You want a separate table just for this scraper

### Steps:
1. Run the SQL from `supabase_schema.sql` in your Supabase SQL Editor
2. The script will automatically use `pharmacist_jobs` table
3. No field mapping needed

## Option 3: Hybrid Approach

**Best if:** You want to keep both schemas

1. Keep your existing schema for other purposes
2. Create a new table using `supabase_schema.sql`
3. Use `SUPABASE_TABLE_NAME` to point to the new table
4. Optionally sync data between tables using Supabase functions

## Quick Comparison

To see what fields your existing table has vs. what the script sends:

```sql
-- Run in Supabase SQL Editor
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

Then compare with the fields listed in `SCHEMA_ALIGNMENT.md`.

## Field Mapping Examples

### Example 1: Simple rename
```python
FIELD_MAPPING = {
    "job_url": "url",
    "date_posted": "posted_date"
}
```

### Example 2: Multiple renames
```python
FIELD_MAPPING = {
    "job_url": "url",
    "company": "company_name",
    "date_posted": "posted_date",
    "is_remote": "remote"
}
```

### Example 3: Via environment variable
```bash
# In GitHub Actions, add as secret:
SUPABASE_FIELD_MAPPING='{"job_url":"url","company":"company_name"}'
```

## Recommended Approach

1. **First, check your existing schema** - See what fields it has
2. **Compare with script fields** - Check `SCHEMA_ALIGNMENT.md` for the complete list
3. **Decide:**
   - If 80%+ match → Use Option 1 (field mapping)
   - If very different → Use Option 2 (new table)
   - If you need both → Use Option 3 (hybrid)

## Testing

After setting up field mapping, test locally:

```bash
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"
export SUPABASE_TABLE_NAME="your_table"  # if different
export SUPABASE_FIELD_MAPPING='{"job_url":"url"}'  # if needed
python search_pharmacist_jobs.py
```

Check the output to see if it uploads successfully!


