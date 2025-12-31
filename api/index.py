"""
Vercel entrypoint for Polymarket Arbitrage Agent API
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app from the api_server module
from agents.arbitrage_agent.api_server import app

# Export the app for Vercel
__all__ = ["app"]
