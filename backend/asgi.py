"""
ASGI Entry Point - FastAPI with Uvicorn
Production-ready async web server
"""

from app import create_app

# Create FastAPI application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn (development mode)
    uvicorn.run(
        "asgi:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
    )
