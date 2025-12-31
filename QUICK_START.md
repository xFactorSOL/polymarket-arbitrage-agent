# Quick Start Guide - Polymarket Arbitrage Agent

## All Bash Commands

### 1. Navigate to Project Directory
```bash
cd /Users/fbetancourtjr/agents
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Activate virtual environment (Windows)
# .venv\Scripts\activate
```

### 3. Upgrade Pip
```bash
pip install --upgrade pip
```

### 4. Install Dependencies
```bash
# Install all dependencies (may have warnings about some packages)
pip install -r requirements.txt

# Note: If you get errors for py_clob_client or poly_eip712_structs,
# these require Python 3.9.10+. You may need to upgrade Python or
# install these packages separately.
```

### 5. Set Up Environment Variables
```bash
# The .env file has been created. Edit it with your actual values:
# nano .env
# or
# vim .env

# Required variables:
# POLYGON_WALLET_PRIVATE_KEY=your_private_key_here
# OPENAI_API_KEY=your_openai_key_here

# Optional variables:
# ODDS_API_KEY=your_odds_api_key_here
# NEWS_API_KEY=your_news_api_key_here
# SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

### 6. Set PYTHONPATH
```bash
# Required for imports to work correctly
export PYTHONPATH="."

# To make this permanent, add to your ~/.zshrc or ~/.bashrc:
# echo 'export PYTHONPATH="."' >> ~/.zshrc
```

### 7. Test Polymarket Connection
```bash
# Run the test script
python test_polymarket_connection.py
```

### 8. Verify Directory Structure
```bash
# Check that all files are created
ls -la agents/arbitrage_agent/

# Should show:
# __init__.py
# config.py
# dashboard.py
# market_scanner.py
# outcome_verifier.py
# risk_manager.py
# trade_executor.py
# utils.py
```

## Complete Setup Script

Here's a complete setup script you can run:

```bash
#!/bin/bash
# Complete setup script for Polymarket Arbitrage Agent

cd /Users/fbetancourtjr/agents

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH="."

# Run tests
echo "Running connection tests..."
python test_polymarket_connection.py

echo "Setup complete!"
echo "Don't forget to:"
echo "1. Edit .env file with your API keys"
echo "2. Fund your Polygon wallet with USDC"
echo "3. Test with small amounts first"
```

## Daily Usage Commands

### Activate Environment and Run Tests
```bash
cd /Users/fbetancourtjr/agents
source .venv/bin/activate
export PYTHONPATH="."
python test_polymarket_connection.py
```

### Run Arbitrage Agent (Example)
```bash
cd /Users/fbetancourtjr/agents
source .venv/bin/activate
export PYTHONPATH="."
python -c "
from agents.arbitrage_agent.market_scanner import MarketScanner
scanner = MarketScanner()
markets = scanner.scan_markets(limit=10)
print(f'Found {len(markets)} near-resolved markets')
"
```

## Troubleshooting Commands

### Check Python Version
```bash
python3 --version
# Should show Python 3.9.x
```

### Check Virtual Environment
```bash
which python
# Should show: /Users/fbetancourtjr/agents/.venv/bin/python
```

### Check Installed Packages
```bash
pip list | grep -E "(polymarket|clob|openai)"
```

### Reinstall Dependencies
```bash
pip install --force-reinstall -r requirements.txt
```

### Check Environment Variables
```bash
# Check if .env file exists
ls -la .env

# View .env file (be careful with private keys!)
cat .env
```

## Directory Structure Created

```
agents/
└── arbitrage_agent/
    ├── __init__.py
    ├── market_scanner.py
    ├── outcome_verifier.py
    ├── risk_manager.py
    ├── trade_executor.py
    ├── dashboard.py
    ├── config.py
    └── utils.py
```

## Files Created

- `.env` - Environment variables (edit with your keys)
- `test_polymarket_connection.py` - Test script
- `SETUP_GUIDE.md` - Detailed setup guide
- `QUICK_START.md` - This file

## Next Steps

1. **Edit `.env` file** with your actual API keys
2. **Run test script**: `python test_polymarket_connection.py`
3. **Fund your wallet** with USDC on Polygon
4. **Start small** - test with minimal amounts first
5. **Monitor trades** using the dashboard

## Important Notes

- **Python Version**: Some packages require Python 3.9.10+, but 3.9.6 should work for most functionality
- **Private Keys**: Never share or commit your `.env` file
- **Testing**: Always test with small amounts first
- **PYTHONPATH**: Must be set to "." for imports to work
