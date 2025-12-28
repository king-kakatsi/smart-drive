#!/usr/bin/env python3
"""
Development runner for Smart-Drive backend
"""
import os
import sys
import uvicorn

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


