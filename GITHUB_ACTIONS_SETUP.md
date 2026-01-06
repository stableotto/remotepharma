# GitHub Actions Setup Guide

Complete step-by-step guide to set up automated daily job scraping with GitHub Actions.

## Prerequisites Checklist

- [ ] GitHub account
- [ ] GitHub repository (this code pushed to GitHub)
- [ ] Supabase account and project
- [ ] Supabase table created (your existing schema or new one)

---

## Step 1: Get Supabase Credentials

### 1.1 Go to Supabase Dashboard

1. Log in to [supabase.com](https://supabase.com)
2. Select your project (or create a new one)

### 1.2 Get Your Credentials

1. Click **Settings** (gear icon) in the left sidebar
2. Click **API** in the settings menu
3. You'll see two important values:

   **a) Project URL**
   - Located under "Project URL"
   - Format: `https://xxxxxxxxxxxxx.supabase.co`
   - Copy this entire URL

   **b) API Keys**
   - You'll see two keys:
     - **`anon` `public`** key (starts with `eyJ...`)
     - **`service_role`** key (starts with `eyJ...`)
   - **Use the `anon` `public` key** for GitHub Actions
   - Copy the entire key (it's long, ~200+ characters)

### 1.3 Verify Your Table Name

1. Go to **Table Editor** in Supabase
2. Find your table name (e.g., `pharmacist_jobs` or your custom name)
3. Note the exact table name (case-sensitive)

### 1.4 Check Your Table Schema

Make sure your table has these required fields:
- `job_url` (or whatever you named it) - must be UNIQUE
- All other fields that the script sends (see `SCHEMA_ALIGNMENT.md`)

**Quick check SQL:**
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

---

## Step 2: Push Code to GitHub

### 2.1 Initialize Git (if not already done)

```bash
cd /Users/randy/Downloads/JobSpy-main
git init
git add .
git commit -m "Initial commit: Job scraper with Supabase integration"
```

### 2.2 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click **New repository** (or **+** → **New repository**)
3. Name it (e.g., `pharmacist-job-scraper`)
4. Choose **Public** or **Private**
   - Public repos get 2000 free minutes/month
   - Private repos get 2000 free minutes/month (GitHub Free plan)
5. **Don't** initialize with README (you already have files)
6. Click **Create repository**

### 2.3 Push Your Code

```bash
# Add your GitHub repo as remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: Configure GitHub Secrets

### 3.1 Navigate to Secrets

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 3.2 Add Required Secrets

Click **New repository secret** for each of these:

#### Secret 1: `SUPABASE_URL`
- **Name:** `SUPABASE_URL`
- **Value:** Your Supabase Project URL (from Step 1.2a)
  - Example: `https://abcdefghijklmnop.supabase.co`
- Click **Add secret**

#### Secret 2: `SUPABASE_KEY`
- **Name:** `SUPABASE_KEY`
- **Value:** Your Supabase `anon` `public` key (from Step 1.2b)
  - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzMDAwMDAwMCwiZXhwIjoxOTQ1NTc2MDAwfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Click **Add secret**

#### Secret 3: `SUPABASE_TABLE_NAME` (if different from default)
- **Name:** `SUPABASE_TABLE_NAME`
- **Value:** Your table name (from Step 1.3)
  - Example: `pharmacist_jobs` or `jobs` or `your_custom_table`
- Click **Add secret**
- **Note:** If your table is named `pharmacist_jobs`, you can skip this secret

#### Secret 4: `SUPABASE_FIELD_MAPPING` (only if field names differ)
- **Name:** `SUPABASE_FIELD_MAPPING`
- **Value:** JSON object mapping script fields to your table fields
  - Example: `{"job_url":"url","company":"company_name"}`
  - Example: `{}` (empty if no mapping needed)
- Click **Add secret**
- **Note:** Only add this if your table uses different field names

### 3.3 Verify Secrets

You should now see these secrets listed:
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_KEY`
- ✅ `SUPABASE_TABLE_NAME` (optional)
- ✅ `SUPABASE_FIELD_MAPPING` (optional)

---

## Step 4: Test the Workflow

### 4.1 Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. You should see **Daily Pharmacist Job Scraper** workflow
3. Click on it
4. Click **Run workflow** → **Run workflow** (green button)
5. Watch it run!

### 4.2 Check the Run

1. Click on the running workflow
2. Click on **scrape-and-upload** job
3. Watch the logs in real-time
4. Look for:
   - ✅ "Successfully uploaded X jobs to Supabase"
   - ❌ Any error messages

### 4.3 Verify in Supabase

1. Go back to Supabase
2. Open **Table Editor**
3. Select your table
4. You should see new rows with job data!

---

## Step 5: Verify Automatic Schedule

### 5.1 Check Schedule

The workflow is set to run **daily at 2:00 AM UTC**.

To verify or change the schedule:
1. Go to `.github/workflows/daily-job-scraper.yml`
2. Find the `cron` line:
   ```yaml
   - cron: '0 2 * * *'  # 2 AM UTC daily
   ```
3. Adjust if needed (see cron format below)

### 5.2 Cron Schedule Examples

```yaml
'0 2 * * *'    # 2:00 AM UTC daily
'0 14 * * *'   # 2:00 PM UTC daily (10 AM EST)
'0 0 * * *'    # Midnight UTC daily
'0 8 * * 1'    # 8 AM UTC every Monday
'*/30 * * * *' # Every 30 minutes (for testing)
```

**Cron format:** `minute hour day month weekday`
- Minute: 0-59
- Hour: 0-23 (UTC)
- Day: 1-31
- Month: 1-12
- Weekday: 0-7 (0 and 7 = Sunday)

---

## Step 6: Monitor and Maintain

### 6.1 Check Workflow Status

- Go to **Actions** tab regularly
- Green checkmark = success ✅
- Red X = failure ❌

### 6.2 View Results

**In GitHub:**
- Go to workflow run → **Artifacts**
- Download `job-results` to get CSV/JSON files

**In Supabase:**
- Query your table:
  ```sql
  SELECT COUNT(*) FROM your_table_name;
  SELECT * FROM your_table_name 
  WHERE scraped_at > NOW() - INTERVAL '24 hours'
  ORDER BY scraped_at DESC;
  ```

### 6.3 Troubleshooting

**If workflow fails:**

1. **Check logs** - Click on failed workflow → View logs
2. **Common issues:**
   - Wrong Supabase URL/key → Check secrets
   - Table doesn't exist → Create table in Supabase
   - Field mismatch → Add `SUPABASE_FIELD_MAPPING` secret
   - Rate limiting → Reduce `results_wanted` in script
   - Missing dependencies → Check requirements.txt

3. **Test locally first:**
   ```bash
   export SUPABASE_URL="your-url"
   export SUPABASE_KEY="your-key"
   python search_pharmacist_jobs.py
   ```

---

## Quick Reference: What You Need from Supabase

| Item | Where to Find | Example |
|------|---------------|---------|
| **Project URL** | Settings → API → Project URL | `https://abc123.supabase.co` |
| **Anon Key** | Settings → API → anon public key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| **Table Name** | Table Editor → Your table | `pharmacist_jobs` |
| **Field Names** | Table Editor → Columns | `job_url`, `company`, etc. |

---

## Summary Checklist

- [ ] Got Supabase URL and anon key
- [ ] Created/verified table in Supabase
- [ ] Pushed code to GitHub
- [ ] Added `SUPABASE_URL` secret
- [ ] Added `SUPABASE_KEY` secret
- [ ] Added `SUPABASE_TABLE_NAME` secret (if needed)
- [ ] Added `SUPABASE_FIELD_MAPPING` secret (if needed)
- [ ] Tested workflow manually
- [ ] Verified data in Supabase
- [ ] Confirmed schedule is correct

---

## Next Steps

Once everything is working:
- Set up Supabase dashboard views for easy browsing
- Create email notifications for new jobs
- Build a frontend to display jobs
- Add more job sites or filters

