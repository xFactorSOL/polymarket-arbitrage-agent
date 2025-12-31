"""
Dashboard - Monitor arbitrage agent performance
"""
from typing import List, Dict
from datetime import datetime
import json


class Dashboard:
    """Dashboard for monitoring arbitrage agent"""
    
    def __init__(self):
        self.trades = []
        self.scans = []
    
    def log_scan(self, markets_found: int, near_resolved: int):
        """Log a market scan"""
        scan = {
            "timestamp": datetime.now().isoformat(),
            "markets_scanned": markets_found,
            "near_resolved_found": near_resolved
        }
        self.scans.append(scan)
        print(f"[SCAN] Found {near_resolved} near-resolved markets out of {markets_found} scanned")
    
    def log_trade(self, trade: Dict):
        """Log a trade execution"""
        trade["timestamp"] = datetime.now().isoformat()
        self.trades.append(trade)
        
        if trade.get("success"):
            print(f"[TRADE] Successfully executed trade: {trade.get('order_id')}")
        else:
            print(f"[TRADE] Failed: {trade.get('error')}")
    
    def get_statistics(self) -> Dict:
        """Get agent statistics"""
        total_trades = len(self.trades)
        successful_trades = sum(1 for t in self.trades if t.get("success"))
        total_volume = sum(t.get("position_size", 0) for t in self.trades)
        
        return {
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "success_rate": successful_trades / total_trades if total_trades > 0 else 0,
            "total_volume": total_volume,
            "total_scans": len(self.scans)
        }
    
    def print_summary(self):
        """Print summary of agent activity"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("ARBITRAGE AGENT SUMMARY")
        print("="*50)
        print(f"Total Scans: {stats['total_scans']}")
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Successful Trades: {stats['successful_trades']}")
        print(f"Success Rate: {stats['success_rate']:.2%}")
        print(f"Total Volume: ${stats['total_volume']:.2f}")
        print("="*50 + "\n")
