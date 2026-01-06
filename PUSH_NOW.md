# Push to GitHub - Use HTTPS with Personal Access Token

## ✅ Remote is now set to HTTPS

The remote has been switched from SSH to HTTPS. Now you can push using a Personal Access Token.

## Step 1: Create Personal Access Token

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Fill in:
   - **Note:** `remotepharma-push`
   - **Expiration:** Choose your preference (90 days, 1 year, or no expiration)
   - **Select scopes:** Check ✅ **`repo`** (this gives full repository access)
4. Click **"Generate token"** at the bottom
5. **⚠️ IMPORTANT:** Copy the token immediately! It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again!

## Step 2: Push to GitHub

Run this command:

```bash
cd /Users/randy/Downloads/JobSpy-main
git push -u origin main
```

When prompted:
- **Username:** `stableotto`
- **Password:** Paste your Personal Access Token (NOT your GitHub password!)

## Alternative: Store Credentials (Optional)

If you don't want to enter credentials every time:

```bash
# Store credentials in macOS Keychain
git config --global credential.helper osxkeychain

# Then push (will prompt once, then remember)
git push -u origin main
```

## Step 3: Verify Push

After successful push:
1. Go to: https://github.com/stableotto/remotepharma
2. You should see all your files!

## Step 4: Add GitHub Secrets

1. Go to: https://github.com/stableotto/remotepharma/settings/secrets/actions
2. Click **"New repository secret"** for each:

   **Secret 1:**
   - Name: `SUPABASE_URL`
   - Value: `https://wfzfjvuxophuhtrgznid.supabase.co`

   **Secret 2:**
   - Name: `SUPABASE_KEY`
   - Value: Your Supabase anon key (after rotating it!)

3. Click **"Add secret"** for each

## Step 5: Test Workflow

1. Go to: https://github.com/stableotto/remotepharma/actions
2. Click **"Daily Pharmacist Job Scraper"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch it run! 🚀

---

## Troubleshooting

**"Authentication failed"?**
- Make sure you're using the Personal Access Token (not your password)
- Verify the token has `repo` scope
- Try generating a new token

**"Repository not found"?**
- Make sure you're logged into the correct GitHub account
- Verify the repo exists at: https://github.com/stableotto/remotepharma

**Still having issues?**
- Try using GitHub Desktop: https://desktop.github.com/
- Or use GitHub CLI: `brew install gh && gh auth login`

