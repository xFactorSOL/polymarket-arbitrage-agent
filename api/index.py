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

# Import FastAPI - this MUST work or nothing will work
try:
    from fastapi import FastAPI
except ImportError as e:
    # FastAPI is not available - this is a critical error
    error_msg = f"""
CRITICAL ERROR: FastAPI is not installed!

Error: {e}

This means Vercel did not install dependencies from api/requirements.txt

SOLUTION:
1. Go to Vercel Dashboard → Settings → General
2. Under "Build & Development Settings"
3. Set "Install Command" to: pip install -r api/requirements.txt
4. Save and redeploy

Current PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}
Project Root: {project_root_str}
"""
    print(error_msg)
    # Create a simple error response that doesn't need FastAPI
    # This will at least show something
    raise ImportError(error_msg) from e

# FastAPI is available, create app
app = FastAPI(title="Polymarket Arbitrage Agent API")

# Try to import the main app
try:
    from agents.arbitrage_agent.api_server import app as main_app
    # Use the main app
    app = main_app
    __all__ = ["app"]
    
except ImportError as e:
    # Main app import failed - create error handler
    import traceback
    
    print("=" * 80)
    print("IMPORT ERROR - Main App")
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
            "sys_path": sys.path[:5],
            "help": "Check Vercel function logs for full traceback. Make sure PYTHONPATH=. is set in environment variables."
        }
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": "Main app failed to import"}
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return error_root()
    
    __all__ = ["app"]
    
except Exception as e:
    # Any other error
    import traceback
    
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
            "help": "Check Vercel function logs for full traceback"
        }
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return error_root()
    
    __all__ = ["app"]
