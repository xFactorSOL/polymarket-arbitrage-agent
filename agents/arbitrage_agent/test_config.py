"""
Unit tests and examples for Configuration Module

Run with: python agents/arbitrage_agent/test_config.py
Or: python -m pytest agents/arbitrage_agent/test_config.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.arbitrage_agent.config import (
    ConfigSingleton,
    MainConfig,
    ScannerConfig,
    PositionConfig,
    VerificationConfig,
    RiskConfig,
    APIConfig,
    BlacklistConfig,
    TradingConfig,
    ConfigValidationError,
    get_config,
    config,
)


def test_scanner_config():
    """Test ScannerConfig validation"""
    print("Testing ScannerConfig...")
    
    # Valid config
    scanner = ScannerConfig(
        scan_interval_seconds=60,
        min_probability=0.92,
        max_probability=0.99,
        time_to_resolution_hours=48,
        min_market_liquidity_usd=5000.0
    )
    assert scanner.scan_interval_seconds == 60
    assert scanner.min_probability == 0.92
    print("✓ ScannerConfig creation test passed")
    
    # Test validation - min_prob >= max_prob should fail
    try:
        invalid = ScannerConfig(min_probability=0.99, max_probability=0.92)
        assert False, "Should have raised validation error"
    except ValueError:
        print("✓ ScannerConfig validation test passed")


def test_position_config():
    """Test PositionConfig validation"""
    print("Testing PositionConfig...")
    
    position = PositionConfig(
        max_position_size_usd=1000.0,
        max_total_exposure_usd=10000.0,
        max_positions_per_category=5,
        min_expected_roi_percent=1.0
    )
    assert position.max_position_size_usd == 1000.0
    print("✓ PositionConfig creation test passed")
    
    # Test validation - max_position > max_total should fail
    try:
        invalid = PositionConfig(
            max_position_size_usd=20000.0,
            max_total_exposure_usd=10000.0
        )
        assert False, "Should have raised validation error"
    except ValueError:
        print("✓ PositionConfig validation test passed")


def test_api_config():
    """Test APIConfig validation"""
    print("Testing APIConfig...")
    
    # Test with valid keys
    api = APIConfig(
        polygon_wallet_private_key="0x" + "a" * 64,
        openai_api_key="sk-" + "a" * 20
    )
    assert api.polygon_wallet_private_key.startswith("0x")
    assert api.openai_api_key.startswith("sk-")
    print("✓ APIConfig creation test passed")
    
    # Test private key without 0x prefix (should auto-add)
    api2 = APIConfig(
        polygon_wallet_private_key="a" * 64,
        openai_api_key="sk-" + "a" * 20
    )
    assert api2.polygon_wallet_private_key.startswith("0x")
    print("✓ APIConfig private key normalization test passed")
    
    # Test invalid OpenAI key format
    try:
        invalid = APIConfig(
            polygon_wallet_private_key="0x" + "a" * 64,
            openai_api_key="invalid-key"
        )
        assert False, "Should have raised validation error"
    except ValueError:
        print("✓ APIConfig validation test passed")


def test_blacklist_config():
    """Test BlacklistConfig"""
    print("Testing BlacklistConfig...")
    
    blacklist = BlacklistConfig()
    
    # Test blacklist checking
    is_blacklisted, reason = blacklist.is_blacklisted(
        question="This is a test market",
        description="",
        category=""
    )
    assert is_blacklisted
    assert "test" in reason.lower()
    print("✓ BlacklistConfig pattern matching test passed")
    
    # Test non-blacklisted market
    is_blacklisted, _ = blacklist.is_blacklisted(
        question="Will Bitcoin reach $100k?",
        description="",
        category=""
    )
    assert not is_blacklisted
    print("✓ BlacklistConfig non-match test passed")


def test_config_singleton():
    """Test singleton pattern"""
    print("Testing ConfigSingleton...")
    
    # Get config instance
    cfg1 = get_config()
    cfg2 = get_config()
    
    # Should be the same instance
    assert cfg1 is cfg2
    print("✓ Singleton pattern test passed")
    
    # Test direct access
    assert config is cfg1
    print("✓ Direct config access test passed")


def test_config_access():
    """Test accessing config values"""
    print("Testing config access...")
    
    cfg = get_config()
    
    # Test accessing nested configs
    assert hasattr(cfg, 'scanner')
    assert hasattr(cfg, 'position')
    assert hasattr(cfg, 'verification')
    assert hasattr(cfg, 'risk')
    assert hasattr(cfg, 'api')
    assert hasattr(cfg, 'blacklist')
    assert hasattr(cfg, 'trading')
    
    print("✓ Config structure test passed")
    
    # Test accessing values
    assert isinstance(cfg.scanner.scan_interval_seconds, int)
    assert isinstance(cfg.position.max_position_size_usd, float)
    assert isinstance(cfg.api.polygon_wallet_private_key, str)
    
    print("✓ Config value access test passed")


def example_usage():
    """Example usage of the config module"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Config Usage")
    print("=" * 60)
    
    # Method 1: Direct access (recommended)
    from agents.arbitrage_agent.config import config
    
    print(f"\nScanner Config:")
    print(f"  Scan Interval: {config.scanner.scan_interval_seconds}s")
    print(f"  Min Probability: {config.scanner.min_probability:.1%}")
    print(f"  Max Probability: {config.scanner.max_probability:.1%}")
    print(f"  Time Window: {config.scanner.time_to_resolution_hours}h")
    print(f"  Min Liquidity: ${config.scanner.min_market_liquidity_usd:,.2f}")
    
    print(f"\nPosition Config:")
    print(f"  Max Position: ${config.position.max_position_size_usd:,.2f}")
    print(f"  Max Exposure: ${config.position.max_total_exposure_usd:,.2f}")
    print(f"  Max Per Category: {config.position.max_positions_per_category}")
    
    print(f"\nRisk Config:")
    print(f"  Emergency Exit: {config.risk.emergency_exit_threshold:.1%}")
    print(f"  Max Slippage: {config.risk.max_slippage_percent:.1f}%")
    print(f"  Max Daily Loss: ${config.risk.max_daily_loss_usd:,.2f}")
    
    print(f"\nTrading Config:")
    print(f"  Enable Trading: {config.trading.enable_trading}")
    print(f"  Dry Run Mode: {config.trading.dry_run_mode}")
    
    # Method 2: Using get_config() function
    cfg = get_config()
    print(f"\nEnvironment: {cfg.environment}")
    print(f"Log Level: {cfg.log_level}")
    
    # Method 3: Using singleton directly
    singleton = ConfigSingleton()
    scanner_cfg = singleton.get_scanner()
    print(f"\nScanner interval (via singleton): {scanner_cfg.scan_interval_seconds}s")
    
    # Example: Check if market is blacklisted
    is_blacklisted, reason = config.blacklist.is_blacklisted(
        question="This is a test market question?",
        description="Test description",
        category="other"
    )
    print(f"\nBlacklist Check:")
    print(f"  Is blacklisted: {is_blacklisted}")
    if is_blacklisted:
        print(f"  Reason: {reason}")


def example_environment_variables():
    """Show example environment variable usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Environment Variables")
    print("=" * 60)
    
    print("""
Required environment variables in .env file:

POLYGON_WALLET_PRIVATE_KEY=0x...
OPENAI_API_KEY=sk-...

Optional environment variables:

# Scanner settings
SCANNER_SCAN_INTERVAL_SECONDS=60
SCANNER_MIN_PROBABILITY=0.92
SCANNER_MAX_PROBABILITY=0.99
SCANNER_TIME_TO_RESOLUTION_HOURS=48
SCANNER_MIN_MARKET_LIQUIDITY_USD=5000.0

# Position settings
POSITION_MAX_POSITION_SIZE_USD=1000.0
POSITION_MAX_TOTAL_EXPOSURE_USD=10000.0
POSITION_MAX_POSITIONS_PER_CATEGORY=5
POSITION_MIN_EXPECTED_ROI_PERCENT=1.0

# Risk settings
RISK_EMERGENCY_EXIT_THRESHOLD=0.85
RISK_MAX_SLIPPAGE_PERCENT=2.0
RISK_MAX_DAILY_LOSS_USD=5000.0

# Trading settings
TRADING_ENABLE_TRADING=false
TRADING_DRY_RUN_MODE=true

# API keys (optional)
ODDS_API_KEY=...
NEWS_API_KEY=...
SLACK_WEBHOOK_URL=...
CLOB_API_KEY=...
CLOB_SECRET=...
CLOB_PASS_PHRASE=...

# Global settings
LOG_LEVEL=INFO
ENVIRONMENT=development
""")


if __name__ == "__main__":
    print("Running Configuration Module Tests")
    print("=" * 60)
    
    try:
        # Run unit tests
        test_scanner_config()
        test_position_config()
        test_api_config()
        test_blacklist_config()
        test_config_singleton()
        test_config_access()
        
        print("\n" + "=" * 60)
        print("All unit tests passed!")
        print("=" * 60)
        
        # Run examples
        example_usage()
        example_environment_variables()
        
    except ConfigValidationError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("\nRequired variables:")
        print("  - POLYGON_WALLET_PRIVATE_KEY")
        print("  - OPENAI_API_KEY")
        exit(1)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)
