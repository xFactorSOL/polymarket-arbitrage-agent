# CRITICAL: Fix Vercel Dependencies - 4 Errors

## The Problem

All 4 errors show: `Error importing api/index.py` - This means FastAPI is not being installed.

## IMMEDIATE FIX - Do This Now

### Step 1: Vercel Dashboard Configuration

1. **Go to:** https://vercel.com/dashboard
2. **Click your project:** `polymarket-arbitrage-agent`
3. **Click:** Settings → General
4. **Scroll to:** "Build & Development Settings"

5. **Set these EXACTLY:**
   - **Framework Preset:** `Other` (or blank)
   - **Root Directory:** `.` (default)
   - **Build Command:** `echo "No build needed"`
   - **Install Command:** `pip install -r api/requirements.txt`
   - **Output Directory:** (leave empty)

6. **Click "Save"**

### Step 2: Environment Variables

1. **Still in Settings**, click **"Environment Variables"**
2. **Add these (if not already set):**
   - `PYTHONPATH` = `.`
   - `POLYGON_WALLET_PRIVATE_KEY` = (your key)
   - `OPENAI_API_KEY` = (your key)

### Step 3: Redeploy

1. **Go to:** Deployments tab
2. **Click:** "..." on latest deployment
3. **Click:** "Redeploy"
4. **OR:** Just push a new commit (I'll do this)

## What I Just Fixed

✅ Simplified `api/index.py` - Better error handling
✅ Added `installCommand` to `vercel.json`
✅ Clear error messages if FastAPI isn't installed

## Verify It's Working

After redeploy, check build logs for:
- ✅ "Installing dependencies from api/requirements.txt"
- ✅ "Successfully installed fastapi"
- ✅ No import errors

## If Still Failing

The error will now show a clear message. Check:
1. **Build Logs** - Do you see pip installing packages?
2. **Function Logs** - What's the exact error message?

The updated code will now fail fast with a clear error message if FastAPI isn't installed!
