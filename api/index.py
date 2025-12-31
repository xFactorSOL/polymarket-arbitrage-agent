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

# Also add current directory
current_dir = str(Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = project_root_str

# Try to import with better error handling
try:
    # Import the FastAPI app from the api_server module
    from agents.arbitrage_agent.api_server import app
    
    # Export the app for Vercel
    __all__ = ["app"]
    
except ImportError as e:
    # If import fails, create a minimal error app
    from fastapi import FastAPI
    import traceback
    
    app = FastAPI(title="Polymarket Arbitrage Agent - Import Error")
    
    error_details = {
        "error": "ImportError",
        "message": str(e),
        "pythonpath": os.environ.get('PYTHONPATH', 'not set'),
        "project_root": project_root_str,
        "sys_path": sys.path[:5],  # First 5 paths
    }
    
    # Print full traceback to logs
    print("=" * 60)
    print("IMPORT ERROR DETAILS")
    print("=" * 60)
    traceback.print_exc()
    print("=" * 60)
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    print(f"Project Root: {project_root_str}")
    print(f"Sys Path: {sys.path[:5]}")
    print("=" * 60)
    
    @app.get("/")
    async def error_root():
        return {
            "status": "error",
            "error_type": "ImportError",
            "error_message": str(e),
            "details": error_details,
            "help": "Check Vercel function logs for full traceback. Common issues: missing PYTHONPATH env var, missing dependencies, or import path issues."
        }
    
    @app.get("/{path:path}")
    async def error_catchall(path: str):
        return error_root()
    
    __all__ = ["app"]
    
except Exception as e:
    # Catch any other errors
    from fastapi import FastAPI
    import traceback
    
    app = FastAPI(title="Polymarket Arbitrage Agent - Error")
    
    error_type = type(e).__name__
    error_message = str(e)
    
    # Print to logs
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
