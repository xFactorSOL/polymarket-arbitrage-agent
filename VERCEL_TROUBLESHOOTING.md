# Vercel Troubleshooting Guide

## Common Issues and Solutions

### 500 INTERNAL_SERVER_ERROR / FUNCTION_INVOCATION_FAILED

This means the function deployed but crashed at runtime. Here's how to debug:

#### 1. Check Vercel Function Logs

1. Go to your Vercel dashboard
2. Click on your project
3. Go to **"Functions"** tab
4. Click on the function that's failing
5. Check the **"Logs"** tab for the actual error

#### 2. Common Causes

**Missing Environment Variables:**
- Make sure these are set in Vercel:
  - `POLYGON_WALLET_PRIVATE_KEY`
  - `OPENAI_API_KEY`
  - `PYTHONPATH` = `.`

**Import Errors:**
- Check if all dependencies are in `requirements.txt`
- Verify Python version (should be 3.9+)

**Path Issues:**
- The entrypoint should be in `api/index.py`
- Make sure `PYTHONPATH=.` is set

#### 3. Test Locally First

```bash
# Install Vercel CLI
npm i -g vercel

# Test locally
vercel dev
```

This will show you the actual error before deploying.

#### 4. Check the Error Endpoint

I've updated the entrypoint to show errors. Visit:
- `https://your-app.vercel.app/` - Should show error details if app failed to load

#### 5. Minimal Test

Create a simple test to verify the setup:

```python
# api/test.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def test():
    return {"status": "ok"}
```

Then update `api/index.py` to import from `test` instead of `api_server` to see if basic FastAPI works.

## Debugging Steps

### Step 1: Check Logs
```bash
# In Vercel dashboard
Functions → Your Function → Logs
```

### Step 2: Verify Environment Variables
```bash
# In Vercel dashboard
Settings → Environment Variables
```

Required:
- `POLYGON_WALLET_PRIVATE_KEY`
- `OPENAI_API_KEY`  
- `PYTHONPATH` = `.`

### Step 3: Test Import Locally
```bash
cd /path/to/repo
export PYTHONPATH=.
python -c "from agents.arbitrage_agent.api_server import app; print('OK')"
```

### Step 4: Check Dependencies
```bash
# Make sure all are in requirements.txt
pip install -r requirements.txt
python -c "from agents.arbitrage_agent.api_server import app"
```

## Quick Fixes

### If it's a missing dependency:
Add to `requirements.txt` and redeploy

### If it's an import error:
Check that `PYTHONPATH=.` is set in Vercel environment variables

### If it's a config error:
The app will show a helpful error message at the root endpoint

## Get Help

1. Check Vercel function logs (most important!)
2. Test locally with `vercel dev`
3. Check the error endpoint I created
4. Verify all environment variables are set

The updated entrypoint will now show you the actual error message when you visit the root URL!
