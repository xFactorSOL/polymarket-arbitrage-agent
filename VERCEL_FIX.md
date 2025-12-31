# Fixing Vercel "No module named 'fastapi'" Error

## The Problem

Vercel is not installing dependencies from `requirements.txt`. The error shows:
```
ModuleNotFoundError: No module named 'fastapi'
```

## Solution

I've created `api/requirements.txt` which Vercel will automatically detect and install.

### What I Did

1. **Created `api/requirements.txt`** - Vercel automatically installs dependencies from `requirements.txt` in the `api/` directory
2. **Updated `vercel.json`** - Added runtime specification
3. **Added minimal dependencies** - Only the essential packages needed for the API

### Manual Fix (If Needed)

If the automatic detection doesn't work, you can:

1. **In Vercel Dashboard:**
   - Go to your project → Settings → General
   - Under "Build & Development Settings"
   - Set **Install Command**: `pip install -r requirements.txt`

2. **Or add to vercel.json:**
   ```json
   {
     "installCommand": "pip install -r requirements.txt"
   }
   ```

### Verify Dependencies

Make sure these are in your root `requirements.txt`:
- `fastapi==0.111.0`
- `uvicorn==0.30.3`
- `pydantic==2.8.2`
- `python-dotenv==1.0.1`
- `httpx==0.27.0`
- `tenacity==8.5.0`

### After Fix

1. Push the changes
2. Vercel will redeploy automatically
3. Check the build logs to see if dependencies are installing
4. The function should now work!

## Why This Happens

Vercel's Python runtime needs to know which dependencies to install. By placing `requirements.txt` in the `api/` directory, Vercel automatically detects and installs them for serverless functions.
