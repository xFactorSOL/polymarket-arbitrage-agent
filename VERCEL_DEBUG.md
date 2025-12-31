# Debugging Vercel Build Failures

## Step 1: Check Build Logs

In Vercel Dashboard:
1. Go to your project
2. Click on the failed deployment (red X)
3. Open "Build Logs" tab
4. Look for the specific error

## Step 2: Common Build Errors

### Error: "Build Command Failed"
**Solution:** The build command might be wrong. Try:
- Remove `buildCommand` from vercel.json (let Vercel auto-detect)
- Or set it to: `echo "No build needed"`

### Error: "Install Command Failed"
**Solution:** Dependencies might be too large. Try:
- Use minimal `api/requirements.txt` (already created)
- Or remove `installCommand` and let Vercel auto-detect

### Error: "Function Size Too Large"
**Solution:** The function bundle is too big. Options:
- Use `.vercelignore` to exclude files (already created)
- Reduce dependencies in `api/requirements.txt`

### Error: "Import Error"
**Solution:** Path or dependency issues:
- Check `PYTHONPATH=.` is set in environment variables
- Verify all imports are available

## Step 3: Test with Minimal App

I've created `api/test.py` as a minimal test. To use it:

1. **Temporarily rename files:**
   ```bash
   mv api/index.py api/index.py.backup
   mv api/test.py api/index.py
   ```

2. **Commit and push:**
   ```bash
   git add api/
   git commit -m "Test minimal Vercel deployment"
   git push
   ```

3. **If this works**, the issue is with dependencies or imports
4. **If this fails**, the issue is with Vercel configuration

## Step 4: Vercel Dashboard Settings

Go to Vercel Dashboard → Your Project → Settings → General:

**Build & Development Settings:**
- Framework Preset: **Other** (or leave blank)
- Root Directory: `.` (default)
- Build Command: (leave empty or `echo "No build"`)
- Install Command: (leave empty - Vercel auto-detects `api/requirements.txt`)
- Output Directory: (leave empty)

**Environment Variables:**
- `PYTHONPATH` = `.`
- `POLYGON_WALLET_PRIVATE_KEY` = (your key)
- `OPENAI_API_KEY` = (your key)

## Step 5: Alternative Configuration

If automatic detection doesn't work, try this minimal `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

Remove `buildCommand` and `installCommand` - let Vercel handle it automatically.

## Quick Fix Checklist

- [ ] Check build logs for specific error
- [ ] Verify `api/requirements.txt` exists
- [ ] Check environment variables are set
- [ ] Try minimal `vercel.json` (remove build/install commands)
- [ ] Test with `api/test.py` minimal app
- [ ] Verify Python 3.9 is selected in Vercel

## Get Help

Share the exact error message from Vercel build logs and I can help fix it!
