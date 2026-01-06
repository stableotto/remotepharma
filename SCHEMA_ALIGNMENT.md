# Schema Alignment Guide

## Fields Sent by the Script

The script sends these exact field names to Supabase:

### Core Fields
- `id` (TEXT) - Job ID from the source site
- `site` (TEXT) - Source site (indeed, linkedin, etc.)
- `job_url` (TEXT, UNIQUE) - Primary URL to the job posting
- `job_url_direct` (TEXT) - Direct application URL if available
- `title` (TEXT) - Job title
- `company` (TEXT) - Company name
- `location` (TEXT) - Formatted location string
- `date_posted` (DATE) - When the job was posted
- `is_remote` (BOOLEAN) - Whether job is remote
- `scraped_at` (TIMESTAMP) - When we scraped this job (added by script)

### Job Details
- `job_type` (TEXT) - fulltime, parttime, contract, etc.
- `job_level` (TEXT) - LinkedIn-specific job level
- `job_function` (TEXT) - LinkedIn-specific function
- `listing_type` (TEXT) - Type of listing
- `description` (TEXT) - Full job description

### Salary Information
- `salary_source` (TEXT) - direct_data or description
- `interval` (TEXT) - yearly, monthly, weekly, daily, hourly
- `min_amount` (NUMERIC) - Minimum salary
- `max_amount` (NUMERIC) - Maximum salary
- `currency` (TEXT) - Currency code (USD, etc.)

### Company Information
- `company_industry` (TEXT)
- `company_url` (TEXT)
- `company_logo` (TEXT) - URL to company logo
- `company_url_direct` (TEXT)
- `company_addresses` (TEXT)
- `company_num_employees` (TEXT)
- `company_revenue` (TEXT)
- `company_description` (TEXT)

### Contact & Additional
- `emails` (TEXT) - Comma-separated email addresses
- `skills` (TEXT) - Comma-separated skills (Naukri-specific)
- `experience_range` (TEXT) - Experience required (Naukri-specific)
- `company_rating` (NUMERIC) - Company rating (Naukri-specific)
- `company_reviews_count` (INTEGER) - Number of reviews (Naukri-specific)
- `vacancy_count` (INTEGER) - Number of vacancies (Naukri-specific)
- `work_from_home_type` (TEXT) - Remote type (Naukri-specific)

## How to Align Your Existing Schema

### Option 1: Update Your Existing Schema
If your existing schema is close, you can run an ALTER TABLE migration:

```sql
-- Example: Add missing columns
ALTER TABLE your_table_name 
ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Example: Rename a column if needed
ALTER TABLE your_table_name 
RENAME COLUMN old_name TO new_name;

-- Example: Change column type if needed
ALTER TABLE your_table_name 
ALTER COLUMN column_name TYPE TEXT;
```

### Option 2: Update the Script
If you prefer to keep your schema as-is, we can modify the script to:
1. Map field names to match your schema
2. Use a different table name
3. Transform data before sending

### Option 3: Use Both Schemas
Keep your existing schema for other purposes and create a new table just for this scraper.

## Quick Check Script

Run this to see what fields your existing table has:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

Then compare with the fields listed above.


