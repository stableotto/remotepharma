# Next Steps - Test Your Workflow

## ✅ Secrets Added!

Now let's test that everything works.

## Step 1: Test the Workflow Manually

1. **Go to Actions:**
   - Visit: https://github.com/stableotto/remotepharma/actions

2. **Run the Workflow:**
   - Click on **"Daily Pharmacist Job Scraper"** workflow
   - Click the **"Run workflow"** button (top right)
   - Click **"Run workflow"** again in the dropdown
   - Watch it start running!

3. **Monitor the Run:**
   - Click on the running workflow
   - Click on **"scrape-and-upload"** job
   - Watch the logs in real-time
   - Look for:
     - ✅ "Searching for remote pharmacist jobs..."
     - ✅ "Found X remote pharmacist jobs"
     - ✅ "Successfully uploaded X jobs to Supabase"

## Step 2: Verify in Supabase

1. **Go to Supabase:**
   - Visit: https://supabase.com/dashboard/project/wfzfjvuxophuhtrgznid/editor

2. **Check Your Table:**
   - Select your table (e.g., `pharmacist_jobs`)
   - You should see new rows with job data!
   - Check the `scraped_at` column to see when jobs were added

3. **Query Recent Jobs:**
   ```sql
   SELECT COUNT(*) FROM pharmacist_jobs;
   
   SELECT title, company, job_url, scraped_at 
   FROM pharmacist_jobs 
   ORDER BY scraped_at DESC 
   LIMIT 10;
   ```

## Step 3: Check Workflow Results

1. **View Artifacts:**
   - Go back to the workflow run
   - Scroll down to **"Artifacts"**
   - Download `job-results` to get CSV/JSON files

2. **Review Logs:**
   - Check for any errors or warnings
   - Verify the summary shows jobs found by site

## Step 4: Verify Automatic Schedule

The workflow is set to run **daily at 2:00 AM UTC**.

To verify:
1. Go to: https://github.com/stableotto/remotepharma/actions
2. You'll see scheduled runs appear automatically

To change the schedule:
- Edit `.github/workflows/daily-job-scraper.yml`
- Modify the cron: `'0 2 * * *'` (2 AM UTC daily)

## Troubleshooting

### Workflow Fails?

**Check the logs:**
- Click on the failed workflow
- Look for error messages
- Common issues:
  - Wrong Supabase URL/key → Check secrets
  - Table doesn't exist → Create table in Supabase
  - Field mismatch → Add `SUPABASE_FIELD_MAPPING` secret
  - Rate limiting → Reduce `results_wanted` in script

### No Data in Supabase?

1. **Check table name:**
   - Verify your table name matches
   - Or add `SUPABASE_TABLE_NAME` secret

2. **Check RLS policies:**
   - Make sure anon key can insert
   - Check Supabase → Authentication → Policies

3. **Check logs:**
   - Look for "Successfully uploaded" message
   - Check for any error messages

### Test Locally First

If workflow fails, test locally:

```bash
cd /Users/randy/Downloads/JobSpy-main
export SUPABASE_URL="https://wfzfjvuxophuhtrgznid.supabase.co"
export SUPABASE_KEY="your-anon-key"
python search_pharmacist_jobs.py
```

## Success Checklist

- [ ] Workflow runs successfully
- [ ] Jobs appear in Supabase table
- [ ] CSV/JSON artifacts are created
- [ ] No errors in logs
- [ ] Schedule is set correctly

## You're All Set! 🎉

Your automated job scraper is now:
- ✅ Running daily at 2 AM UTC
- ✅ Scraping from multiple job sites
- ✅ Uploading to Supabase automatically
- ✅ Saving backup files as artifacts

## Next Steps (Optional)

- Set up Supabase dashboard views for easy browsing
- Create email notifications for new jobs
- Build a frontend to display the jobs
- Add more job sites or filters
- Set up monitoring/alerts

