"""
Comprehensive Configuration Module for Polymarket Arbitrage Agent

Provides type-safe configuration with validation, environment variable loading,
and singleton pattern for easy access throughout the application.
"""
import os
import re
from typing import List, Optional, Pattern, Tuple
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator, root_validator


# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


class ScannerConfig(BaseModel):
    """Configuration for market scanner"""
    
    scan_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Seconds between scans in continuous mode"
    )
    min_probability: float = Field(
        default=0.92,
        ge=0.0,
        le=1.0,
        description="Minimum probability threshold (0-1)"
    )
    max_probability: float = Field(
        default=0.99,
        ge=0.0,
        le=1.0,
        description="Maximum probability threshold (0-1)"
    )
    time_to_resolution_hours: int = Field(
        default=48,
        ge=1,
        le=168,
        description="Hours until resolution to consider (max 1 week)"
    )
    min_market_liquidity_usd: float = Field(
        default=5000.0,
        ge=0.0,
        description="Minimum market liquidity in USD"
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for API calls"
    )
    
    @root_validator
    def validate_probability_range(cls, values):
        """Ensure min_probability < max_probability"""
        min_prob = values.get('min_probability', 0.92)
        max_prob = values.get('max_probability', 0.99)
        if min_prob >= max_prob:
            raise ValueError(
                f"min_probability ({min_prob}) must be less than "
                f"max_probability ({max_prob})"
            )
        return values
    
    class Config:
        env_prefix = "SCANNER_"


class PositionConfig(BaseModel):
    """Configuration for position sizing and management"""
    
    max_position_size_usd: float = Field(
        default=1000.0,
        ge=1.0,
        description="Maximum position size per trade in USD"
    )
    max_total_exposure_usd: float = Field(
        default=10000.0,
        ge=1.0,
        description="Maximum total exposure across all positions in USD"
    )
    max_positions_per_category: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of positions per market category"
    )
    min_expected_roi_percent: float = Field(
        default=1.0,
        ge=0.0,
        le=100.0,
        description="Minimum expected ROI percentage to take a position"
    )
    position_size_multiplier: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Multiplier for position sizing (for testing/risk adjustment)"
    )
    
    @root_validator
    def validate_exposure(cls, values):
        """Ensure max_position_size <= max_total_exposure"""
        max_pos = values.get('max_position_size_usd', 1000.0)
        max_total = values.get('max_total_exposure_usd', 10000.0)
        if max_pos > max_total:
            raise ValueError(
                f"max_position_size_usd ({max_pos}) cannot exceed "
                f"max_total_exposure_usd ({max_total})"
            )
        return values
    
    class Config:
        env_prefix = "POSITION_"


class VerificationConfig(BaseModel):
    """Configuration for outcome verification"""
    
    min_verification_confidence: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for verification (0-1)"
    )
    min_source_agreement: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Minimum number of sources that must agree"
    )
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Timeout for verification API calls in seconds"
    )
    enable_sports_verification: bool = Field(
        default=True,
        description="Enable sports API verification"
    )
    enable_news_verification: bool = Field(
        default=True,
        description="Enable news API verification"
    )
    verification_retry_attempts: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Number of retry attempts for verification"
    )
    
    class Config:
        env_prefix = "VERIFICATION_"


class RiskConfig(BaseModel):
    """Configuration for risk management"""
    
    emergency_exit_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Probability threshold below which to exit positions"
    )
    max_slippage_percent: float = Field(
        default=2.0,
        ge=0.0,
        le=10.0,
        description="Maximum acceptable slippage percentage"
    )
    max_daily_loss_usd: float = Field(
        default=5000.0,
        ge=0.0,
        description="Maximum daily loss before stopping trading"
    )
    max_drawdown_percent: float = Field(
        default=20.0,
        ge=0.0,
        le=100.0,
        description="Maximum drawdown percentage before stopping"
    )
    stop_loss_percent: float = Field(
        default=5.0,
        ge=0.0,
        le=50.0,
        description="Stop loss percentage per position"
    )
    gas_price_multiplier: float = Field(
        default=1.2,
        ge=1.0,
        le=3.0,
        description="Multiplier for gas price (for faster execution)"
    )
    
    class Config:
        env_prefix = "RISK_"


class APIConfig(BaseModel):
    """Configuration for API keys and credentials"""
    
    polygon_wallet_private_key: str = Field(
        ...,
        min_length=64,
        description="Polygon wallet private key (required)"
    )
    openai_api_key: str = Field(
        ...,
        min_length=20,
        description="OpenAI API key (required)"
    )
    odds_api_key: Optional[str] = Field(
        default=None,
        description="Odds API key for sports verification (optional)"
    )
    news_api_key: Optional[str] = Field(
        default=None,
        description="News API key for news verification (optional)"
    )
    slack_webhook_url: Optional[str] = Field(
        default=None,
        description="Slack webhook URL for notifications (optional)"
    )
    clob_api_key: Optional[str] = Field(
        default=None,
        description="CLOB API key (optional, can be derived from wallet)"
    )
    clob_secret: Optional[str] = Field(
        default=None,
        description="CLOB API secret (optional)"
    )
    clob_passphrase: Optional[str] = Field(
        default=None,
        description="CLOB API passphrase (optional)"
    )
    
    @validator('polygon_wallet_private_key')
    def validate_private_key_format(cls, v):
        """Validate private key format (hex string)"""
        if not v.startswith('0x'):
            # Try adding 0x prefix
            if len(v) == 64:
                return '0x' + v
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError(
                "Private key must be a 64-character hex string (with or without 0x prefix)"
            )
        return v
    
    @validator('openai_api_key')
    def validate_openai_key_format(cls, v):
        """Validate OpenAI API key format"""
        if not v.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
        if len(v) < 20:
            raise ValueError("OpenAI API key appears to be invalid (too short)")
        return v
    
    @validator('slack_webhook_url', pre=True)
    def validate_slack_webhook(cls, v):
        """Validate Slack webhook URL format"""
        if v and not v.startswith('https://hooks.slack.com/'):
            raise ValueError("Slack webhook URL must start with 'https://hooks.slack.com/'")
        return v
    
    class Config:
        env_prefix = ""


class BlacklistConfig(BaseModel):
    """Configuration for market blacklist patterns"""
    
    # Question patterns to blacklist
    question_patterns: List[str] = Field(
        default_factory=lambda: [
            r".*test.*",
            r".*demo.*",
            r".*example.*",
            r".*scam.*",
            r".*fraud.*",
            r".*pump.*dump.*",
        ],
        description="Regex patterns to match against market questions"
    )
    
    # Description patterns to blacklist
    description_patterns: List[str] = Field(
        default_factory=lambda: [
            r".*test.*",
            r".*demo.*",
        ],
        description="Regex patterns to match against market descriptions"
    )
    
    # Category blacklist
    blacklisted_categories: List[str] = Field(
        default_factory=lambda: [],
        description="List of market categories to blacklist"
    )
    
    # Minimum market age (hours) - blacklist very new markets
    min_market_age_hours: int = Field(
        default=1,
        ge=0,
        description="Minimum market age in hours (blacklist newer markets)"
    )
    
    # Maximum spread to consider
    max_spread_percent: float = Field(
        default=10.0,
        ge=0.0,
        le=100.0,
        description="Maximum spread percentage to consider"
    )
    
    # Minimum volume requirement
    min_volume_24hr_usd: float = Field(
        default=100.0,
        ge=0.0,
        description="Minimum 24-hour volume in USD"
    )
    
    def is_blacklisted(self, question: str, description: str = "", category: str = "") -> Tuple[bool, str]:
        """
        Check if a market should be blacklisted.
        
        Args:
            question: Market question text
            description: Market description text
            category: Market category
            
        Returns:
            Tuple of (is_blacklisted: bool, reason: str)
        """
        question_lower = question.lower()
        description_lower = description.lower()
        category_lower = category.lower()
        
        # Check question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return True, f"Question matches blacklist pattern: {pattern}"
        
        # Check description patterns
        if description:
            for pattern in self.description_patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return True, f"Description matches blacklist pattern: {pattern}"
        
        # Check category blacklist
        if category and category_lower in [c.lower() for c in self.blacklisted_categories]:
            return True, f"Category '{category}' is blacklisted"
        
        return False, ""
    
    def compile_patterns(self) -> List[Pattern]:
        """Compile regex patterns for performance"""
        all_patterns = self.question_patterns + self.description_patterns
        return [re.compile(pattern, re.IGNORECASE) for pattern in all_patterns]
    
    class Config:
        env_prefix = "BLACKLIST_"


class TradingConfig(BaseModel):
    """Configuration for trading execution"""
    
    enable_trading: bool = Field(
        default=False,
        description="Enable actual trading (set to False for dry-run mode)"
    )
    dry_run_mode: bool = Field(
        default=True,
        description="Run in dry-run mode (no actual trades executed)"
    )
    min_confirmations: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Minimum blockchain confirmations required"
    )
    order_timeout_seconds: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Order timeout in seconds"
    )
    max_gas_price_gwei: float = Field(
        default=100.0,
        ge=1.0,
        description="Maximum gas price in Gwei"
    )
    
    class Config:
        env_prefix = "TRADING_"


class MainConfig(BaseModel):
    """Main configuration class combining all sub-configs"""
    
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    position: PositionConfig = Field(default_factory=PositionConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    api: APIConfig
    blacklist: BlacklistConfig = Field(default_factory=BlacklistConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    
    # Global settings
    log_level: str = Field(
        default="INFO",
        regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    environment: str = Field(
        default="development",
        regex="^(development|staging|production)$",
        description="Environment name"
    )
    
    @classmethod
    def from_env(cls) -> 'MainConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            MainConfig instance
            
        Raises:
            ConfigValidationError: If required environment variables are missing
        """
        # Load API config (required fields)
        try:
            api_config = APIConfig(
                polygon_wallet_private_key=os.getenv(
                    "POLYGON_WALLET_PRIVATE_KEY",
                    ""
                ),
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
                odds_api_key=os.getenv("ODDS_API_KEY"),
                news_api_key=os.getenv("NEWS_API_KEY"),
                slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
                clob_api_key=os.getenv("CLOB_API_KEY"),
                clob_secret=os.getenv("CLOB_SECRET"),
                clob_passphrase=os.getenv("CLOB_PASS_PHRASE"),
            )
        except Exception as e:
            missing_vars = []
            if not os.getenv("POLYGON_WALLET_PRIVATE_KEY"):
                missing_vars.append("POLYGON_WALLET_PRIVATE_KEY")
            if not os.getenv("OPENAI_API_KEY"):
                missing_vars.append("OPENAI_API_KEY")
            
            error_msg = (
                f"Configuration validation failed: {str(e)}\n\n"
                f"Required environment variables missing: {', '.join(missing_vars)}\n"
                f"Please set these in your .env file."
            )
            raise ConfigValidationError(error_msg) from e
        
        # Load other configs with environment variable overrides
        scanner_config = ScannerConfig(
            scan_interval_seconds=int(os.getenv("SCANNER_SCAN_INTERVAL_SECONDS", "60")),
            min_probability=float(os.getenv("SCANNER_MIN_PROBABILITY", "0.92")),
            max_probability=float(os.getenv("SCANNER_MAX_PROBABILITY", "0.99")),
            time_to_resolution_hours=int(os.getenv("SCANNER_TIME_TO_RESOLUTION_HOURS", "48")),
            min_market_liquidity_usd=float(os.getenv("SCANNER_MIN_MARKET_LIQUIDITY_USD", "5000.0")),
            max_retries=int(os.getenv("SCANNER_MAX_RETRIES", "3")),
        )
        
        position_config = PositionConfig(
            max_position_size_usd=float(os.getenv("POSITION_MAX_POSITION_SIZE_USD", "1000.0")),
            max_total_exposure_usd=float(os.getenv("POSITION_MAX_TOTAL_EXPOSURE_USD", "10000.0")),
            max_positions_per_category=int(os.getenv("POSITION_MAX_POSITIONS_PER_CATEGORY", "5")),
            min_expected_roi_percent=float(os.getenv("POSITION_MIN_EXPECTED_ROI_PERCENT", "1.0")),
            position_size_multiplier=float(os.getenv("POSITION_POSITION_SIZE_MULTIPLIER", "1.0")),
        )
        
        verification_config = VerificationConfig(
            min_verification_confidence=float(os.getenv("VERIFICATION_MIN_VERIFICATION_CONFIDENCE", "0.90")),
            min_source_agreement=int(os.getenv("VERIFICATION_MIN_SOURCE_AGREEMENT", "2")),
            timeout_seconds=int(os.getenv("VERIFICATION_TIMEOUT_SECONDS", "30")),
            enable_sports_verification=os.getenv("VERIFICATION_ENABLE_SPORTS_VERIFICATION", "true").lower() == "true",
            enable_news_verification=os.getenv("VERIFICATION_ENABLE_NEWS_VERIFICATION", "true").lower() == "true",
            verification_retry_attempts=int(os.getenv("VERIFICATION_VERIFICATION_RETRY_ATTEMPTS", "2")),
        )
        
        risk_config = RiskConfig(
            emergency_exit_threshold=float(os.getenv("RISK_EMERGENCY_EXIT_THRESHOLD", "0.85")),
            max_slippage_percent=float(os.getenv("RISK_MAX_SLIPPAGE_PERCENT", "2.0")),
            max_daily_loss_usd=float(os.getenv("RISK_MAX_DAILY_LOSS_USD", "5000.0")),
            max_drawdown_percent=float(os.getenv("RISK_MAX_DRAWDOWN_PERCENT", "20.0")),
            stop_loss_percent=float(os.getenv("RISK_STOP_LOSS_PERCENT", "5.0")),
            gas_price_multiplier=float(os.getenv("RISK_GAS_PRICE_MULTIPLIER", "1.2")),
        )
        
        blacklist_config = BlacklistConfig()
        
        trading_config = TradingConfig(
            enable_trading=os.getenv("TRADING_ENABLE_TRADING", "false").lower() == "true",
            dry_run_mode=os.getenv("TRADING_DRY_RUN_MODE", "true").lower() == "true",
            min_confirmations=int(os.getenv("TRADING_MIN_CONFIRMATIONS", "1")),
            order_timeout_seconds=int(os.getenv("TRADING_ORDER_TIMEOUT_SECONDS", "300")),
            max_gas_price_gwei=float(os.getenv("TRADING_MAX_GAS_PRICE_GWEI", "100.0")),
        )
        
        return cls(
            scanner=scanner_config,
            position=position_config,
            verification=verification_config,
            risk=risk_config,
            api=api_config,
            blacklist=blacklist_config,
            trading=trading_config,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            environment=os.getenv("ENVIRONMENT", "development"),
        )
    
    def reload(self) -> 'MainConfig':
        """Reload configuration from environment variables"""
        return self.from_env()
    
    def validate(self) -> bool:
        """
        Validate all configuration settings.
        
        Returns:
            True if valid
            
        Raises:
            ConfigValidationError: If validation fails
        """
        try:
            # Validate all sub-configs
            self.scanner.validate()
            self.position.validate()
            self.verification.validate()
            self.risk.validate()
            self.api.validate()
            self.blacklist.validate()
            self.trading.validate()
            
            # Additional cross-config validations
            if self.scanner.min_market_liquidity_usd < self.position.max_position_size_usd:
                raise ConfigValidationError(
                    f"Scanner min_market_liquidity_usd ({self.scanner.min_market_liquidity_usd}) "
                    f"should be >= position max_position_size_usd ({self.position.max_position_size_usd})"
                )
            
            return True
        except Exception as e:
            raise ConfigValidationError(f"Configuration validation failed: {str(e)}") from e


class ConfigSingleton:
    """Singleton pattern for global config access"""
    
    _instance: Optional[MainConfig] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                self._config = MainConfig.from_env()
                self._config.validate()
                self._initialized = True
            except ConfigValidationError as e:
                print(f"ERROR: {e}")
                raise
    
    @property
    def config(self) -> MainConfig:
        """Get the configuration instance"""
        if not self._initialized:
            self.__init__()
        return self._config
    
    def reload(self) -> MainConfig:
        """Reload configuration from environment"""
        self._config = MainConfig.from_env()
        self._config.validate()
        return self._config
    
    def get_scanner(self) -> ScannerConfig:
        """Get scanner configuration"""
        return self.config.scanner
    
    def get_position(self) -> PositionConfig:
        """Get position configuration"""
        return self.config.position
    
    def get_verification(self) -> VerificationConfig:
        """Get verification configuration"""
        return self.config.verification
    
    def get_risk(self) -> RiskConfig:
        """Get risk configuration"""
        return self.config.risk
    
    def get_api(self) -> APIConfig:
        """Get API configuration"""
        return self.config.api
    
    def get_blacklist(self) -> BlacklistConfig:
        """Get blacklist configuration"""
        return self.config.blacklist
    
    def get_trading(self) -> TradingConfig:
        """Get trading configuration"""
        return self.config.trading


# Global config instance (singleton)
_config_singleton = ConfigSingleton()

# Convenience accessor
def get_config() -> MainConfig:
    """Get the global configuration instance"""
    return _config_singleton.config

# For backward compatibility and easy access
config = _config_singleton.config


# Example usage and validation
if __name__ == "__main__":
    try:
        # Load and validate config
        cfg = get_config()
        
        print("=" * 60)
        print("Configuration Loaded Successfully")
        print("=" * 60)
        print(f"\nEnvironment: {cfg.environment}")
        print(f"Log Level: {cfg.log_level}")
        print(f"\nScanner Config:")
        print(f"  Scan Interval: {cfg.scanner.scan_interval_seconds}s")
        print(f"  Probability Range: {cfg.scanner.min_probability:.1%} - {cfg.scanner.max_probability:.1%}")
        print(f"  Time Window: {cfg.scanner.time_to_resolution_hours}h")
        print(f"  Min Liquidity: ${cfg.scanner.min_market_liquidity_usd:,.2f}")
        print(f"\nPosition Config:")
        print(f"  Max Position Size: ${cfg.position.max_position_size_usd:,.2f}")
        print(f"  Max Total Exposure: ${cfg.position.max_total_exposure_usd:,.2f}")
        print(f"  Max Positions/Category: {cfg.position.max_positions_per_category}")
        print(f"\nRisk Config:")
        print(f"  Emergency Exit: {cfg.risk.emergency_exit_threshold:.1%}")
        print(f"  Max Slippage: {cfg.risk.max_slippage_percent:.1f}%")
        print(f"  Max Daily Loss: ${cfg.risk.max_daily_loss_usd:,.2f}")
        print(f"\nTrading Config:")
        print(f"  Enable Trading: {cfg.trading.enable_trading}")
        print(f"  Dry Run Mode: {cfg.trading.dry_run_mode}")
        print(f"\nAPI Keys:")
        print(f"  Polygon Wallet: {'*' * 20} (set)")
        print(f"  OpenAI: {'*' * 20} (set)")
        print(f"  Odds API: {'set' if cfg.api.odds_api_key else 'not set'}")
        print(f"  News API: {'set' if cfg.api.news_api_key else 'not set'}")
        print(f"  Slack Webhook: {'set' if cfg.api.slack_webhook_url else 'not set'}")
        print("\n" + "=" * 60)
        print("✓ All configuration validated successfully!")
        print("=" * 60)
        
    except ConfigValidationError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
