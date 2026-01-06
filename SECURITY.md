# ⚠️ SECURITY ALERT - ACTION REQUIRED

## 🔴 IMMEDIATE ACTION: Rotate Your Supabase Keys

**Your Supabase credentials were exposed in this conversation. You MUST rotate them immediately.**

### Steps to Rotate Keys:

1. **Go to Supabase Dashboard**
   - Settings → API → API Keys

2. **Rotate the anon key:**
   - Click "Reset" or "Regenerate" on the `anon` `public` key
   - Copy the new key

3. **Rotate the service_role key (if you shared it):**
   - Click "Reset" or "Regenerate" on the `service_role` key
   - Copy the new key
   - **⚠️ WARNING:** Service role key has full database access - keep it secret!

4. **Update GitHub Secrets:**
   - Go to your GitHub repo → Settings → Secrets
   - Update `SUPABASE_KEY` with the new anon key
   - Update any other secrets if you rotated them

5. **Update Local Environment:**
   - Update any `.env` files with new keys
   - Never commit `.env` files to git

---

## 🔒 Best Practices for API Keys

### ✅ DO:
- ✅ Store keys in GitHub Secrets (for Actions)
- ✅ Use environment variables locally (`.env` file)
- ✅ Use `.gitignore` to exclude `.env` files
- ✅ Use the `anon` key for GitHub Actions (not service_role)
- ✅ Rotate keys if accidentally exposed
- ✅ Use different keys for different environments

### ❌ DON'T:
- ❌ Commit API keys to git
- ❌ Share keys in chat/email/screenshots
- ❌ Hardcode keys in source code
- ❌ Use service_role key in client-side code
- ❌ Share keys publicly (even in "private" repos that might become public)

---

## 🛡️ Security Checklist

Before pushing to GitHub:

- [ ] No API keys in source code
- [ ] No API keys in commit history
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` template (without real keys)
- [ ] All secrets stored in GitHub Secrets
- [ ] Using `anon` key (not `service_role`) for Actions

---

## 🔍 How to Check for Exposed Keys

### Check Git History:
```bash
# Search git history for your key
git log -p -S "your-key-here" --all

# If found, you may need to rewrite history (advanced)
```

### Check Current Files:
```bash
# Search for Supabase URLs
grep -r "supabase.co" .

# Search for JWT tokens (start with eyJ)
grep -r "eyJ" . --exclude-dir=.git
```

### Check GitHub:
- Go to repository → Settings → Security → Secret scanning
- GitHub will alert you if secrets are detected

---

## 📝 Safe Key Storage

### For GitHub Actions:
Use **Repository Secrets**:
1. Go to: Settings → Secrets and variables → Actions
2. Add secrets there
3. Reference in workflow: `${{ secrets.SUPABASE_KEY }}`

### For Local Development:
Use `.env` file (in `.gitignore`):
```bash
# .env (DO NOT COMMIT THIS FILE)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE_NAME=pharmacist_jobs
```

### Create `.env.example` (safe to commit):
```bash
# .env.example (safe template)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE_NAME=pharmacist_jobs
```

---

## 🚨 If Keys Are Exposed

1. **Rotate immediately** (see steps above)
2. **Check access logs** in Supabase dashboard
3. **Review recent database changes**
4. **Update all places using the old key**
5. **Consider enabling additional security**:
   - IP restrictions
   - Rate limiting
   - Row Level Security (RLS) policies

---

## 🔐 Service Role Key vs Anon Key

### Anon Key (Use This for GitHub Actions)
- ✅ Safe for client-side use
- ✅ Respects Row Level Security (RLS)
- ✅ Limited permissions
- ✅ Can be rotated easily

### Service Role Key (DANGEROUS)
- ❌ Bypasses all RLS policies
- ❌ Full database access
- ❌ NEVER use in client-side code
- ❌ NEVER commit to git
- ❌ Only use in secure server environments
- ⚠️ **You shared this - rotate it NOW!**

---

## 📚 Additional Resources

- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/security)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

