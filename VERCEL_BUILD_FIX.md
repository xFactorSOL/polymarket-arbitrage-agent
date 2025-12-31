# Fixing Vercel Build Failures

## Common Build Issues

### Issue 1: Dependencies Not Installing

**Solution:** Vercel needs explicit build/install commands.

I've updated `vercel.json` with:
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "installCommand": "pip install -r requirements.txt"
}
```

### Issue 2: Too Many Dependencies

If the full `requirements.txt` is too large, Vercel may timeout. The `api/requirements.txt` has only essential packages.

### Issue 3: Python Version

Make sure Vercel is using Python 3.9. Check in Vercel dashboard:
- Settings → General → Node.js Version (should be auto)
- The `vercel.json` specifies `python3.9` runtime

## Manual Vercel Configuration

If automatic detection fails, configure in Vercel Dashboard:

1. **Go to Project Settings**
2. **General Tab:**
   - **Framework Preset:** Other
   - **Root Directory:** `.` (default)
   - **Build Command:** `pip install -r requirements.txt`
   - **Install Command:** `pip install -r requirements.txt`
   - **Output Directory:** Leave empty

3. **Environment Variables:**
   - `PYTHONPATH` = `.`
   - `POLYGON_WALLET_PRIVATE_KEY` = your key
   - `OPENAI_API_KEY` = your key

## Alternative: Use Minimal Requirements

If build still fails, we can create a minimal `api/requirements.txt` with just:
- fastapi
- uvicorn
- pydantic
- python-dotenv

And let the app handle missing optional dependencies gracefully.

## Check Build Logs

In Vercel Dashboard:
1. Go to your project
2. Click on the failed deployment
3. Check the "Build Logs" tab
4. Look for specific error messages

Common errors:
- `pip install` failures → Check Python version
- `ModuleNotFoundError` → Dependencies not installing
- `ImportError` → Path issues
- Timeout → Too many dependencies

## Quick Test

To test if it's a dependency issue, try deploying with just:

```python
# api/index.py (minimal test)
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def test():
    return {"status": "ok", "message": "Vercel is working!"}
```

If this works, then it's a dependency issue. If it doesn't, it's a Vercel configuration issue.
