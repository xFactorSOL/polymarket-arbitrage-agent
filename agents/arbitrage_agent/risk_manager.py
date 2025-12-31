"""
Risk Manager - Manages position sizing and risk limits
"""
from typing import Dict
from agents.arbitrage_agent.config import Config
from agents.polymarket.polymarket import Polymarket


class RiskManager:
    """Manages risk for arbitrage trades"""
    
    def __init__(self):
        self.config = Config()
        self.polymarket = Polymarket()
    
    def calculate_position_size(self, market: Dict, probability: float) -> float:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            market: Market dictionary
            probability: Current probability of winning outcome
            liquidity: Available liquidity
            
        Returns:
            Position size in USDC
        """
        # Base position size
        base_size = self.config.MAX_POSITION_SIZE
        
        # Adjust based on probability (higher probability = larger position)
        probability_multiplier = (probability - self.config.MIN_PROBABILITY) / (
            self.config.MAX_PROBABILITY - self.config.MIN_PROBABILITY
        )
        
        # Adjust based on liquidity
        liquidity = market.get("liquidity", 0)
        if liquidity < self.config.MIN_LIQUIDITY:
            return 0.0  # Insufficient liquidity
        
        liquidity_multiplier = min(1.0, liquidity / (self.config.MIN_LIQUIDITY * 2))
        
        # Calculate final position size
        position_size = base_size * probability_multiplier * liquidity_multiplier
        
        # Ensure we don't exceed max position size
        position_size = min(position_size, self.config.MAX_POSITION_SIZE)
        
        # Ensure minimum viable position
        if position_size < 10.0:
            return 0.0
        
        return round(position_size, 2)
    
    def check_risk_limits(self, market: Dict, position_size: float) -> Dict:
        """
        Check if trade meets risk limits
        
        Args:
            market: Market dictionary
            position_size: Proposed position size
            
        Returns:
            Dictionary with risk check results
        """
        checks = {
            "approved": True,
            "reasons": []
        }
        
        # Check liquidity
        liquidity = market.get("liquidity", 0)
        if liquidity < self.config.MIN_LIQUIDITY:
            checks["approved"] = False
            checks["reasons"].append(f"Insufficient liquidity: {liquidity} < {self.config.MIN_LIQUIDITY}")
        
        # Check position size
        if position_size > self.config.MAX_POSITION_SIZE:
            checks["approved"] = False
            checks["reasons"].append(f"Position size too large: {position_size} > {self.config.MAX_POSITION_SIZE}")
        
        # Check wallet balance
        try:
            balance = self.polymarket.get_usdc_balance()
            if balance < position_size * 1.1:  # 10% buffer for gas
                checks["approved"] = False
                checks["reasons"].append(f"Insufficient balance: {balance} < {position_size * 1.1}")
        except Exception as e:
            checks["approved"] = False
            checks["reasons"].append(f"Error checking balance: {e}")
        
        # Check spread
        spread = market.get("spread", 1.0)
        if spread > 0.05:  # 5% spread
            checks["approved"] = False
            checks["reasons"].append(f"Spread too wide: {spread} > 0.05")
        
        return checks
