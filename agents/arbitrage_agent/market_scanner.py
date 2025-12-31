"""
Production-grade Market Scanner for Polymarket Arbitrage Agent

Identifies markets closing within a specified time window with high probability (92-99%)
on one outcome, with sufficient liquidity for trading.
"""
import ast
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from agents.polymarket.gamma import GammaMarketClient
from agents.polymarket.polymarket import Polymarket
from agents.utils.objects import Market, SimpleMarket
from agents.arbitrage_agent.config import Config
from agents.arbitrage_agent.utils import send_slack_notification


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketCategory(str, Enum):
    """Market category classification"""
    SPORTS = "sports"
    POLITICS = "politics"
    CRYPTO = "crypto"
    ENTERTAINMENT = "entertainment"
    ECONOMICS = "economics"
    OTHER = "other"


class MarketCandidate(BaseModel):
    """Pydantic model for qualifying market candidates"""
    
    # Market identification
    market_id: int = Field(..., description="Polymarket market ID")
    question: str = Field(..., description="Market question")
    description: Optional[str] = Field(None, description="Market description")
    
    # Outcomes and probabilities
    outcomes: List[str] = Field(..., description="List of outcome options")
    outcome_prices: List[float] = Field(..., description="Current prices for each outcome")
    winning_outcome_index: int = Field(..., description="Index of outcome with high probability")
    winning_probability: float = Field(..., description="Probability of winning outcome (0-1)")
    
    # Market status
    active: bool = Field(..., description="Whether market is currently active")
    closed: bool = Field(..., description="Whether market is closed")
    funded: bool = Field(..., description="Whether market is funded")
    
    # Timing
    end_date: str = Field(..., description="Market end date (ISO format)")
    end_date_iso: Optional[str] = Field(None, description="Market end date ISO")
    hours_until_resolution: float = Field(..., description="Hours until market resolution")
    time_window_qualifies: bool = Field(..., description="Whether within time window")
    
    # Trading metrics
    liquidity: float = Field(..., description="Total liquidity in USDC")
    liquidity_clob: Optional[float] = Field(None, description="CLOB liquidity")
    volume: Optional[float] = Field(None, description="Total volume")
    volume_24hr: Optional[float] = Field(None, description="24-hour volume")
    spread: float = Field(..., description="Current spread")
    
    # Market metadata
    category: MarketCategory = Field(MarketCategory.OTHER, description="Market category")
    tags: Optional[List[str]] = Field(None, description="Market tags")
    slug: Optional[str] = Field(None, description="Market slug")
    
    # Token information
    clob_token_ids: Optional[List[str]] = Field(None, description="CLOB token IDs for outcomes")
    condition_id: Optional[str] = Field(None, description="Condition ID")
    
    # Validation flags
    meets_liquidity_requirement: bool = Field(..., description="Meets minimum liquidity")
    meets_probability_requirement: bool = Field(..., description="Meets probability range")
    meets_time_requirement: bool = Field(..., description="Meets time window requirement")
    is_qualified: bool = Field(..., description="Overall qualification status")
    
    # Additional metadata
    resolution_source: Optional[str] = Field(None, description="Resolution source")
    created_at: Optional[str] = Field(None, description="Market creation date")
    
    @validator('winning_probability')
    def validate_probability(cls, v):
        """Ensure probability is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError(f"Probability must be between 0 and 1, got {v}")
        return v
    
    @validator('liquidity')
    def validate_liquidity(cls, v):
        """Ensure liquidity is non-negative"""
        if v < 0:
            raise ValueError(f"Liquidity must be non-negative, got {v}")
        return v


class MarketScanner:
    """
    Production-grade market scanner for identifying arbitrage opportunities.
    
    Scans Polymarket for markets that:
    - Close within a specified time window (default 48 hours)
    - Have one outcome with 92-99% probability
    - Have sufficient liquidity (default $5000 minimum)
    - Are still open and active
    """
    
    def __init__(
        self,
        scan_interval: int = 60,
        min_liquidity: float = 5000.0,
        max_retries: int = 3,
    ):
        """
        Initialize the MarketScanner.
        
        Args:
            scan_interval: Seconds between scans in continuous mode (default: 60)
            min_liquidity: Minimum liquidity required in USDC (default: 5000.0)
            max_retries: Maximum retry attempts for API calls (default: 3)
        """
        self.gamma_client = GammaMarketClient()
        self.polymarket = Polymarket()
        self.config = Config()
        self.scan_interval = scan_interval
        self.min_liquidity = min_liquidity
        self.max_retries = max_retries
        
        # Track scan statistics
        self.scan_count = 0
        self.last_scan_time: Optional[datetime] = None
        self.qualified_markets: List[MarketCandidate] = []
        
        logger.info(
            f"MarketScanner initialized with scan_interval={scan_interval}s, "
            f"min_liquidity=${min_liquidity:.2f}"
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.RequestError)),
        reraise=True,
    )
    def scan_markets(
        self,
        min_prob: float = 0.92,
        max_prob: float = 0.99,
        time_window_hours: float = 48.0,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Fetch all active markets and filter by criteria.
        
        Args:
            min_prob: Minimum probability threshold (default: 0.92)
            max_prob: Maximum probability threshold (default: 0.99)
            time_window_hours: Hours until resolution to consider (default: 48.0)
            limit: Maximum number of markets to fetch (None = all)
            
        Returns:
            List of dictionaries containing qualifying market data
        """
        logger.info(
            f"Starting market scan: min_prob={min_prob}, max_prob={max_prob}, "
            f"time_window={time_window_hours}h"
        )
        
        try:
            # Fetch markets from Gamma API
            params = {
                "active": True,
                "closed": False,
                "archived": False,
                "enableOrderBook": True,
            }
            
            if limit:
                params["limit"] = limit
            
            raw_markets = self.gamma_client.get_markets(
                querystring_params=params,
                parse_pydantic=False
            )
            
            logger.info(f"Fetched {len(raw_markets)} active markets from Gamma API")
            
            # Filter and process markets
            qualified_markets = []
            for market_data in raw_markets:
                try:
                    # Check if market meets criteria
                    qualifies, reason = self.check_market_criteria(
                        market_data,
                        min_prob=min_prob,
                        max_prob=max_prob,
                        time_window_hours=time_window_hours,
                    )
                    
                    if qualifies:
                        # Get comprehensive market details
                        market_details = self.get_market_details(market_data.get("id"))
                        if market_details:
                            qualified_markets.append(market_details)
                            logger.info(
                                f"Qualified market {market_data.get('id')}: "
                                f"{market_details.get('question', 'N/A')[:60]}..."
                            )
                    else:
                        logger.debug(
                            f"Market {market_data.get('id')} did not qualify: {reason}"
                        )
                        
                except Exception as e:
                    logger.warning(
                        f"Error processing market {market_data.get('id', 'unknown')}: {e}",
                        exc_info=True
                    )
                    continue
            
            self.scan_count += 1
            self.last_scan_time = datetime.now(timezone.utc)
            self.qualified_markets = [
                MarketCandidate(**m) for m in qualified_markets
            ]
            
            logger.info(
                f"Scan complete: {len(qualified_markets)} qualified markets found "
                f"out of {len(raw_markets)} total markets"
            )
            
            return qualified_markets
            
        except Exception as e:
            logger.error(f"Error during market scan: {e}", exc_info=True)
            raise
    
    def check_market_criteria(
        self,
        market: Dict,
        min_prob: float = 0.92,
        max_prob: float = 0.99,
        time_window_hours: float = 48.0,
    ) -> Tuple[bool, str]:
        """
        Validate individual market against all criteria.
        
        Args:
            market: Market dictionary from Gamma API
            min_prob: Minimum probability threshold
            max_prob: Maximum probability threshold
            time_window_hours: Hours until resolution to consider
            
        Returns:
            Tuple of (qualifies: bool, reason: str)
        """
        try:
            # Check if market is active and open
            if not market.get("active", False):
                return False, "Market is not active"
            
            if market.get("closed", False):
                return False, "Market is closed"
            
            if market.get("archived", False):
                return False, "Market is archived"
            
            # Check if market is funded
            if not market.get("funded", False):
                return False, "Market is not funded"
            
            # Parse outcome prices
            outcome_prices = market.get("outcomePrices", [])
            if isinstance(outcome_prices, str):
                outcome_prices = json.loads(outcome_prices)
            
            if not outcome_prices or len(outcome_prices) < 2:
                return False, "Invalid outcome prices"
            
            # Convert to floats
            try:
                prices = [float(p) for p in outcome_prices]
            except (ValueError, TypeError):
                return False, "Could not parse outcome prices"
            
            # Check if any outcome is in probability range
            max_price = max(prices)
            max_price_index = prices.index(max_price)
            
            if not (min_prob <= max_price <= max_prob):
                return False, f"Probability {max_price:.2%} outside range [{min_prob:.2%}, {max_prob:.2%}]"
            
            # Check time until resolution
            end_date_str = market.get("endDate") or market.get("endDateIso")
            if not end_date_str:
                return False, "No end date available"
            
            try:
                # Parse end date (handle both ISO and other formats)
                if "T" in end_date_str:
                    end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                else:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    end_date = end_date.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                time_diff = (end_date - now).total_seconds() / 3600  # Convert to hours
                
                if time_diff < 0:
                    return False, "Market has already ended"
                
                if time_diff > time_window_hours:
                    return False, f"Resolution too far: {time_diff:.1f}h > {time_window_hours}h"
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse end date '{end_date_str}': {e}")
                return False, f"Invalid end date format: {end_date_str}"
            
            # Check liquidity
            liquidity = market.get("liquidityClob") or market.get("liquidity")
            if liquidity is None:
                # Try to get from orderbook if available
                liquidity = 0.0  # Will be checked in get_market_details
            
            if liquidity and liquidity < self.min_liquidity:
                return False, f"Insufficient liquidity: ${liquidity:.2f} < ${self.min_liquidity:.2f}"
            
            # All checks passed
            return True, "All criteria met"
            
        except Exception as e:
            logger.error(f"Error checking market criteria: {e}", exc_info=True)
            return False, f"Error during validation: {str(e)}"
    
    def get_market_details(self, market_id: int) -> Optional[Dict]:
        """
        Fetch comprehensive market data.
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            Dictionary with comprehensive market data, or None if error
        """
        try:
            # Get market from Gamma API
            market_data = self.gamma_client.get_market(market_id)
            
            if not market_data:
                logger.warning(f"Market {market_id} not found")
                return None
            
            # Parse outcome prices and outcomes
            outcome_prices = market_data.get("outcomePrices", [])
            outcomes = market_data.get("outcome", [])
            
            if isinstance(outcome_prices, str):
                outcome_prices = json.loads(outcome_prices)
            if isinstance(outcomes, str):
                outcomes = json.loads(outcomes)
            
            if not outcome_prices or not outcomes:
                logger.warning(f"Market {market_id} has invalid outcomes")
                return None
            
            # Convert prices to floats
            prices = [float(p) for p in outcome_prices]
            
            # Find winning outcome (highest probability)
            max_price = max(prices)
            winning_index = prices.index(max_price)
            winning_prob = max_price
            
            # Calculate time until resolution
            end_date_str = market_data.get("endDate") or market_data.get("endDateIso")
            if end_date_str:
                try:
                    if "T" in end_date_str:
                        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                    else:
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                        end_date = end_date.replace(tzinfo=timezone.utc)
                    
                    now = datetime.now(timezone.utc)
                    hours_until = (end_date - now).total_seconds() / 3600
                except (ValueError, TypeError):
                    hours_until = None
            else:
                hours_until = None
            
            # Get liquidity
            liquidity = market_data.get("liquidityClob") or market_data.get("liquidity") or 0.0
            
            # If liquidity is low, try to get from orderbook
            if liquidity < self.min_liquidity and market_data.get("clobTokenIds"):
                try:
                    clob_token_ids = market_data.get("clobTokenIds")
                    if isinstance(clob_token_ids, str):
                        clob_token_ids = json.loads(clob_token_ids)
                    
                    if clob_token_ids and len(clob_token_ids) > winning_index:
                        token_id = clob_token_ids[winning_index]
                        orderbook = self.polymarket.get_orderbook(token_id)
                        liquidity = self._calculate_orderbook_liquidity(orderbook)
                except Exception as e:
                    logger.debug(f"Could not fetch orderbook liquidity: {e}")
            
            # Determine category
            category = self._categorize_market(market_data)
            
            # Build result dictionary
            result = {
                "market_id": market_id,
                "question": market_data.get("question", ""),
                "description": market_data.get("description"),
                "outcomes": outcomes,
                "outcome_prices": prices,
                "winning_outcome_index": winning_index,
                "winning_probability": winning_prob,
                "active": market_data.get("active", False),
                "closed": market_data.get("closed", False),
                "funded": market_data.get("funded", False),
                "end_date": end_date_str or "",
                "end_date_iso": market_data.get("endDateIso"),
                "hours_until_resolution": hours_until if hours_until is not None else 0.0,
                "time_window_qualifies": hours_until is not None and 0 < hours_until <= 48.0,
                "liquidity": liquidity,
                "liquidity_clob": market_data.get("liquidityClob"),
                "volume": market_data.get("volume") or market_data.get("volumeClob"),
                "volume_24hr": market_data.get("volume24hr") or market_data.get("volume24hrClob"),
                "spread": market_data.get("spread", 0.0),
                "category": category,
                "tags": [tag.get("slug") or tag.get("label") for tag in market_data.get("tags", []) if tag],
                "slug": market_data.get("slug"),
                "clob_token_ids": market_data.get("clobTokenIds"),
                "condition_id": market_data.get("conditionId"),
                "resolution_source": market_data.get("resolutionSource"),
                "created_at": market_data.get("createdAt"),
                "meets_liquidity_requirement": liquidity >= self.min_liquidity,
                "meets_probability_requirement": 0.92 <= winning_prob <= 0.99,
                "meets_time_requirement": hours_until is not None and 0 < hours_until <= 48.0,
                "is_qualified": (
                    liquidity >= self.min_liquidity and
                    0.92 <= winning_prob <= 0.99 and
                    hours_until is not None and
                    0 < hours_until <= 48.0
                ),
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting market details for {market_id}: {e}", exc_info=True)
            return None
    
    def _calculate_orderbook_liquidity(self, orderbook) -> float:
        """
        Calculate total liquidity from orderbook.
        
        Args:
            orderbook: OrderBookSummary object from Polymarket API
            
        Returns:
            Total liquidity in USDC
        """
        try:
            total_liquidity = 0.0
            
            # Sum bids (buy orders)
            if hasattr(orderbook, 'bids') and orderbook.bids:
                for bid in orderbook.bids:
                    price = float(bid.price) if hasattr(bid, 'price') else 0.0
                    size = float(bid.size) if hasattr(bid, 'size') else 0.0
                    total_liquidity += price * size
            
            # Sum asks (sell orders)
            if hasattr(orderbook, 'asks') and orderbook.asks:
                for ask in orderbook.asks:
                    price = float(ask.price) if hasattr(ask, 'price') else 0.0
                    size = float(ask.size) if hasattr(ask, 'size') else 0.0
                    total_liquidity += price * size
            
            return total_liquidity
            
        except Exception as e:
            logger.warning(f"Error calculating orderbook liquidity: {e}")
            return 0.0
    
    def _categorize_market(self, market_data: Dict) -> MarketCategory:
        """
        Categorize market based on question, tags, and description.
        
        Args:
            market_data: Market dictionary from API
            
        Returns:
            MarketCategory enum value
        """
        question = (market_data.get("question", "") or "").lower()
        description = (market_data.get("description", "") or "").lower()
        tags = [tag.get("slug", "").lower() if isinstance(tag, dict) else str(tag).lower() 
                for tag in market_data.get("tags", [])]
        
        text = f"{question} {description} {' '.join(tags)}"
        
        # Sports keywords
        sports_keywords = ["sport", "game", "match", "team", "player", "nfl", "nba", "mlb", 
                          "nhl", "soccer", "football", "basketball", "baseball", "hockey",
                          "championship", "tournament", "playoff", "super bowl", "world cup"]
        if any(keyword in text for keyword in sports_keywords):
            return MarketCategory.SPORTS
        
        # Politics keywords
        politics_keywords = ["election", "president", "senate", "congress", "vote", "candidate",
                            "democrat", "republican", "trump", "biden", "political", "policy"]
        if any(keyword in text for keyword in politics_keywords):
            return MarketCategory.POLITICS
        
        # Crypto keywords
        crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency",
                          "blockchain", "defi", "nft", "token", "coin", "price", "market cap"]
        if any(keyword in text for keyword in crypto_keywords):
            return MarketCategory.CRYPTO
        
        # Economics keywords
        economics_keywords = ["gdp", "inflation", "unemployment", "fed", "federal reserve",
                             "interest rate", "economy", "economic", "recession", "gdp"]
        if any(keyword in text for keyword in economics_keywords):
            return MarketCategory.ECONOMICS
        
        # Entertainment keywords
        entertainment_keywords = ["movie", "film", "oscar", "grammy", "award", "celebrity",
                                "actor", "actress", "music", "album", "tv show", "television"]
        if any(keyword in text for keyword in entertainment_keywords):
            return MarketCategory.ENTERTAINMENT
        
        return MarketCategory.OTHER
    
    def run_continuous_scan(
        self,
        min_prob: float = 0.92,
        max_prob: float = 0.99,
        time_window_hours: float = 48.0,
        callback: Optional[callable] = None,
    ):
        """
        Continuously scan for new opportunities.
        
        Args:
            min_prob: Minimum probability threshold
            max_prob: Maximum probability threshold
            time_window_hours: Hours until resolution to consider
            callback: Optional callback function to call when opportunities are found
                     Signature: callback(markets: List[MarketCandidate])
        """
        logger.info(
            f"Starting continuous scan mode (interval: {self.scan_interval}s)"
        )
        
        try:
            while True:
                try:
                    # Perform scan
                    markets = self.scan_markets(
                        min_prob=min_prob,
                        max_prob=max_prob,
                        time_window_hours=time_window_hours,
                    )
                    
                    # Convert to MarketCandidate objects
                    candidates = [MarketCandidate(**m) for m in markets]
                    
                    # Log findings
                    if candidates:
                        logger.info(
                            f"Found {len(candidates)} qualified markets in scan #{self.scan_count}"
                        )
                        
                        # Send Slack notification if configured
                        if self.config.SLACK_WEBHOOK_URL:
                            message = (
                                f"🔍 Found {len(candidates)} arbitrage opportunities:\n"
                                + "\n".join([
                                    f"• {m.question[:60]}... ({m.winning_probability:.1%}, "
                                    f"${m.liquidity:,.0f} liquidity, {m.hours_until_resolution:.1f}h)"
                                    for m in candidates[:5]  # Limit to 5 in notification
                                ])
                            )
                            send_slack_notification(message)
                        
                        # Call callback if provided
                        if callback:
                            try:
                                callback(candidates)
                            except Exception as e:
                                logger.error(f"Error in callback: {e}", exc_info=True)
                    else:
                        logger.debug(f"No qualified markets found in scan #{self.scan_count}")
                    
                    # Wait before next scan
                    time.sleep(self.scan_interval)
                    
                except KeyboardInterrupt:
                    logger.info("Continuous scan interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in continuous scan: {e}", exc_info=True)
                    logger.info(f"Retrying in {self.scan_interval} seconds...")
                    time.sleep(self.scan_interval)
                    
        except Exception as e:
            logger.error(f"Fatal error in continuous scan: {e}", exc_info=True)
            raise


# Example usage and unit tests
if __name__ == "__main__":
    # Initialize scanner
    scanner = MarketScanner(scan_interval=60, min_liquidity=5000.0)
    
    # Single scan
    print("Running single scan...")
    markets = scanner.scan_markets(
        min_prob=0.92,
        max_prob=0.99,
        time_window_hours=48.0,
        limit=100
    )
    
    print(f"\nFound {len(markets)} qualified markets:")
    for market in markets[:5]:  # Show first 5
        print(f"\nMarket ID: {market['market_id']}")
        print(f"Question: {market['question'][:80]}...")
        print(f"Probability: {market['winning_probability']:.2%}")
        print(f"Liquidity: ${market['liquidity']:,.2f}")
        print(f"Hours until resolution: {market['hours_until_resolution']:.1f}")
        print(f"Category: {market['category']}")
    
    # Example: Run continuous scan (uncomment to use)
    # scanner.run_continuous_scan(
    #     min_prob=0.92,
    #     max_prob=0.99,
    #     time_window_hours=48.0,
    #     callback=lambda markets: print(f"Found {len(markets)} opportunities!")
    # )
