# Custom Field Mapping for Your `jobs` Table

## Your Schema vs Script Output

Your `jobs` table has a different structure than what the script sends. We need to map the fields.

## Field Mapping

Add this as a GitHub Secret:

**Name:** `SUPABASE_FIELD_MAPPING`

**Value:**
```json
{
  "title": "title",
  "description": "description",
  "job_type": "job_type",
  "min_amount": "salary_min",
  "max_amount": "salary_max",
  "interval": "salary_type",
  "job_url": "application_url",
  "is_remote": "is_featured"
}
```

## Important Notes

### 1. No Direct Company Field
Your table uses `company_id` (UUID, FK to `companies` table), but the script sends `company` (text).

**Options:**
- **Option A:** Create companies first, then link (complex)
- **Option B:** Store company name in a different field (if you have one)
- **Option C:** Ignore company for now, focus on other fields

### 2. Upsert Conflict Key
The script uses `job_url` for upserts, but your table doesn't have that. We can:
- Use `application_url` as the conflict key (if unique)
- Or use `slug` if that's unique
- Or modify the script to use a different field

### 3. Missing Fields
Your table has fields the script doesn't send:
- `slug` - needs to be generated from title
- `company_id` - needs to be looked up or created
- `status` - probably should be `pending` or `approved`
- `posted_at` - can use `date_posted` from script
- `requirements`, `benefits` - not in script output

### 4. Fields to Map
- `title` → `title` ✅
- `description` → `description` ✅
- `job_type` → `job_type` ✅ (may need to normalize: "fulltime" → "full-time")
- `min_amount` → `salary_min` ✅
- `max_amount` → `salary_max` ✅
- `interval` → `salary_type` ✅ (may need to normalize: "yearly" → "yearly")
- `job_url` → `application_url` ✅
- `date_posted` → `posted_at` ✅
- `is_remote` → could map to `is_featured` or ignore

## Recommended Approach

### Step 1: Update Script for Your Schema

We need to modify the script to:
1. Generate `slug` from title
2. Handle `company_id` (lookup or create company)
3. Set default values for missing fields
4. Use `application_url` or `slug` for upsert conflict

### Step 2: Add Field Mapping Secret

Add to GitHub Secrets:
- `SUPABASE_TABLE_NAME` = `jobs`
- `SUPABASE_FIELD_MAPPING` = (see JSON above)

### Step 3: Update RLS Policies

```sql
CREATE POLICY "Allow anon insert" ON jobs
    FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow anon update" ON jobs
    FOR UPDATE 
    USING (true);
```

## Quick Questions

1. **Is `application_url` unique?** (needed for upsert conflict)
2. **Is `slug` unique?** (alternative for upsert)
3. **How should we handle `company_id`?**
   - Create companies automatically?
   - Leave as NULL?
   - Use a default company?
4. **What should `status` be?** (probably `pending` for new jobs)
5. **What should `slug` be?** (generate from title?)

Let me know and I'll update the script accordingly!

