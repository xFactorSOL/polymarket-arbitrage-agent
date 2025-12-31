# Manual Vercel Setup - Fix Dependency Installation

## The Problem

Vercel is not automatically installing dependencies from `api/requirements.txt`. The error shows:
```
ModuleNotFoundError: No module named 'fastapi'
```

## Solution: Manual Configuration in Vercel Dashboard

Since automatic detection isn't working, configure it manually:

### Step 1: Go to Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click on your project: `polymarket-arbitrage-agent`

### Step 2: Configure Build Settings

1. Click **"Settings"** tab
2. Click **"General"** in the left sidebar
3. Scroll to **"Build & Development Settings"**

4. Configure these settings:
   - **Framework Preset:** `Other` (or leave blank)
   - **Root Directory:** `.` (default)
   - **Build Command:** Leave **EMPTY** (Vercel will auto-detect)
   - **Install Command:** `pip install -r api/requirements.txt`
   - **Output Directory:** Leave **EMPTY**

### Step 3: Set Environment Variables

1. Still in Settings, click **"Environment Variables"**
2. Add these variables:

   **Required:**
   - `PYTHONPATH` = `.`
   - `POLYGON_WALLET_PRIVATE_KEY` = (your key)
   - `OPENAI_API_KEY` = (your key)

   **Optional:**
   - `ENVIRONMENT` = `production`
   - `LOG_LEVEL` = `INFO`

### Step 4: Redeploy

1. Go to **"Deployments"** tab
2. Click the **"..."** menu on the latest deployment
3. Click **"Redeploy"**
4. Or push a new commit to trigger automatic redeploy

## Alternative: Use Vercel CLI

If dashboard doesn't work, use CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Set environment variables
vercel env add PYTHONPATH
# Enter value: .

vercel env add POLYGON_WALLET_PRIVATE_KEY
# Enter your key

vercel env add OPENAI_API_KEY
# Enter your key

# Deploy
vercel --prod
```

## Verify Dependencies Are Installing

After redeploy, check build logs:

1. Go to **Deployments** tab
2. Click on the deployment
3. Check **"Build Logs"**
4. Look for: `Installing dependencies from api/requirements.txt` or similar

If you see pip installing packages, it's working!

## If Still Not Working

Try creating a `vercel.json` with explicit install:

```json
{
  "installCommand": "pip install -r api/requirements.txt"
}
```

But the dashboard settings should work better.

## Test Endpoint

Once deployed, test:
- `https://your-app.vercel.app/` - Should show API or error details
- `https://your-app.vercel.app/health` - Health check

The updated `api/index.py` will now show helpful error messages if dependencies aren't installed!
