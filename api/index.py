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

# Try to import FastAPI first (most critical dependency)
try:
    from fastapi import FastAPI
    FASTAPI_AVAILABLE = True
except ImportError as e:
    FASTAPI_AVAILABLE = False
    FASTAPI_ERROR = str(e)
    print(f"CRITICAL: FastAPI not available: {e}")
    print("This means dependencies are not being installed.")
    print("Check that api/requirements.txt exists and contains 'fastapi'")

# Try to import the main app
if FASTAPI_AVAILABLE:
    try:
        # Import the FastAPI app from the api_server module
        from agents.arbitrage_agent.api_server import app
        
        # Export the app for Vercel
        __all__ = ["app"]
        
    except ImportError as e:
        # If import fails, create a minimal error app
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
else:
    # FastAPI is not available - create a minimal handler that doesn't need FastAPI
    # This is a fallback that will at least show an error
    class MinimalApp:
        def __call__(self, environ, start_response):
            error_msg = f"""
            <html>
            <head><title>Dependencies Not Installed</title></head>
            <body>
                <h1>Error: Dependencies Not Installed</h1>
                <p><strong>FastAPI Error:</strong> {FASTAPI_ERROR}</p>
                <h2>Solution:</h2>
                <ol>
                    <li>Check that <code>api/requirements.txt</code> exists</li>
                    <li>Verify it contains <code>fastapi</code></li>
                    <li>Check Vercel build logs to see if dependencies are installing</li>
                    <li>In Vercel Dashboard → Settings → General, ensure Install Command is set correctly</li>
                </ol>
                <h2>Debug Info:</h2>
                <ul>
                    <li>PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}</li>
                    <li>Project Root: {project_root_str}</li>
                    <li>Python Path: {sys.path[:3]}</li>
                </ul>
            </body>
            </html>
            """
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            start_response(status, headers)
            return [error_msg.encode('utf-8')]
    
    # For Vercel, we still need to export 'app' as a FastAPI instance
    # So we'll create a simple one that shows the error
    try:
        # Try one more time with a simple import
        from fastapi import FastAPI as F
        app = F()
        @app.get("/")
        def error():
            return {
                "error": "Dependencies not installed",
                "fastapi_error": FASTAPI_ERROR,
                "solution": "Check that api/requirements.txt exists and contains fastapi. Check Vercel build logs."
            }
    except:
        # Last resort - this will fail but at least we tried
        raise ImportError(f"FastAPI is not available: {FASTAPI_ERROR}. Please ensure api/requirements.txt contains 'fastapi' and Vercel is installing dependencies.")
