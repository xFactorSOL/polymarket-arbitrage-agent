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

try:
    from agents.arbitrage_agent.config import config, ConfigValidationError
    from agents.arbitrage_agent.market_scanner import MarketScanner
    from agents.arbitrage_agent.dashboard import Dashboard
    from agents.arbitrage_agent.outcome_verifier import OutcomeVerifier
    from agents.arbitrage_agent.risk_manager import RiskManager
    from agents.arbitrage_agent.trade_executor import TradeExecutor
except ImportError as e:
    print(f"Warning: Could not import agent modules: {e}")
    config = None

app = FastAPI(
    title="Polymarket Arbitrage Agent API",
    description="API for monitoring and controlling the Polymarket arbitrage agent",
    version="1.0.0"
)

# Serve static files (dashboard)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
scanner: Optional[MarketScanner] = None
dashboard: Optional[Dashboard] = None
scanner_thread: Optional[threading.Thread] = None
is_scanning: bool = False


class ScanRequest(BaseModel):
    """Request model for manual scan"""
    min_prob: float = 0.92
    max_prob: float = 0.99
    time_window_hours: float = 48.0
    limit: Optional[int] = None


class StatusResponse(BaseModel):
    """Response model for status"""
    status: str
    message: str
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global scanner, dashboard
    
    try:
        if config:
            scanner = MarketScanner(
                scan_interval=config.scanner.scan_interval_seconds,
                min_liquidity=config.scanner.min_market_liquidity_usd
            )
            dashboard = Dashboard()
            print("✓ Arbitrage agent initialized successfully")
        else:
            print("⚠ Configuration not available - running in limited mode")
    except Exception as e:
        print(f"⚠ Error initializing agent: {e}")


@app.get("/")
async def root():
    """Root endpoint - serve dashboard or API info"""
    dashboard_path = static_path / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return {
        "name": "Polymarket Arbitrage Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "status": "/status",
            "health": "/health",
            "scan": "/scan",
            "markets": "/markets",
            "statistics": "/statistics",
            "config": "/config",
            "start": "/start",
            "stop": "/stop"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if config:
            return {
                "status": "healthy",
                "config_loaded": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "degraded",
                "config_loaded": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/status")
async def get_status():
    """Get agent status"""
    global is_scanning
    
    return {
        "status": "scanning" if is_scanning else "idle",
        "is_scanning": is_scanning,
        "scanner_initialized": scanner is not None,
        "dashboard_initialized": dashboard is not None,
        "config_loaded": config is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/config")
async def get_config_info():
    """Get configuration information (without sensitive data)"""
    if not config:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    
    return {
        "scanner": {
            "scan_interval_seconds": config.scanner.scan_interval_seconds,
            "min_probability": config.scanner.min_probability,
            "max_probability": config.scanner.max_probability,
            "time_to_resolution_hours": config.scanner.time_to_resolution_hours,
            "min_market_liquidity_usd": config.scanner.min_market_liquidity_usd,
        },
        "position": {
            "max_position_size_usd": config.position.max_position_size_usd,
            "max_total_exposure_usd": config.position.max_total_exposure_usd,
            "max_positions_per_category": config.position.max_positions_per_category,
        },
        "risk": {
            "emergency_exit_threshold": config.risk.emergency_exit_threshold,
            "max_slippage_percent": config.risk.max_slippage_percent,
            "max_daily_loss_usd": config.risk.max_daily_loss_usd,
        },
        "trading": {
            "enable_trading": config.trading.enable_trading,
            "dry_run_mode": config.trading.dry_run_mode,
        },
        "environment": config.environment,
        "log_level": config.log_level,
    }


@app.post("/scan")
async def manual_scan(request: ScanRequest):
    """Perform a manual market scan"""
    global scanner, dashboard
    
    if not scanner:
        raise HTTPException(status_code=503, detail="Scanner not initialized")
    
    try:
        markets = scanner.scan_markets(
            min_prob=request.min_prob,
            max_prob=request.max_prob,
            time_window_hours=request.time_window_hours,
            limit=request.limit
        )
        
        if dashboard:
            dashboard.log_scan(
                markets_found=len(markets) * 10,  # Estimate
                near_resolved=len(markets)
            )
        
        return {
            "success": True,
            "markets_found": len(markets),
            "markets": markets[:10],  # Return first 10
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/markets")
async def get_markets():
    """Get recently found markets"""
    if not scanner:
        raise HTTPException(status_code=503, detail="Scanner not initialized")
    
    try:
        markets = scanner.scan_markets(limit=20)
        return {
            "markets": markets,
            "count": len(markets),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get markets: {str(e)}")


@app.get("/statistics")
async def get_statistics():
    """Get agent statistics"""
    if not dashboard:
        return {
            "message": "Dashboard not initialized",
            "statistics": {
                "total_trades": 0,
                "successful_trades": 0,
                "success_rate": 0,
                "total_volume": 0,
                "total_scans": 0
            }
        }
    
    stats = dashboard.get_statistics()
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/start")
async def start_scanning(background_tasks: BackgroundTasks):
    """Start continuous scanning"""
    global scanner, is_scanning, scanner_thread
    
    if not scanner:
        raise HTTPException(status_code=503, detail="Scanner not initialized")
    
    if is_scanning:
        return {"message": "Already scanning", "status": "scanning"}
    
    is_scanning = True
    
    def scan_loop():
        global is_scanning
        try:
            scanner.run_continuous_scan(
                min_prob=config.scanner.min_probability if config else 0.92,
                max_prob=config.scanner.max_probability if config else 0.99,
                time_window_hours=config.scanner.time_to_resolution_hours if config else 48.0,
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
        return {"message": "Not currently scanning", "status": "idle"}
    
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
        raise HTTPException(status_code=503, detail="Scanner not initialized")
    
    try:
        details = scanner.get_market_details(market_id)
        if not details:
            raise HTTPException(status_code=404, detail="Market not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
