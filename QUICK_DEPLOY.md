# Quick Deploy Guide - Render

## 🚀 Deploy in 5 Minutes

### Step 1: Push to GitHub

```bash
# If not already a git repo
git init
git add .
git commit -m "Deploy arbitrage agent"

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Use these settings:
   - **Name**: `polymarket-arbitrage-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn agents.arbitrage_agent.api_server:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In Render dashboard, add these environment variables:

**Required:**
```
POLYGON_WALLET_PRIVATE_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PYTHONPATH=.
```

**Optional:**
```
ODDS_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
SLACK_WEBHOOK_URL=your_webhook_url
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 4: Deploy!

Click **"Create Web Service"** and wait for deployment.

### Step 5: Test

Once deployed, visit:
- `https://your-app.onrender.com/` - Dashboard
- `https://your-app.onrender.com/health` - Health check
- `https://your-app.onrender.com/status` - Status

## 📊 Using the Dashboard

1. Visit your deployed URL
2. Click **"Manual Scan"** to test
3. Click **"Start Scanning"** for continuous mode
4. View markets in real-time

## 🔧 API Endpoints

- `GET /` - Dashboard
- `GET /health` - Health check
- `GET /status` - Agent status
- `GET /markets` - Get markets
- `POST /scan` - Manual scan
- `POST /start` - Start scanning
- `POST /stop` - Stop scanning

## 🐛 Troubleshooting

**Build fails?**
- Check that all dependencies are in `requirements.txt`
- Verify Python version (3.9)

**Runtime errors?**
- Check environment variables are set
- View logs in Render dashboard
- Test locally first: `python agents/arbitrage_agent/api_server.py`

**Can't connect?**
- Wait a few minutes for deployment
- Check the service is running (not sleeping)
- Verify the URL is correct

## 💡 Tips

- **Free tier**: Render spins down after 15 min inactivity
- **Always-on**: Upgrade to paid plan for $7/month
- **Monitoring**: Set up health checks
- **Logs**: Check Render dashboard for detailed logs

That's it! Your arbitrage agent is now live! 🎉
