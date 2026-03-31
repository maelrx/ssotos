"""FastAPI application entry point - Uvicorn run this."""
from src.core.logging import configure_logging
from src.app import app

# Configure structured logging at startup
configure_logging()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
