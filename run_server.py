#!/usr/bin/env python
"""
Clinic CRM - API Server
Run this to start the FastAPI server for remote access
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name} API Server...")
    print(f"Mode: {settings.app_mode}")
    print(f"Docs: http://localhost:8000/docs")

    uvicorn.run(
        "app.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
