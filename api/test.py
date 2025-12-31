"""
Minimal test endpoint for Vercel
Use this to verify Vercel is working before loading the full app
"""
from fastapi import FastAPI

app = FastAPI(title="Vercel Test")

@app.get("/")
def test():
    return {
        "status": "ok",
        "message": "Vercel is working!",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
