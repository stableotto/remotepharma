# Quick Start: GitHub Actions + Supabase

## 🎯 What You Need from Supabase

Get these 3 things from your Supabase dashboard:

### 1. Project URL
- **Location:** Settings → API → Project URL
- **Format:** `https://xxxxxxxxxxxxx.supabase.co`
- **Example:** `https://abcdefghijklmnop.supabase.co`

### 2. Anon/Public Key
- **Location:** Settings → API → anon `public` key
- **Format:** Long string starting with `eyJ...`
- **Length:** ~200+ characters
- **Important:** Use the `anon` `public` key, NOT the `service_role` key

### 3. Table Name
- **Location:** Table Editor → Your table name
- **Example:** `pharmacist_jobs` or `jobs` or your custom name
- **Note:** Must match exactly (case-sensitive)

---

## 🚀 GitHub Actions Setup (5 Steps)

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value | Required? |
|------------|-------|-----------|
| `SUPABASE_URL` | Your Supabase Project URL | ✅ Yes |
| `SUPABASE_KEY` | Your Supabase anon key | ✅ Yes |
| `SUPABASE_TABLE_NAME` | Your table name | ⚠️ Only if not `pharmacist_jobs` |
| `SUPABASE_FIELD_MAPPING` | JSON mapping | ⚠️ Only if field names differ |

**Example `SUPABASE_FIELD_MAPPING`:**
```json
{"job_url":"url","company":"company_name"}
```

### Step 3: Test Manually

1. Go to **Actions** tab
2. Click **Daily Pharmacist Job Scraper**
3. Click **Run workflow** → **Run workflow**
4. Watch it run!

### Step 4: Verify in Supabase

1. Go to Supabase → Table Editor
2. Select your table
3. See new job data! 🎉

### Step 5: Done!

The workflow will now run **automatically every day at 2:00 AM UTC**.

---

## 📋 Checklist

- [ ] Got Supabase URL
- [ ] Got Supabase anon key
- [ ] Know your table name
- [ ] Pushed code to GitHub
- [ ] Added `SUPABASE_URL` secret
- [ ] Added `SUPABASE_KEY` secret
- [ ] Added `SUPABASE_TABLE_NAME` secret (if needed)
- [ ] Added `SUPABASE_FIELD_MAPPING` secret (if needed)
- [ ] Tested workflow manually
- [ ] Verified data appears in Supabase

---

## 🔧 Troubleshooting

**Workflow fails?**
1. Check the logs in Actions tab
2. Verify secrets are correct
3. Check table exists in Supabase
4. Test locally first (see below)

**Test locally:**
```bash
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"
export SUPABASE_TABLE_NAME="your-table"  # if needed
python search_pharmacist_jobs.py
```

**Need more help?**
- See `GITHUB_ACTIONS_SETUP.md` for detailed guide
- See `SCHEMA_OPTIONS.md` for schema alignment help

