"""
Vercel entrypoint for Polymarket Arbitrage Agent API
"""
import sys
import os
from pathlib import Path

# Get the project root (parent of api directory)
project_root = Path(__file__).parent.parent
project_root_str = str(project_root.absolute())

# Add project root to Python path
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = project_root_str

# CRITICAL: Try to import FastAPI first
# If this fails, dependencies aren't installed
try:
    from fastapi import FastAPI
    FASTAPI_AVAILABLE = True
except ImportError as e:
    FASTAPI_AVAILABLE = False
    FASTAPI_ERROR = str(e)
    print("=" * 80)
    print("CRITICAL ERROR: FastAPI is not installed!")
    print("=" * 80)
    print(f"Error: {e}")
    print("\nThis means Vercel did not install dependencies from api/requirements.txt")
    print("\nSOLUTION:")
    print("1. Go to Vercel Dashboard → Settings → General")
    print("2. Set 'Install Command' to: pip install -r api/requirements.txt")
    print("3. Redeploy")
    print("=" * 80)
    # Raise the error so Vercel shows it
    raise

# FastAPI is available, try to import the main app
try:
    from agents.arbitrage_agent.api_server import app
    __all__ = ["app"]
    
except ImportError as e:
    # Import failed - create error app
    import traceback
    
    app = FastAPI(title="Polymarket Arbitrage Agent - Import Error")
    
    # Print to logs
    print("=" * 80)
    print("IMPORT ERROR")
    print("=" * 80)
    traceback.print_exc()
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    print(f"Project Root: {project_root_str}")
    print(f"Python Path: {sys.path[:5]}")
    print("=" * 80)
    
    @app.get("/")
    async def error_root():
        return {
            "status": "error",
            "error_type": "ImportError",
            "error_message": str(e),
            "pythonpath": os.environ.get('PYTHONPATH', 'not set'),
            "project_root": project_root_str,
            "help": "Check Vercel function logs for full traceback"
        }
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return error_root()
    
    __all__ = ["app"]
    
except Exception as e:
    # Any other error
    import traceback
    
    app = FastAPI(title="Polymarket Arbitrage Agent - Error")
    
    error_type = type(e).__name__
    error_message = str(e)
    
    print(f"UNEXPECTED ERROR: {error_type}: {error_message}")
    traceback.print_exc()
    
    @app.get("/")
    async def error_root():
        return {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message,
            "help": "Check Vercel function logs"
        }
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return error_root()
    
    __all__ = ["app"]
