"""
Unit tests and examples for MarketScanner

Run with: python -m pytest agents/arbitrage_agent/test_market_scanner.py
Or: python agents/arbitrage_agent/test_market_scanner.py
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.arbitrage_agent.market_scanner import MarketScanner, MarketCandidate, MarketCategory


def test_market_scanner_initialization():
    """Test MarketScanner initialization"""
    scanner = MarketScanner(scan_interval=30, min_liquidity=5000.0)
    assert scanner.scan_interval == 30
    assert scanner.min_liquidity == 5000.0
    assert scanner.scan_count == 0
    print("✓ MarketScanner initialization test passed")


def test_market_criteria_check():
    """Test market criteria checking"""
    scanner = MarketScanner()
    
    # Create a mock market that should qualify
    good_market = {
        "id": 12345,
        "active": True,
        "closed": False,
        "archived": False,
        "funded": True,
        "endDate": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "outcomePrices": [0.95, 0.05],  # 95% probability
        "liquidityClob": 10000.0,  # $10k liquidity
    }
    
    qualifies, reason = scanner.check_market_criteria(
        good_market,
        min_prob=0.92,
        max_prob=0.99,
        time_window_hours=48.0
    )
    
    assert qualifies, f"Good market should qualify: {reason}"
    print("✓ Market criteria check test passed")
    
    # Test market that should NOT qualify (too low probability)
    bad_market = {
        "id": 12346,
        "active": True,
        "closed": False,
        "archived": False,
        "funded": True,
        "endDate": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "outcomePrices": [0.85, 0.15],  # 85% probability (too low)
        "liquidityClob": 10000.0,
    }
    
    qualifies, reason = scanner.check_market_criteria(bad_market)
    assert not qualifies, "Market with low probability should not qualify"
    print("✓ Market criteria rejection test passed")


def test_market_categorization():
    """Test market categorization"""
    scanner = MarketScanner()
    
    # Test sports market
    sports_market = {
        "question": "Will the Lakers win the NBA championship?",
        "description": "NBA finals",
        "tags": [{"slug": "sports"}]
    }
    category = scanner._categorize_market(sports_market)
    assert category == MarketCategory.SPORTS, f"Expected SPORTS, got {category}"
    print("✓ Sports categorization test passed")
    
    # Test politics market
    politics_market = {
        "question": "Will Trump win the 2024 election?",
        "description": "Presidential election",
        "tags": []
    }
    category = scanner._categorize_market(politics_market)
    assert category == MarketCategory.POLITICS, f"Expected POLITICS, got {category}"
    print("✓ Politics categorization test passed")
    
    # Test crypto market
    crypto_market = {
        "question": "Will Bitcoin reach $100k?",
        "description": "Bitcoin price prediction",
        "tags": []
    }
    category = scanner._categorize_market(crypto_market)
    assert category == MarketCategory.CRYPTO, f"Expected CRYPTO, got {category}"
    print("✓ Crypto categorization test passed")


def test_market_candidate_model():
    """Test MarketCandidate Pydantic model"""
    candidate_data = {
        "market_id": 12345,
        "question": "Test market question?",
        "outcomes": ["Yes", "No"],
        "outcome_prices": [0.95, 0.05],
        "winning_outcome_index": 0,
        "winning_probability": 0.95,
        "active": True,
        "closed": False,
        "funded": True,
        "end_date": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "hours_until_resolution": 24.0,
        "time_window_qualifies": True,
        "liquidity": 10000.0,
        "spread": 0.02,
        "category": MarketCategory.OTHER,
        "meets_liquidity_requirement": True,
        "meets_probability_requirement": True,
        "meets_time_requirement": True,
        "is_qualified": True,
    }
    
    candidate = MarketCandidate(**candidate_data)
    assert candidate.market_id == 12345
    assert candidate.winning_probability == 0.95
    assert candidate.is_qualified
    print("✓ MarketCandidate model test passed")


def example_single_scan():
    """Example: Run a single scan"""
    print("\n" + "="*60)
    print("EXAMPLE: Single Market Scan")
    print("="*60)
    
    scanner = MarketScanner(scan_interval=60, min_liquidity=5000.0)
    
    try:
        markets = scanner.scan_markets(
            min_prob=0.92,
            max_prob=0.99,
            time_window_hours=48.0,
            limit=50  # Limit to 50 markets for testing
        )
        
        print(f"\nFound {len(markets)} qualified markets:")
        print("-" * 60)
        
        for i, market in enumerate(markets[:5], 1):  # Show first 5
            print(f"\n{i}. Market ID: {market['market_id']}")
            print(f"   Question: {market['question'][:70]}...")
            print(f"   Probability: {market['winning_probability']:.2%}")
            print(f"   Liquidity: ${market['liquidity']:,.2f}")
            print(f"   Hours until resolution: {market['hours_until_resolution']:.1f}")
            print(f"   Category: {market['category']}")
            print(f"   Qualified: {market['is_qualified']}")
        
        if len(markets) > 5:
            print(f"\n... and {len(markets) - 5} more markets")
            
    except Exception as e:
        print(f"Error during scan: {e}")
        import traceback
        traceback.print_exc()


def example_continuous_scan():
    """Example: Run continuous scan (commented out to avoid infinite loop)"""
    print("\n" + "="*60)
    print("EXAMPLE: Continuous Market Scan")
    print("="*60)
    print("This would run continuously. Uncomment to use:")
    print("""
    scanner = MarketScanner(scan_interval=60, min_liquidity=5000.0)
    
    def on_opportunity_found(markets):
        print(f"\\n🎯 Found {len(markets)} arbitrage opportunities!")
        for market in markets:
            print(f"  • {market.question[:60]}...")
            print(f"    Probability: {market.winning_probability:.1%}")
            print(f"    Liquidity: ${market.liquidity:,.0f}")
    
    scanner.run_continuous_scan(
        min_prob=0.92,
        max_prob=0.99,
        time_window_hours=48.0,
        callback=on_opportunity_found
    )
    """)


if __name__ == "__main__":
    print("Running MarketScanner Tests and Examples")
    print("="*60)
    
    # Run unit tests
    try:
        test_market_scanner_initialization()
        test_market_criteria_check()
        test_market_categorization()
        test_market_candidate_model()
        print("\n" + "="*60)
        print("All unit tests passed!")
        print("="*60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    # Run examples (uncomment to test with real API)
    # example_single_scan()
    # example_continuous_scan()
    
    print("\n" + "="*60)
    print("Tests complete!")
    print("="*60)
    print("\nTo test with real API, uncomment example_single_scan() above")
