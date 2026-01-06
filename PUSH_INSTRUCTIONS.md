# Push to GitHub - Authentication Required

Your repository is configured: `https://github.com/stableotto/remotepharma`

## Option 1: Use GitHub CLI (Easiest)

If you have GitHub CLI installed:

```bash
cd /Users/randy/Downloads/JobSpy-main
gh auth login
git push -u origin main
```

## Option 2: Use Personal Access Token (Recommended)

1. **Create a Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click **Generate new token** → **Generate new token (classic)**
   - Name it: `remotepharma-push`
   - Select scope: `repo` (full control of private repositories)
   - Click **Generate token**
   - **Copy the token immediately** (you won't see it again!)

2. **Push using the token:**
   ```bash
   cd /Users/randy/Downloads/JobSpy-main
   git push -u origin main
   ```
   
   When prompted:
   - **Username:** `stableotto`
   - **Password:** Paste your personal access token (not your GitHub password)

## Option 3: Use SSH (If you have SSH keys set up)

1. **Change remote to SSH:**
   ```bash
   cd /Users/randy/Downloads/JobSpy-main
   git remote set-url origin git@github.com:stableotto/remotepharma.git
   git push -u origin main
   ```

2. **If SSH keys aren't set up:**
   - Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

## Option 4: Use GitHub Desktop

1. Install GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Add the repository
4. Click "Publish repository"

---

## Quick Command (After Authentication)

Once authenticated, just run:

```bash
cd /Users/randy/Downloads/JobSpy-main
git push -u origin main
```

---

## After Pushing Successfully

1. **Add GitHub Secrets:**
   - Go to: https://github.com/stableotto/remotepharma/settings/secrets/actions
   - Add `SUPABASE_URL`: `https://wfzfjvuxophuhtrgznid.supabase.co`
   - Add `SUPABASE_KEY`: Your Supabase anon key (after rotating!)

2. **Test the Workflow:**
   - Go to: https://github.com/stableotto/remotepharma/actions
   - Click "Daily Pharmacist Job Scraper"
   - Click "Run workflow"

---

## Troubleshooting

**"Authentication failed"?**
- Make sure you're using a Personal Access Token (not password)
- Check token has `repo` scope
- Try using GitHub CLI: `gh auth login`

**"Permission denied"?**
- Verify you own the repository
- Check you're logged into the correct GitHub account

**"Repository not found"?**
- Make sure the repo exists at: https://github.com/stableotto/remotepharma
- Check you have write access

