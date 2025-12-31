"""
FastAPI Server for Polymarket Arbitrage Agent

Provides REST API endpoints for monitoring and controlling the arbitrage agent.
"""
import os
import sys
import threading
import time
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Try to import agent modules - make this more resilient
config = None
ConfigValidationError = None
MarketScanner = None
Dashboard = None
OutcomeVerifier = None
RiskManager = None
TradeExecutor = None

IMPORT_ERRORS = []

try:
    from agents.arbitrage_agent.config import config, ConfigValidationError
except ImportError as e:
    IMPORT_ERRORS.append(f"config: {e}")
    print(f"Warning: Could not import config: {e}")

try:
    from agents.arbitrage_agent.market_scanner import MarketScanner
except ImportError as e:
    IMPORT_ERRORS.append(f"market_scanner: {e}")
    print(f"Warning: Could not import MarketScanner: {e}")

try:
    from agents.arbitrage_agent.dashboard import Dashboard
except ImportError as e:
    IMPORT_ERRORS.append(f"dashboard: {e}")
    print(f"Warning: Could not import Dashboard: {e}")

try:
    from agents.arbitrage_agent.outcome_verifier import OutcomeVerifier
except ImportError as e:
    IMPORT_ERRORS.append(f"outcome_verifier: {e}")
    print(f"Warning: Could not import OutcomeVerifier: {e}")

try:
    from agents.arbitrage_agent.risk_manager import RiskManager
except ImportError as e:
    IMPORT_ERRORS.append(f"risk_manager: {e}")
    print(f"Warning: Could not import RiskManager: {e}")

try:
    from agents.arbitrage_agent.trade_executor import TradeExecutor
except ImportError as e:
    IMPORT_ERRORS.append(f"trade_executor: {e}")
    print(f"Warning: Could not import TradeExecutor: {e}")

app = FastAPI(
    title="Polymarket Arbitrage Agent API",
    description="API for monitoring and controlling the Polymarket arbitrage agent",
    version="1.0.0"
)

# Serve static files (dashboard)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
scanner: Optional[MarketScanner] = None if MarketScanner is None else None
dashboard: Optional[Dashboard] = None if Dashboard is None else None
scanner_thread: Optional[threading.Thread] = None
is_scanning: bool = False


class ScanRequest(BaseModel):
    """Request model for manual scan"""
    min_prob: float = 0.92
    max_prob: float = 0.99
    time_window_hours: float = 48.0


class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global scanner, dashboard
    
    if IMPORT_ERRORS:
        print(f"⚠ Running in limited mode due to import errors: {IMPORT_ERRORS}")
        return
    
    try:
        if config:
            if MarketScanner:
                scanner = MarketScanner(
                    scan_interval=config.scanner.scan_interval_seconds,
                    min_liquidity=config.scanner.min_market_liquidity_usd
                )
            if Dashboard:
                dashboard = Dashboard()
            print("✓ Arbitrage agent initialized successfully")
        else:
            print("⚠ Configuration not available - running in limited mode")
    except Exception as e:
        print(f"⚠ Error initializing agent: {e}")


@app.get("/")
async def root():
    """Root endpoint - serve dashboard or API info"""
    if IMPORT_ERRORS:
        return {
            "status": "error",
            "message": "Some modules failed to import",
            "import_errors": IMPORT_ERRORS,
            "available_endpoints": [
                "/health",
                "/status",
                "/import-errors"
            ],
            "help": "Check Vercel function logs for full error details. Some dependencies may be missing from api/requirements.txt"
        }
    
    return {
        "status": "ok",
        "message": "Polymarket Arbitrage Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "scan": "/scan",
            "start": "/start",
            "stop": "/stop",
            "markets": "/markets",
            "statistics": "/statistics"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "import_errors": len(IMPORT_ERRORS) if IMPORT_ERRORS else 0
    }


@app.get("/import-errors")
async def get_import_errors():
    """Get details about import errors"""
    return {
        "errors": IMPORT_ERRORS,
        "count": len(IMPORT_ERRORS),
        "modules_available": {
            "config": config is not None,
            "MarketScanner": MarketScanner is not None,
            "Dashboard": Dashboard is not None,
            "OutcomeVerifier": OutcomeVerifier is not None,
            "RiskManager": RiskManager is not None,
            "TradeExecutor": TradeExecutor is not None,
        }
    }


@app.get("/status")
async def get_status():
    """Get current agent status"""
    if not config:
        return {
            "status": "error",
            "message": "Configuration not available",
            "import_errors": IMPORT_ERRORS
        }
    
    return {
        "status": "running" if not IMPORT_ERRORS else "limited",
        "is_scanning": is_scanning,
        "config_loaded": config is not None,
        "scanner_initialized": scanner is not None,
        "dashboard_initialized": dashboard is not None,
        "import_errors": len(IMPORT_ERRORS) if IMPORT_ERRORS else 0,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/scan", response_model=StatusResponse)
async def scan_markets(request: ScanRequest):
    """Manually trigger a market scan"""
    if not scanner:
        raise HTTPException(
            status_code=503,
            detail=f"Scanner not available. Import errors: {IMPORT_ERRORS}"
        )
    
    try:
        markets = scanner.scan_markets(
            min_prob=request.min_prob,
            max_prob=request.max_prob,
            time_window_hours=request.time_window_hours
        )
        
        if dashboard:
            dashboard.log_scan(len(markets), len(markets))
        
        return StatusResponse(
            status="success",
            message=f"Found {len(markets)} qualifying markets",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/markets")
async def get_markets():
    """Get list of scanned markets"""
    if not scanner:
        return {
            "markets": [],
            "message": "Scanner not available",
            "import_errors": IMPORT_ERRORS
        }
    
    try:
        # Return empty list for now - implement actual market fetching
        return {
            "markets": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get markets: {str(e)}")


@app.get("/statistics")
async def get_statistics():
    """Get agent statistics"""
    stats = {
        "total_scans": 0,
        "markets_found": 0,
        "trades_executed": 0,
        "import_errors": IMPORT_ERRORS,
        "timestamp": datetime.now().isoformat()
    }
    
    if dashboard:
        try:
            # Get stats from dashboard if available
            pass
        except Exception:
            pass
    
    return stats


@app.post("/start")
async def start_scanning(background_tasks: BackgroundTasks):
    """Start continuous scanning"""
    if not scanner:
        raise HTTPException(
            status_code=503,
            detail=f"Scanner not available. Import errors: {IMPORT_ERRORS}"
        )
    
    global is_scanning, scanner_thread
    
    if is_scanning:
        return {"message": "Already scanning", "status": "scanning"}
    
    is_scanning = True
    
    def scan_loop():
        global is_scanning
        try:
            if scanner and config:
                scanner.run_continuous_scan(
                    min_prob=config.scanner.min_probability,
                    max_prob=config.scanner.max_probability,
                    time_window_hours=config.scanner.time_to_resolution_hours,
                    callback=lambda markets: dashboard.log_scan(len(markets), len(markets)) if dashboard else None
                )
        except Exception as e:
            print(f"Error in scan loop: {e}")
        finally:
            is_scanning = False
    
    scanner_thread = threading.Thread(target=scan_loop, daemon=True)
    scanner_thread.start()
    
    return {
        "status": "started",
        "message": "Continuous scanning started",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/stop")
async def stop_scanning():
    """Stop continuous scanning"""
    global is_scanning
    
    if not is_scanning:
        return {"message": "Not currently scanning", "status": "stopped"}
    
    is_scanning = False
    
    return {
        "status": "stopped",
        "message": "Scanning stopped",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/markets/{market_id}")
async def get_market_details(market_id: int):
    """Get details for a specific market"""
    if not scanner:
        raise HTTPException(
            status_code=503,
            detail=f"Scanner not available. Import errors: {IMPORT_ERRORS}"
        )
    
    try:
        market = scanner.get_market_details(market_id)
        return market
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
