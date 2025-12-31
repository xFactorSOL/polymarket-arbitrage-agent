"""
Alternative Vercel entrypoint - FastAPI app
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from agents.arbitrage_agent.api_server import app

# Vercel expects 'app' to be available
__all__ = ["app"]
