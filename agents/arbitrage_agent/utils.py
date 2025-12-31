"""
Utility functions for arbitrage agent
"""
from typing import Dict, List
import requests
from agents.arbitrage_agent.config import Config


def send_slack_notification(message: str, webhook_url: str = None):
    """
    Send notification to Slack webhook
    
    Args:
        message: Message to send
        webhook_url: Slack webhook URL (optional, uses config if not provided)
    """
    config = Config()
    webhook = webhook_url or config.SLACK_WEBHOOK_URL
    
    if not webhook:
        return
    
    try:
        payload = {"text": message}
        response = requests.post(webhook, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Slack notification: {e}")


def format_market_info(market: Dict) -> str:
    """
    Format market information for display
    
    Args:
        market: Market dictionary
        
    Returns:
        Formatted string
    """
    return f"""
Market ID: {market.get('market_id')}
Question: {market.get('question')}
Outcomes: {market.get('outcomes')}
Prices: {market.get('outcome_prices')}
Spread: {market.get('spread')}
Liquidity: ${market.get('liquidity', 0):.2f}
"""


def calculate_expected_value(market: Dict, probability: float, position_size: float) -> float:
    """
    Calculate expected value of a trade
    
    Args:
        market: Market dictionary
        probability: Probability of winning
        position_size: Position size in USDC
        
    Returns:
        Expected value in USDC
    """
    # If probability is 95%, expected value is 95% of position
    # But we need to account for fees and slippage
    expected_payout = position_size / probability
    fees = position_size * 0.01  # 1% fee estimate
    slippage = position_size * 0.01  # 1% slippage estimate
    
    expected_value = (expected_payout * probability) - position_size - fees - slippage
    return expected_value
