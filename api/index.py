"""
Vercel entrypoint for Polymarket Arbitrage Agent API
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH if not set
if 'PYTHONPATH' not in os.environ:
    os.environ['PYTHONPATH'] = str(project_root)

try:
    # Import the FastAPI app from the api_server module
    from agents.arbitrage_agent.api_server import app
    
    # Export the app for Vercel
    __all__ = ["app"]
    
except Exception as e:
    # Create a minimal app that shows the error for debugging
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Polymarket Arbitrage Agent - Error")
    
    error_message = str(e)
    error_type = type(e).__name__
    
    @app.get("/")
    async def error_root():
        return {
            "error": "Failed to load application",
            "error_type": error_type,
            "error_message": error_message,
            "pythonpath": os.environ.get('PYTHONPATH', 'not set'),
            "project_root": str(project_root),
            "sys_path": sys.path[:3],  # First 3 paths
            "help": "Check Vercel function logs for full traceback"
        }
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return {
            "error": "Failed to load application",
            "error_type": error_type,
            "error_message": error_message,
            "help": "Check Vercel function logs for full traceback"
        }
    
    # Print error to logs
    import traceback
    print(f"ERROR loading app: {error_type}: {error_message}")
    traceback.print_exc()
    
    __all__ = ["app"]
