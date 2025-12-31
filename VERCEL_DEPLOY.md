# Deploying to Vercel

## Quick Deploy

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Add environment variables**:
   ```bash
   vercel env add POLYGON_WALLET_PRIVATE_KEY
   vercel env add OPENAI_API_KEY
   vercel env add PYTHONPATH
   # Enter value: .
   ```

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: GitHub Integration

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New..." → "Project"**
3. **Import your GitHub repository**: `xFactorSOL/polymarket-arbitrage-agent`
4. **Configure**:
   - Framework Preset: **Other**
   - Root Directory: `.` (leave as default)
   - Build Command: `pip install -r requirements.txt` (optional, Vercel auto-detects)
   - Output Directory: Leave empty
5. **Add Environment Variables**:
   - `POLYGON_WALLET_PRIVATE_KEY` = your key
   - `OPENAI_API_KEY` = your key
   - `PYTHONPATH` = `.`
6. **Click "Deploy"**

## File Structure

Vercel expects the FastAPI app in one of these locations:
- ✅ `api/index.py` (created)
- ✅ `api/app.py` (created)
- ✅ `pyproject.toml` with app script (created)

All three are set up for maximum compatibility.

## Environment Variables

Add these in Vercel dashboard (Settings → Environment Variables):

**Required:**
- `POLYGON_WALLET_PRIVATE_KEY`
- `OPENAI_API_KEY`
- `PYTHONPATH` = `.`

**Optional:**
- `ODDS_API_KEY`
- `NEWS_API_KEY`
- `SLACK_WEBHOOK_URL`
- `ENVIRONMENT` = `production`
- `LOG_LEVEL` = `INFO`

## Testing Locally

Test the Vercel setup locally:

```bash
vercel dev
```

This will start a local server that mimics Vercel's environment.

## API Endpoints

Once deployed, your API will be available at:
- `https://your-project.vercel.app/` - Dashboard
- `https://your-project.vercel.app/health` - Health check
- `https://your-project.vercel.app/status` - Status
- `https://your-project.vercel.app/markets` - Markets
- `https://your-project.vercel.app/docs` - API documentation (FastAPI auto-generated)

## Troubleshooting

### Error: "No fastapi entrypoint found"
- ✅ Fixed: Created `api/index.py` and `api/app.py`
- ✅ Fixed: Created `pyproject.toml` with configuration

### Import errors
- Ensure `PYTHONPATH=.` is set in environment variables
- Check that all dependencies are in `requirements.txt`

### Build fails
- Check Vercel build logs
- Verify Python version (should be 3.9+)
- Ensure all dependencies are installable

### Runtime errors
- Check function logs in Vercel dashboard
- Verify environment variables are set
- Test locally with `vercel dev`

## Differences from Render

- **Serverless**: Vercel uses serverless functions (not always-on)
- **Cold starts**: First request may be slower
- **Timeout**: 10 seconds for hobby, 60 seconds for pro
- **Auto-scaling**: Handles traffic automatically

## Cost

- **Hobby (Free)**: Unlimited deployments, 100GB bandwidth
- **Pro ($20/month)**: Better performance, longer timeouts

## Next Steps

1. Deploy to Vercel
2. Test the endpoints
3. Monitor function logs
4. Set up custom domain (optional)

Your agent is ready for Vercel! 🚀
