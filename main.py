#!/usr/bin/env python3
"""
Simple FastAPI application for testing Cloud Run deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Email RAG API - Simple Test",
    description="Simple test API for Cloud Run deployment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Email RAG API - Simple Test",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "GET /": "This endpoint",
            "GET /health": "Health check",
            "GET /test": "Simple test endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Simple health check passed"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {
        "message": "Test endpoint working!",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.getenv("PORT", 8080))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info"
    ) 