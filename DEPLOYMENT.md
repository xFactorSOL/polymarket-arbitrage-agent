# Deployment Guide - Polymarket Arbitrage Agent

This guide will help you deploy the Polymarket Arbitrage Agent to Render (or similar platforms).

## Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Environment Variables** - Have your API keys ready

## Deployment Options

### Option 1: Render (Recommended)

Render is a great platform for deploying Python applications with minimal configuration.

#### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - Polymarket Arbitrage Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### Step 2: Deploy on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Name**: `polymarket-arbitrage-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn agents.arbitrage_agent.api_server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `.` (leave as default)

5. **Add Environment Variables** in Render dashboard:
   ```
   PYTHONPATH=.
   PORT=8000
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   POLYGON_WALLET_PRIVATE_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ODDS_API_KEY=your_key_here (optional)
   NEWS_API_KEY=your_key_here (optional)
   SLACK_WEBHOOK_URL=your_webhook_url (optional)
   ```

6. **Click "Create Web Service"**

#### Step 3: Verify Deployment

Once deployed, you'll get a URL like: `https://polymarket-arbitrage-agent.onrender.com`

Test the endpoints:
- `https://your-app.onrender.com/` - API info
- `https://your-app.onrender.com/health` - Health check
- `https://your-app.onrender.com/status` - Agent status
- `https://your-app.onrender.com/markets` - Get markets

### Option 2: Railway

Railway is another excellent option for Python deployments.

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Set environment variables** in Railway dashboard

### Option 3: Heroku

1. **Install Heroku CLI**

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set POLYGON_WALLET_PRIVATE_KEY=your_key
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set PYTHONPATH=.
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 4: Docker (Any Platform)

The repository includes a Dockerfile. You can deploy to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

#### Build and Run Locally

```bash
docker build -t arbitrage-agent .
docker run -p 8000:8000 \
  -e POLYGON_WALLET_PRIVATE_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -e PYTHONPATH=. \
  arbitrage-agent
```

## API Endpoints

Once deployed, your API will have these endpoints:

### Health & Status

- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Agent status
- `GET /config` - Configuration (non-sensitive)

### Market Operations

- `GET /markets` - Get recently found markets
- `GET /markets/{market_id}` - Get specific market details
- `POST /scan` - Perform manual scan
  ```json
  {
    "min_prob": 0.92,
    "max_prob": 0.99,
    "time_window_hours": 48.0,
    "limit": 50
  }
  ```

### Control

- `POST /start` - Start continuous scanning
- `POST /stop` - Stop continuous scanning
- `GET /statistics` - Get agent statistics

## Testing the Deployment

### Using curl

```bash
# Health check
curl https://your-app.onrender.com/health

# Get status
curl https://your-app.onrender.com/status

# Manual scan
curl -X POST https://your-app.onrender.com/scan \
  -H "Content-Type: application/json" \
  -d '{"min_prob": 0.92, "max_prob": 0.99, "time_window_hours": 48.0}'

# Get markets
curl https://your-app.onrender.com/markets
```

### Using Python

```python
import requests

base_url = "https://your-app.onrender.com"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Manual scan
response = requests.post(
    f"{base_url}/scan",
    json={"min_prob": 0.92, "max_prob": 0.99, "time_window_hours": 48.0}
)
print(response.json())

# Get markets
response = requests.get(f"{base_url}/markets")
print(response.json())
```

## Environment Variables

### Required

- `POLYGON_WALLET_PRIVATE_KEY` - Your Polygon wallet private key
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional

- `ODDS_API_KEY` - For sports verification
- `NEWS_API_KEY` - For news verification
- `SLACK_WEBHOOK_URL` - For notifications
- `CLOB_API_KEY` - CLOB API key
- `CLOB_SECRET` - CLOB API secret
- `CLOB_PASS_PHRASE` - CLOB passphrase

### Configuration Overrides

You can override default settings with environment variables:

- `SCANNER_SCAN_INTERVAL_SECONDS=60`
- `SCANNER_MIN_PROBABILITY=0.92`
- `SCANNER_MAX_PROBABILITY=0.99`
- `POSITION_MAX_POSITION_SIZE_USD=1000.0`
- `RISK_MAX_SLIPPAGE_PERCENT=2.0`
- `TRADING_DRY_RUN_MODE=true`
- `TRADING_ENABLE_TRADING=false`

## Monitoring

### Logs

View logs in your platform's dashboard:
- **Render**: Dashboard → Your Service → Logs
- **Railway**: Dashboard → Your Service → Deployments → View Logs
- **Heroku**: `heroku logs --tail`

### Health Checks

The `/health` endpoint can be used for monitoring:
- Set up uptime monitoring (e.g., UptimeRobot)
- Configure health checks in your platform
- Monitor response times and errors

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure `PYTHONPATH=.` is set
   - Check that all dependencies are in `requirements.txt`

2. **Configuration errors**
   - Verify all required environment variables are set
   - Check that API keys are valid

3. **Port binding errors**
   - Ensure you're using `$PORT` environment variable
   - Check that the port is correctly configured

4. **Import errors**
   - Verify the project structure is correct
   - Check that all files are committed to git

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG
```

## Security Considerations

1. **Never commit `.env` file** - Use platform environment variables
2. **Use secrets management** - Store sensitive keys securely
3. **Enable HTTPS** - Most platforms provide this automatically
4. **Rate limiting** - Consider adding rate limiting for production
5. **Authentication** - Add API authentication for production use

## Cost Considerations

### Render
- Free tier: 750 hours/month
- Paid: $7/month for always-on service

### Railway
- Free tier: $5 credit/month
- Paid: Pay-as-you-go

### Heroku
- Free tier: Discontinued
- Paid: $7/month for hobby dyno

## Next Steps

1. **Deploy to Render** (or your chosen platform)
2. **Set environment variables**
3. **Test the API endpoints**
4. **Monitor logs and performance**
5. **Set up alerts** (Slack webhook)
6. **Configure continuous scanning** (POST /start)

## Support

If you encounter issues:
1. Check the logs in your platform dashboard
2. Verify environment variables are set correctly
3. Test locally first: `python agents/arbitrage_agent/api_server.py`
4. Check the API documentation at `/docs` (FastAPI auto-generated)

## Example Deployment Script

```bash
#!/bin/bash
# deploy.sh

echo "Deploying Polymarket Arbitrage Agent..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo "Deployment initiated!"
echo "Go to your platform dashboard to complete the deployment."
```

Happy deploying! 🚀
