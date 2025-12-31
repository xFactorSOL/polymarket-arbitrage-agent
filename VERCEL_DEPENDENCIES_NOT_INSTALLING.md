# CRITICAL: Vercel Not Installing Dependencies

## The Problem

Vercel is **NOT** installing dependencies. The error shows FastAPI is missing, which means the install command isn't running.

## Root Cause

Vercel dashboard settings **OVERRIDE** `vercel.json`. Even if `vercel.json` has `installCommand`, Vercel might ignore it if dashboard settings are different.

## SOLUTION - Do This Now

### Step 1: Check Current Settings

1. Go to: https://vercel.com/dashboard
2. Click your project: `polymarket-arbitrage-agent`
3. Click: **Settings** → **General**
4. Scroll to: **"Build & Development Settings"**

### Step 2: Set Install Command

**Set these EXACTLY:**

- **Framework Preset:** `Other` (or leave blank)
- **Root Directory:** `.` (default)
- **Build Command:** `echo 'Build complete'` (or leave empty)
- **Install Command:** `pip install --upgrade pip && pip install -r api/requirements.txt`
- **Output Directory:** (leave empty)

### Step 3: Save and Redeploy

1. Click **"Save"** at the bottom
2. Go to **Deployments** tab
3. Click **"..."** on latest deployment
4. Click **"Redeploy"**

### Step 4: Verify Build Logs

After redeploy, **check the build logs**. You MUST see:

```
Installing dependencies...
Collecting fastapi==0.111.0
  Downloading fastapi-0.111.0-py3-none-any.whl
...
Successfully installed fastapi-0.111.0 ...
```

**If you DON'T see "Installing dependencies..." in the logs, the install command isn't running.**

## Alternative: Use Root requirements.txt

If the above doesn't work, Vercel might auto-detect `requirements.txt` at the root:

1. I've created `requirements.txt` at the root
2. Vercel should auto-detect it
3. But you still need to set Install Command in dashboard

## Why This Happens

Vercel's Python runtime requires explicit installation commands. The `@vercel/python` builder doesn't automatically install from `api/requirements.txt` - you must tell it to.

## Test After Fix

1. Wait for deployment to complete
2. Visit: `https://your-app.vercel.app/`
3. Should see either:
   - API response (success!)
   - JSON error with clear message (shows what's wrong)

The updated code will now show a JSON error even if FastAPI isn't installed, so you can see what's happening.
