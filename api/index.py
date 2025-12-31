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
# If this fails, we can't do anything - Vercel didn't install dependencies
try:
    from fastapi import FastAPI
    FASTAPI_AVAILABLE = True
except ImportError as e:
    FASTAPI_AVAILABLE = False
    FASTAPI_ERROR = str(e)
    
    # Print detailed error to logs
    print("=" * 80)
    print("CRITICAL ERROR: FastAPI is not installed!")
    print("=" * 80)
    print(f"Error: {e}")
    print(f"\nPYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    print(f"Project Root: {project_root_str}")
    print(f"Python Path: {sys.path[:5]}")
    print("\nThis means Vercel did not install dependencies from api/requirements.txt")
    print("\nSOLUTION:")
    print("1. Go to Vercel Dashboard → Settings → General")
    print("2. Under 'Build & Development Settings'")
    print("3. Set 'Install Command' to: pip install -r api/requirements.txt")
    print("4. Save and redeploy")
    print("=" * 80)
    
    # Create a minimal WSGI-compatible error handler that doesn't need FastAPI
    # This will at least return something to the user
    class MinimalErrorApp:
        def __call__(self, environ, start_response):
            error_response = {
                "status": "error",
                "error_type": "DependenciesNotInstalled",
                "error_message": "FastAPI is not installed. Dependencies were not installed during build.",
                "solution": "Go to Vercel Dashboard → Settings → General → Set Install Command to: pip install -r api/requirements.txt",
                "pythonpath": os.environ.get('PYTHONPATH', 'not set'),
                "project_root": project_root_str
            }
            
            import json
            response_body = json.dumps(error_response).encode('utf-8')
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [response_body]
    
    app = MinimalErrorApp()
    __all__ = ["app"]
    
    # Also raise the error so it shows in logs
    raise ImportError(f"FastAPI not installed: {e}. Install dependencies with: pip install -r api/requirements.txt")

# FastAPI is available, try to import the main app
if FASTAPI_AVAILABLE:
    try:
        from agents.arbitrage_agent.api_server import app
        __all__ = ["app"]
        
    except ImportError as e:
        # Import failed - create error app
        import traceback
        
        app = FastAPI(title="Polymarket Arbitrage Agent - Import Error")
        
        # Print to logs
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
                "help": "Check Vercel function logs for full traceback"
            }
        
        @app.get("/{path:path}")
        async def error_catchall(path: str):
            return error_root()
        
        __all__ = ["app"]
