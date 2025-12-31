# Arbitrage Agent Setup Guide

This guide will help you set up the development environment for the Polymarket Arbitrage Agent.

## Prerequisites

- Python 3.9 (Note: Some packages require Python 3.9.10+, but 3.9.6 should work for most functionality)
- Git
- A Polymarket wallet with USDC for trading

## Setup Steps

### 1. Clone the Repository (Already Done)

The Polymarket agents repository is already cloned at `/Users/fbetancourtjr/agents`.

### 2. Set Up Virtual Environment

```bash
cd /Users/fbetancourtjr/agents
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

**Note:** Some packages (`py_clob_client`, `poly_eip712_structs`) require Python 3.9.10+. If you encounter installation errors, you may need to upgrade Python or install these packages separately.

```bash
# Install dependencies (may have warnings about some packages)
pip install --upgrade pip
pip install -r requirements.txt

# If you get errors for py_clob_client or poly_eip712_structs, try:
# pip install py_clob_client py_order_utils --no-deps
# Then install remaining dependencies
```

### 4. Configure Environment Variables

Edit the `.env` file in the project root:

```bash
# Required
POLYGON_WALLET_PRIVATE_KEY=your_private_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional but recommended
ODDS_API_KEY=your_odds_api_key_here
NEWS_API_KEY=your_news_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

**Important:** Never commit your `.env` file to version control!

### 5. Test the Connection

Run the test script to verify everything is set up correctly:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="."

# Run test script
python test_polymarket_connection.py
```

The test script will:
- Check environment variables
- Test Polymarket API connection
- Test Gamma API connection
- Verify arbitrage agent modules can be imported

### 6. Directory Structure

The arbitrage agent is located at:
```
agents/
└── arbitrage_agent/
    ├── __init__.py
    ├── market_scanner.py      # Scans for near-resolved markets
    ├── outcome_verifier.py   # Verifies outcomes using external APIs
    ├── risk_manager.py       # Manages position sizing and risk
    ├── trade_executor.py     # Executes trades
    ├── dashboard.py          # Monitoring and logging
    ├── config.py             # Configuration settings
    └── utils.py              # Utility functions
```

## Usage

### Basic Usage Example

```python
from agents.arbitrage_agent.market_scanner import MarketScanner
from agents.arbitrage_agent.config import Config

# Initialize scanner
scanner = MarketScanner()

# Scan for near-resolved markets (92-99% probability)
markets = scanner.scan_markets(limit=100)

# Get details for each market
for market in markets:
    details = scanner.get_market_details(market)
    print(f"Market: {details['question']}")
    print(f"Probability: {details['outcome_prices']}")
    print(f"Liquidity: ${details['liquidity']:.2f}")
```

### Running the Test Script

```bash
# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="."

# Run tests
python test_polymarket_connection.py
```

## Troubleshooting

### Python Version Issues

If you encounter errors about Python version requirements:
- Some packages require Python 3.9.10+
- Current Python version: 3.9.6
- Consider upgrading to Python 3.9.10+ or Python 3.10+

### Package Installation Issues

If `py_clob_client` or `poly_eip712_structs` fail to install:
- These packages may require Python 3.9.10+
- Try installing them separately or upgrade Python
- Check the Polymarket documentation for alternative installation methods

### API Connection Issues

If API connections fail:
- Verify your `POLYGON_WALLET_PRIVATE_KEY` is set correctly
- Check your internet connection
- Ensure you're not behind a firewall blocking API calls
- Verify the Polymarket API is accessible

### Import Errors

If you get import errors:
- Make sure `PYTHONPATH="."` is set
- Verify the virtual environment is activated
- Check that all dependencies are installed

## Next Steps

1. **Fund your wallet**: Load USDC into your Polygon wallet
2. **Test with small amounts**: Start with small position sizes
3. **Monitor performance**: Use the dashboard to track trades
4. **Adjust parameters**: Modify `config.py` to suit your risk tolerance

## Security Notes

- **Never share your private keys**
- **Use a dedicated wallet** for trading (not your main wallet)
- **Start with small amounts** to test the system
- **Monitor your trades** regularly
- **Keep your `.env` file secure** and never commit it

## Support

For issues with:
- **Polymarket API**: Check [Polymarket documentation](https://docs.polymarket.com)
- **Python setup**: Check Python version and virtual environment
- **Package installation**: Verify Python version compatibility

## License

This code is part of the Polymarket Agents repository and is subject to the MIT License.
