# 🚨 URGENT: Rotate Your Supabase Keys

## Your keys were exposed - Rotate them immediately!

### Step 1: Rotate in Supabase (2 minutes)

1. Go to: https://supabase.com/dashboard/project/wfzfjvuxophuhtrgznid/settings/api
2. Click **"Reset"** or **"Regenerate"** next to:
   - ✅ `anon` `public` key (for GitHub Actions)
   - ✅ `service_role` key (if you shared it - this is dangerous!)
3. Copy the new keys

### Step 2: Update GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Update `SUPABASE_KEY` with your new anon key
3. Update `SUPABASE_URL` if needed (should be: `https://wfzfjvuxophuhtrgznid.supabase.co`)

### Step 3: Update Local Files (if any)

If you have a `.env` file locally:
```bash
# Update .env file with new keys
SUPABASE_URL=https://wfzfjvuxophuhtrgznid.supabase.co
SUPABASE_KEY=<your-new-anon-key>
```

### Step 4: Verify

1. Test the workflow manually in GitHub Actions
2. Check Supabase logs to ensure old key is rejected
3. Verify new key works

---

## ✅ Good News

- ✅ No keys are hardcoded in your code
- ✅ Workflow file uses secrets correctly
- ✅ `.gitignore` is set up to protect `.env` files
- ✅ You're using the anon key (safer than service_role)

## ⚠️ Important Notes

- **Service Role Key:** If you shared the service_role key, rotate it immediately - it has full database access!
- **Anon Key:** This is safer but still rotate it since it was exposed
- **Never share keys again:** Always use GitHub Secrets or environment variables

---

## After Rotating

Once you've rotated the keys:
1. Delete this file (ROTATE_KEYS_NOW.md)
2. Update GitHub Secrets with new keys
3. Test the workflow
4. Read `SECURITY.md` for best practices

