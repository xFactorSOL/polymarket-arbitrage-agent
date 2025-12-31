# Configuration Module Usage Guide

## Overview

The configuration module provides a comprehensive, type-safe configuration system for the Polymarket arbitrage agent using Pydantic models, environment variable loading, and a singleton pattern.

## Quick Start

### Basic Usage

```python
from agents.arbitrage_agent.config import config

# Access scanner config
scan_interval = config.scanner.scan_interval_seconds
min_prob = config.scanner.min_probability

# Access position config
max_position = config.position.max_position_size_usd
max_exposure = config.position.max_total_exposure_usd

# Access API keys
private_key = config.api.polygon_wallet_private_key
openai_key = config.api.openai_api_key

# Check if market is blacklisted
is_blacklisted, reason = config.blacklist.is_blacklisted(
    question="Market question?",
    description="Description",
    category="sports"
)
```

### Alternative Access Methods

```python
# Method 1: Direct import (recommended)
from agents.arbitrage_agent.config import config

# Method 2: Using get_config() function
from agents.arbitrage_agent.config import get_config
cfg = get_config()

# Method 3: Using singleton
from agents.arbitrage_agent.config import ConfigSingleton
singleton = ConfigSingleton()
scanner_cfg = singleton.get_scanner()
```

## Configuration Classes

### ScannerConfig

Scanner configuration settings:

```python
config.scanner.scan_interval_seconds          # Default: 60
config.scanner.min_probability                # Default: 0.92
config.scanner.max_probability                # Default: 0.99
config.scanner.time_to_resolution_hours       # Default: 48
config.scanner.min_market_liquidity_usd       # Default: 5000.0
config.scanner.max_retries                    # Default: 3
```

### PositionConfig

Position sizing and management:

```python
config.position.max_position_size_usd         # Default: 1000.0
config.position.max_total_exposure_usd        # Default: 10000.0
config.position.max_positions_per_category    # Default: 5
config.position.min_expected_roi_percent      # Default: 1.0
config.position.position_size_multiplier      # Default: 1.0
```

### VerificationConfig

Outcome verification settings:

```python
config.verification.min_verification_confidence    # Default: 0.90
config.verification.min_source_agreement           # Default: 2
config.verification.timeout_seconds               # Default: 30
config.verification.enable_sports_verification     # Default: True
config.verification.enable_news_verification      # Default: True
config.verification.verification_retry_attempts   # Default: 2
```

### RiskConfig

Risk management parameters:

```python
config.risk.emergency_exit_threshold          # Default: 0.85
config.risk.max_slippage_percent              # Default: 2.0
config.risk.max_daily_loss_usd                # Default: 5000.0
config.risk.max_drawdown_percent              # Default: 20.0
config.risk.stop_loss_percent                 # Default: 5.0
config.risk.gas_price_multiplier              # Default: 1.2
```

### APIConfig

API keys and credentials:

```python
config.api.polygon_wallet_private_key          # Required
config.api.openai_api_key                     # Required
config.api.odds_api_key                       # Optional
config.api.news_api_key                       # Optional
config.api.slack_webhook_url                  # Optional
config.api.clob_api_key                       # Optional
config.api.clob_secret                        # Optional
config.api.clob_passphrase                    # Optional
```

### BlacklistConfig

Market blacklist patterns:

```python
config.blacklist.question_patterns            # List of regex patterns
config.blacklist.description_patterns         # List of regex patterns
config.blacklist.blacklisted_categories       # List of categories
config.blacklist.min_market_age_hours         # Default: 1
config.blacklist.max_spread_percent           # Default: 10.0
config.blacklist.min_volume_24hr_usd           # Default: 100.0

# Check if market is blacklisted
is_blacklisted, reason = config.blacklist.is_blacklisted(
    question="Market question?",
    description="Description",
    category="sports"
)
```

### TradingConfig

Trading execution settings:

```python
config.trading.enable_trading                 # Default: False
config.trading.dry_run_mode                   # Default: True
config.trading.min_confirmations              # Default: 1
config.trading.order_timeout_seconds          # Default: 300
config.trading.max_gas_price_gwei             # Default: 100.0
```

## Environment Variables

### Required Variables

```bash
POLYGON_WALLET_PRIVATE_KEY=0x...
OPENAI_API_KEY=sk-...
```

### Optional Variables

#### Scanner Settings
```bash
SCANNER_SCAN_INTERVAL_SECONDS=60
SCANNER_MIN_PROBABILITY=0.92
SCANNER_MAX_PROBABILITY=0.99
SCANNER_TIME_TO_RESOLUTION_HOURS=48
SCANNER_MIN_MARKET_LIQUIDITY_USD=5000.0
SCANNER_MAX_RETRIES=3
```

#### Position Settings
```bash
POSITION_MAX_POSITION_SIZE_USD=1000.0
POSITION_MAX_TOTAL_EXPOSURE_USD=10000.0
POSITION_MAX_POSITIONS_PER_CATEGORY=5
POSITION_MIN_EXPECTED_ROI_PERCENT=1.0
POSITION_POSITION_SIZE_MULTIPLIER=1.0
```

#### Verification Settings
```bash
VERIFICATION_MIN_VERIFICATION_CONFIDENCE=0.90
VERIFICATION_MIN_SOURCE_AGREEMENT=2
VERIFICATION_TIMEOUT_SECONDS=30
VERIFICATION_ENABLE_SPORTS_VERIFICATION=true
VERIFICATION_ENABLE_NEWS_VERIFICATION=true
VERIFICATION_VERIFICATION_RETRY_ATTEMPTS=2
```

#### Risk Settings
```bash
RISK_EMERGENCY_EXIT_THRESHOLD=0.85
RISK_MAX_SLIPPAGE_PERCENT=2.0
RISK_MAX_DAILY_LOSS_USD=5000.0
RISK_MAX_DRAWDOWN_PERCENT=20.0
RISK_STOP_LOSS_PERCENT=5.0
RISK_GAS_PRICE_MULTIPLIER=1.2
```

#### Trading Settings
```bash
TRADING_ENABLE_TRADING=false
TRADING_DRY_RUN_MODE=true
TRADING_MIN_CONFIRMATIONS=1
TRADING_ORDER_TIMEOUT_SECONDS=300
TRADING_MAX_GAS_PRICE_GWEI=100.0
```

#### API Keys (Optional)
```bash
ODDS_API_KEY=...
NEWS_API_KEY=...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
CLOB_API_KEY=...
CLOB_SECRET=...
CLOB_PASS_PHRASE=...
```

#### Global Settings
```bash
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Validation

The configuration module includes comprehensive validation:

### Automatic Validation

- **Type checking**: All values are validated for correct types
- **Range validation**: Numeric values are checked against min/max bounds
- **Format validation**: API keys and URLs are validated for correct format
- **Cross-config validation**: Relationships between configs are validated

### Example Validation Errors

```python
# Invalid probability range
try:
    scanner = ScannerConfig(min_probability=0.99, max_probability=0.92)
except ValueError as e:
    print(f"Error: {e}")  # min_probability must be less than max_probability

# Invalid position size
try:
    position = PositionConfig(
        max_position_size_usd=20000.0,
        max_total_exposure_usd=10000.0
    )
except ValueError as e:
    print(f"Error: {e}")  # max_position_size_usd cannot exceed max_total_exposure_usd

# Missing required API key
try:
    api = APIConfig(
        polygon_wallet_private_key="",
        openai_api_key=""
    )
except ValueError as e:
    print(f"Error: {e}")  # Required fields missing
```

## Reloading Configuration

To reload configuration from environment variables:

```python
from agents.arbitrage_agent.config import ConfigSingleton

singleton = ConfigSingleton()
new_config = singleton.reload()
```

## Blacklist Patterns

### Default Patterns

The blacklist includes default patterns to filter out:
- Test/demo markets
- Scam/fraud markets
- Pump and dump schemes

### Customizing Blacklist

```python
# Add custom patterns
config.blacklist.question_patterns.append(r".*suspicious.*")
config.blacklist.blacklisted_categories.append("crypto-pump")

# Check if market is blacklisted
is_blacklisted, reason = config.blacklist.is_blacklisted(
    question="Will suspicious token pump?",
    description="",
    category="crypto-pump"
)
```

## Error Handling

### ConfigValidationError

Raised when configuration validation fails:

```python
from agents.arbitrage_agent.config import ConfigValidationError

try:
    cfg = get_config()
except ConfigValidationError as e:
    print(f"Configuration error: {e}")
    # Handle error appropriately
```

### Missing Environment Variables

If required environment variables are missing, a clear error message is provided:

```
Configuration validation failed: ...

Required environment variables missing: POLYGON_WALLET_PRIVATE_KEY, OPENAI_API_KEY
Please set these in your .env file.
```

## Examples

### Example 1: Using Config in Market Scanner

```python
from agents.arbitrage_agent.config import config
from agents.arbitrage_agent.market_scanner import MarketScanner

# Initialize scanner with config values
scanner = MarketScanner(
    scan_interval=config.scanner.scan_interval_seconds,
    min_liquidity=config.scanner.min_market_liquidity_usd
)

# Scan markets using config thresholds
markets = scanner.scan_markets(
    min_prob=config.scanner.min_probability,
    max_prob=config.scanner.max_probability,
    time_window_hours=config.scanner.time_to_resolution_hours
)
```

### Example 2: Using Config in Risk Manager

```python
from agents.arbitrage_agent.config import config

def check_risk_limits(market, position_size):
    # Use risk config
    if position_size > config.position.max_position_size_usd:
        return False, "Position size exceeds maximum"
    
    if market.get("spread", 0) > config.risk.max_slippage_percent:
        return False, "Spread exceeds maximum slippage"
    
    return True, "Risk limits OK"
```

### Example 3: Using Config in Trade Executor

```python
from agents.arbitrage_agent.config import config

def execute_trade(market, position_size):
    # Check if trading is enabled
    if not config.trading.enable_trading:
        return {"success": False, "error": "Trading is disabled"}
    
    # Check if in dry-run mode
    if config.trading.dry_run_mode:
        print(f"[DRY RUN] Would execute trade: ${position_size}")
        return {"success": True, "dry_run": True}
    
    # Execute actual trade
    # ...
```

## Testing

Run configuration tests:

```bash
python agents/arbitrage_agent/test_config.py
```

Or test the config module directly:

```bash
python agents/arbitrage_agent/config.py
```

## Best Practices

1. **Always use the singleton**: Import `config` directly rather than creating new instances
2. **Validate on startup**: The config is automatically validated when first accessed
3. **Use environment variables**: Keep sensitive data in `.env` file, not in code
4. **Check dry-run mode**: Always check `config.trading.dry_run_mode` before executing trades
5. **Use blacklist**: Check markets against blacklist before processing
6. **Reload for testing**: Use `reload()` to test different configurations

## Troubleshooting

### Configuration Not Loading

- Check that `.env` file exists in project root
- Verify required environment variables are set
- Check file permissions on `.env` file

### Validation Errors

- Review error message for specific validation failure
- Check that numeric values are within valid ranges
- Verify API key formats are correct

### Type Errors

- Ensure you're accessing nested configs correctly: `config.scanner.scan_interval_seconds`
- Use type hints for better IDE support

## Summary

The configuration module provides:
- ✅ Type-safe configuration with Pydantic
- ✅ Environment variable loading with validation
- ✅ Singleton pattern for easy access
- ✅ Comprehensive validation
- ✅ Blacklist pattern matching
- ✅ Clear error messages
- ✅ Reload capability

Use `from agents.arbitrage_agent.config import config` to access configuration throughout your application!
