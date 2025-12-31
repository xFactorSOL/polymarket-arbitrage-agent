# Market Scanner Usage Guide

## Overview

The `MarketScanner` is a production-grade component that identifies arbitrage opportunities on Polymarket by scanning for markets that:
- Close within 48 hours (configurable)
- Have one outcome with 92-99% probability
- Have sufficient liquidity (default $5000 minimum)
- Are still open and active

## Quick Start

### Basic Usage

```python
from agents.arbitrage_agent.market_scanner import MarketScanner

# Initialize scanner
scanner = MarketScanner(
    scan_interval=60,      # Seconds between scans
    min_liquidity=5000.0,  # Minimum liquidity in USDC
)

# Run a single scan
markets = scanner.scan_markets(
    min_prob=0.92,
    max_prob=0.99,
    time_window_hours=48.0,
    limit=100  # Optional: limit number of markets to fetch
)

# Process results
for market in markets:
    print(f"Market: {market['question']}")
    print(f"Probability: {market['winning_probability']:.2%}")
    print(f"Liquidity: ${market['liquidity']:,.2f}")
    print(f"Hours until resolution: {market['hours_until_resolution']:.1f}")
```

### Continuous Scanning

```python
from agents.arbitrage_agent.market_scanner import MarketScanner

scanner = MarketScanner(scan_interval=60)

def on_opportunity_found(markets):
    """Callback when opportunities are found"""
    print(f"Found {len(markets)} opportunities!")
    for market in markets:
        # Process or trade on market
        pass

# Run continuous scan
scanner.run_continuous_scan(
    min_prob=0.92,
    max_prob=0.99,
    time_window_hours=48.0,
    callback=on_opportunity_found
)
```

## API Reference

### MarketScanner Class

#### `__init__(scan_interval=60, min_liquidity=5000.0, max_retries=3)`

Initialize the scanner.

**Parameters:**
- `scan_interval` (int): Seconds between scans in continuous mode
- `min_liquidity` (float): Minimum liquidity required in USDC
- `max_retries` (int): Maximum retry attempts for API calls

#### `scan_markets(min_prob=0.92, max_prob=0.99, time_window_hours=48.0, limit=None) -> List[Dict]`

Fetch all active markets and filter by criteria.

**Parameters:**
- `min_prob` (float): Minimum probability threshold (0-1)
- `max_prob` (float): Maximum probability threshold (0-1)
- `time_window_hours` (float): Hours until resolution to consider
- `limit` (int, optional): Maximum number of markets to fetch

**Returns:**
- `List[Dict]`: List of qualifying market dictionaries

**Example:**
```python
markets = scanner.scan_markets(
    min_prob=0.93,  # 93% minimum
    max_prob=0.98,  # 98% maximum
    time_window_hours=24.0,  # Next 24 hours only
    limit=50
)
```

#### `check_market_criteria(market, min_prob=0.92, max_prob=0.99, time_window_hours=48.0) -> Tuple[bool, str]`

Validate individual market against all criteria.

**Parameters:**
- `market` (Dict): Market dictionary from Gamma API
- `min_prob` (float): Minimum probability threshold
- `max_prob` (float): Maximum probability threshold
- `time_window_hours` (float): Hours until resolution

**Returns:**
- `Tuple[bool, str]`: (qualifies, reason)

**Example:**
```python
qualifies, reason = scanner.check_market_criteria(market_data)
if qualifies:
    print(f"Market qualifies: {reason}")
else:
    print(f"Market does not qualify: {reason}")
```

#### `get_market_details(market_id) -> Optional[Dict]`

Fetch comprehensive market data.

**Parameters:**
- `market_id` (int): Polymarket market ID

**Returns:**
- `Optional[Dict]`: Dictionary with market details or None if error

**Example:**
```python
details = scanner.get_market_details(12345)
if details:
    print(f"Question: {details['question']}")
    print(f"Category: {details['category']}")
    print(f"Liquidity: ${details['liquidity']:,.2f}")
```

#### `run_continuous_scan(min_prob=0.92, max_prob=0.99, time_window_hours=48.0, callback=None)`

Continuously scan for new opportunities.

**Parameters:**
- `min_prob` (float): Minimum probability threshold
- `max_prob` (float): Maximum probability threshold
- `time_window_hours` (float): Hours until resolution
- `callback` (callable, optional): Function to call when opportunities found
  - Signature: `callback(markets: List[MarketCandidate])`

**Example:**
```python
def process_opportunities(markets):
    for market in markets:
        # Your trading logic here
        pass

scanner.run_continuous_scan(callback=process_opportunities)
```

## MarketCandidate Model

The scanner returns `MarketCandidate` Pydantic models with the following fields:

```python
{
    "market_id": int,
    "question": str,
    "description": Optional[str],
    "outcomes": List[str],
    "outcome_prices": List[float],
    "winning_outcome_index": int,
    "winning_probability": float,
    "active": bool,
    "closed": bool,
    "funded": bool,
    "end_date": str,
    "hours_until_resolution": float,
    "liquidity": float,
    "volume": Optional[float],
    "spread": float,
    "category": MarketCategory,
    "is_qualified": bool,
    # ... and more
}
```

## Integration with Outcome Verifier

The scanner output is compatible with `outcome_verifier.py`:

```python
from agents.arbitrage_agent.market_scanner import MarketScanner
from agents.arbitrage_agent.outcome_verifier import OutcomeVerifier

scanner = MarketScanner()
verifier = OutcomeVerifier()

# Scan for markets
markets = scanner.scan_markets()

# Verify each market
for market in markets:
    verification = verifier.verify_outcome(market)
    if verification["verified"]:
        print(f"Market {market['market_id']} verified with {verification['confidence']:.0%} confidence")
```

## Error Handling

The scanner includes robust error handling:

- **Retry Logic**: Automatic retries with exponential backoff for API failures
- **Logging**: Comprehensive logging at INFO, WARNING, and ERROR levels
- **Graceful Degradation**: Continues scanning even if individual markets fail

**Example error handling:**
```python
try:
    markets = scanner.scan_markets()
except Exception as e:
    logger.error(f"Scan failed: {e}")
    # Handle error appropriately
```

## Configuration

Scanner settings can be configured in `config.py`:

```python
# Scanner Parameters
SCAN_INTERVAL = 60  # Seconds between scans
MIN_LIQUIDITY_SCANNER = 5000.0  # Minimum liquidity
TIME_WINDOW_HOURS = 48.0  # Hours until resolution
MAX_RETRIES = 3  # Maximum retry attempts
```

## Logging

The scanner uses Python's `logging` module. Configure logging level:

```python
import logging

# Set to DEBUG for verbose output
logging.getLogger('agents.arbitrage_agent.market_scanner').setLevel(logging.DEBUG)

# Set to WARNING to reduce output
logging.getLogger('agents.arbitrage_agent.market_scanner').setLevel(logging.WARNING)
```

## Performance Considerations

- **API Rate Limits**: The scanner respects API rate limits with retry logic
- **Batch Processing**: Markets are processed in batches to optimize performance
- **Caching**: Consider caching market data to reduce API calls

## Testing

Run unit tests:

```bash
python agents/arbitrage_agent/test_market_scanner.py
```

Or with pytest:

```bash
pytest agents/arbitrage_agent/test_market_scanner.py -v
```

## Example: Complete Workflow

```python
from agents.arbitrage_agent.market_scanner import MarketScanner
from agents.arbitrage_agent.outcome_verifier import OutcomeVerifier
from agents.arbitrage_agent.risk_manager import RiskManager
from agents.arbitrage_agent.trade_executor import TradeExecutor

# Initialize components
scanner = MarketScanner(min_liquidity=5000.0)
verifier = OutcomeVerifier()
risk_manager = RiskManager()
executor = TradeExecutor()

# Scan for opportunities
markets = scanner.scan_markets(
    min_prob=0.92,
    max_prob=0.99,
    time_window_hours=48.0
)

# Process each market
for market in markets:
    # Verify outcome
    verification = verifier.verify_outcome(market)
    if not verification["verified"]:
        continue
    
    # Check risk
    position_size = risk_manager.calculate_position_size(
        market, 
        market["winning_probability"]
    )
    risk_check = risk_manager.check_risk_limits(market, position_size)
    
    if risk_check["approved"]:
        # Execute trade
        result = executor.execute_trade(
            market,
            market["winning_outcome_index"],
            market["winning_probability"]
        )
        
        if result["success"]:
            print(f"Trade executed: {result['order_id']}")
```

## Troubleshooting

### No markets found
- Check that markets actually meet criteria (probability, time, liquidity)
- Verify API connection is working
- Check logs for errors

### API errors
- Verify API keys are set in `.env`
- Check network connectivity
- Review rate limiting

### Performance issues
- Reduce `limit` parameter
- Increase `scan_interval` for continuous scans
- Check API response times

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Review API documentation
3. Test with smaller limits first
