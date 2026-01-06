# Setup Guide: Daily Pharmacist Job Scraper with Supabase

This guide will help you set up automated daily job scraping that uploads results to Supabase.

## Prerequisites

- A GitHub account
- A Supabase account (free tier works)
- Python 3.10+ (for local testing)

## Step 1: Set Up Supabase Database

### 1.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Create a new project (or use an existing one)
3. Note your project URL and anon/public key from Settings → API

### 1.2 Create the Database Table

Run this SQL in the Supabase SQL Editor:

```sql
-- Create table for pharmacist jobs
CREATE TABLE IF NOT EXISTS pharmacist_jobs (
    id TEXT PRIMARY KEY,
    site TEXT,
    job_url TEXT UNIQUE NOT NULL,
    job_url_direct TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    date_posted DATE,
    job_type TEXT,
    salary_source TEXT,
    interval TEXT,
    min_amount NUMERIC,
    max_amount NUMERIC,
    currency TEXT,
    is_remote BOOLEAN,
    job_level TEXT,
    job_function TEXT,
    listing_type TEXT,
    emails TEXT,
    description TEXT,
    company_industry TEXT,
    company_url TEXT,
    company_logo TEXT,
    company_url_direct TEXT,
    company_addresses TEXT,
    company_num_employees TEXT,
    company_revenue TEXT,
    company_description TEXT,
    skills TEXT,
    experience_range TEXT,
    company_rating NUMERIC,
    company_reviews_count INTEGER,
    vacancy_count INTEGER,
    work_from_home_type TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on job_url for faster lookups
CREATE INDEX IF NOT EXISTS idx_job_url ON pharmacist_jobs(job_url);

-- Create index on scraped_at for querying recent jobs
CREATE INDEX IF NOT EXISTS idx_scraped_at ON pharmacist_jobs(scraped_at);

-- Enable Row Level Security (RLS) - adjust policies as needed
ALTER TABLE pharmacist_jobs ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to read (adjust based on your needs)
CREATE POLICY "Allow public read access" ON pharmacist_jobs
    FOR SELECT USING (true);

-- Create a policy that allows service role to insert/update
CREATE POLICY "Allow service role insert/update" ON pharmacist_jobs
    FOR ALL USING (auth.role() = 'service_role');
```

### 1.3 Get Your Supabase Credentials

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

## Step 2: Set Up GitHub Actions Secrets

### 2.1 Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

   - **Name:** `SUPABASE_URL`
     **Value:** Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)

   - **Name:** `SUPABASE_KEY`
     **Value:** Your Supabase anon/public key

### 2.2 Verify Secrets

The workflow file (`.github/workflows/daily-job-scraper.yml`) is already configured to use these secrets.

## Step 3: Test Locally (Optional)

### 3.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.2 Set Environment Variables

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key-here"
```

### 3.3 Run the Script

```bash
python search_pharmacist_jobs.py
```

This will:
- Scrape jobs from multiple sites
- Save results to CSV and JSON files
- Upload to Supabase (if credentials are set)

## Step 4: GitHub Actions Workflow

### 4.1 Automatic Daily Runs

The workflow is configured to run **daily at 2:00 AM UTC**. 

To change the schedule, edit `.github/workflows/daily-job-scraper.yml` and modify the cron expression:

```yaml
- cron: '0 2 * * *'  # 2 AM UTC daily
```

Cron format: `minute hour day month weekday`
- `0 2 * * *` = 2:00 AM UTC every day
- `0 14 * * *` = 2:00 PM UTC every day (10 AM EST)

### 4.2 Manual Trigger

You can also trigger the workflow manually:
1. Go to **Actions** tab in GitHub
2. Select **Daily Pharmacist Job Scraper**
3. Click **Run workflow**

### 4.3 View Results

- **GitHub Actions**: Check the workflow run logs
- **Supabase**: Query the `pharmacist_jobs` table
- **Artifacts**: Download CSV/JSON from workflow runs (kept for 7 days)

## Step 5: Query Your Data in Supabase

### Example Queries

```sql
-- Get all jobs from the last 24 hours
SELECT * FROM pharmacist_jobs 
WHERE scraped_at > NOW() - INTERVAL '24 hours'
ORDER BY scraped_at DESC;

-- Count jobs by site
SELECT site, COUNT(*) as count 
FROM pharmacist_jobs 
GROUP BY site;

-- Get jobs with salary information
SELECT title, company, min_amount, max_amount, currency, job_url
FROM pharmacist_jobs
WHERE min_amount IS NOT NULL
ORDER BY min_amount DESC;

-- Find duplicate jobs (same URL, different scrape times)
SELECT job_url, COUNT(*) as occurrences
FROM pharmacist_jobs
GROUP BY job_url
HAVING COUNT(*) > 1;
```

## Troubleshooting

### GitHub Actions Fails

1. **Check secrets**: Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
2. **Check logs**: View the workflow run logs for error messages
3. **Test locally**: Run the script locally to debug issues

### Supabase Upload Fails

1. **Check RLS policies**: Ensure your anon key has insert permissions
2. **Check table schema**: Verify the table matches the expected structure
3. **Check API key**: Ensure you're using the anon/public key, not the service role key

### Rate Limiting

- LinkedIn may rate limit after ~10 pages
- Consider using proxies (add to workflow secrets if needed)
- Reduce `results_wanted` if hitting limits

## Customization

### Change Search Parameters

Edit `search_pharmacist_jobs.py`:

```python
jobs = scrape_jobs(
    site_name=["indeed", "linkedin"],  # Change sites
    search_term="pharmacist",           # Change search term
    is_remote=True,                     # Remote only
    results_wanted=100,                  # More/fewer results
    country_indeed='USA',
)
```

### Change Table Name

1. Update the table name in `search_pharmacist_jobs.py`:
   ```python
   supabase.table("your_table_name").upsert(...)
   ```

2. Update the SQL schema in Step 1.2 with your table name

## Next Steps

- Set up Supabase dashboard views for easy job browsing
- Create email notifications for new jobs
- Build a frontend to display the jobs
- Add filtering and search functionality


