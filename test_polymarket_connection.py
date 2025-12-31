#!/usr/bin/env python3
"""
Test script to verify Polymarket API connection
Run this to test your setup before using the arbitrage agent
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def test_environment_variables():
    """Test that required environment variables are set"""
    print("=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)
    
    required_vars = {
        "POLYGON_WALLET_PRIVATE_KEY": os.getenv("POLYGON_WALLET_PRIVATE_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
    
    optional_vars = {
        "ODDS_API_KEY": os.getenv("ODDS_API_KEY"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
    }
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            print(f"✓ {var}: {'*' * 20} (set)")
        else:
            print(f"✗ {var}: NOT SET")
            all_set = False
    
    print("\nOptional variables:")
    for var, value in optional_vars.items():
        if value:
            print(f"✓ {var}: {'*' * 20} (set)")
        else:
            print(f"○ {var}: not set (optional)")
    
    print()
    return all_set


def test_polymarket_connection():
    """Test Polymarket API connection"""
    print("=" * 60)
    print("Testing Polymarket API Connection")
    print("=" * 60)
    
    try:
        from agents.polymarket.polymarket import Polymarket
        
        print("Initializing Polymarket client...")
        pm = Polymarket()
        
        print("✓ Polymarket client initialized")
        
        # Test getting markets
        print("\nFetching markets...")
        markets = pm.get_all_markets()
        print(f"✓ Successfully fetched {len(markets)} markets")
        
        if markets:
            # Show first market as example
            first_market = markets[0]
            print(f"\nExample market:")
            print(f"  ID: {first_market.id}")
            print(f"  Question: {first_market.question[:80]}...")
            print(f"  Active: {first_market.active}")
            print(f"  Spread: {first_market.spread}")
        
        # Test getting wallet address
        print("\nTesting wallet connection...")
        if pm.private_key:
            address = pm.get_address_for_private_key()
            print(f"✓ Wallet address: {address}")
            
            # Test getting balance
            try:
                balance = pm.get_usdc_balance()
                print(f"✓ USDC Balance: ${balance:.2f}")
            except Exception as e:
                print(f"⚠ Could not fetch balance: {e}")
                print("  (This is normal if wallet is not funded or on testnet)")
        else:
            print("⚠ POLYGON_WALLET_PRIVATE_KEY not set - skipping wallet tests")
        
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Polymarket: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gamma_api():
    """Test Gamma API connection"""
    print("\n" + "=" * 60)
    print("Testing Gamma API Connection")
    print("=" * 60)
    
    try:
        from agents.polymarket.gamma import GammaMarketClient
        
        print("Initializing Gamma client...")
        gamma = GammaMarketClient()
        
        print("Fetching markets from Gamma API...")
        markets = gamma.get_markets(querystring_params={"limit": 5})
        print(f"✓ Successfully fetched {len(markets)} markets from Gamma API")
        
        if markets:
            print(f"\nExample market from Gamma:")
            market = markets[0]
            if isinstance(market, dict):
                print(f"  ID: {market.get('id', 'N/A')}")
                print(f"  Question: {str(market.get('question', 'N/A'))[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Gamma API: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arbitrage_agent_imports():
    """Test that arbitrage agent modules can be imported"""
    print("\n" + "=" * 60)
    print("Testing Arbitrage Agent Imports")
    print("=" * 60)
    
    modules = [
        "agents.arbitrage_agent.config",
        "agents.arbitrage_agent.market_scanner",
        "agents.arbitrage_agent.outcome_verifier",
        "agents.arbitrage_agent.risk_manager",
        "agents.arbitrage_agent.trade_executor",
        "agents.arbitrage_agent.dashboard",
        "agents.arbitrage_agent.utils",
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            all_imported = False
    
    return all_imported


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("POLYMARKET ARBITRAGE AGENT - CONNECTION TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test environment variables
    env_ok = test_environment_variables()
    results.append(("Environment Variables", env_ok))
    
    # Test Polymarket connection
    pm_ok = test_polymarket_connection()
    results.append(("Polymarket API", pm_ok))
    
    # Test Gamma API
    gamma_ok = test_gamma_api()
    results.append(("Gamma API", gamma_ok))
    
    # Test arbitrage agent imports
    agent_ok = test_arbitrage_agent_imports()
    results.append(("Arbitrage Agent", agent_ok))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Your setup is ready.")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        print("\nNote: Some failures may be expected:")
        print("  - Wallet balance test may fail if wallet is not funded")
        print("  - Environment variables need to be set in .env file")
    print("=" * 60)
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
