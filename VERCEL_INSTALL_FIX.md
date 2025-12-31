# CRITICAL: Vercel Not Installing Dependencies

## The Problem

Vercel is **NOT** installing dependencies from `api/requirements.txt`. The error shows:
```
ModuleNotFoundError: No module named 'fastapi'
```

## Solution 1: Manual Vercel Dashboard Configuration (DO THIS FIRST)

1. **Go to:** https://vercel.com/dashboard
2. **Click your project:** `polymarket-arbitrage-agent`
3. **Click:** Settings → General
4. **Scroll to:** "Build & Development Settings"

5. **Set these EXACTLY:**
   - **Framework Preset:** `Other` (or leave blank)
   - **Root Directory:** `.` (default)
   - **Build Command:** `echo 'Build complete'`
   - **Install Command:** `pip install --upgrade pip && pip install -r api/requirements.txt`
   - **Output Directory:** (leave empty)

6. **Click "Save"**

7. **Go to:** Deployments tab
8. **Click:** "..." on latest deployment → "Redeploy"

## Solution 2: Check Build Logs

After redeploy, check the build logs. You should see:
```
Installing dependencies...
Collecting fastapi==0.111.0
...
Successfully installed fastapi-0.111.0 ...
```

If you DON'T see this, the install command isn't running.

## Solution 3: Alternative - Use Root requirements.txt

If the above doesn't work, Vercel might be looking for `requirements.txt` at the root:

1. I've created `requirements.txt` at the root with minimal dependencies
2. Vercel should auto-detect it
3. But still set the Install Command in dashboard

## What I Just Fixed

✅ Updated `vercel.json` with explicit `installCommand`
✅ Added `requirements.txt` at root as backup
✅ Fixed `api/index.py` error handler to not require FastAPI
✅ Added better error messages

## Verify It's Working

After redeploy:
1. Check build logs for "Installing dependencies"
2. Visit `https://your-app.vercel.app/`
3. Should see API response OR clear error message

## If Still Failing

The error handler will now show a JSON response even if FastAPI isn't installed, so you can see what's wrong.

**Most likely issue:** Vercel dashboard settings override `vercel.json`. You MUST set the Install Command in the dashboard.
