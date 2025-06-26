#!/usr/bin/env python3
"""
Production deployment script for Render
Handles dependency installation and service startup
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description, check=True):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False, e.stderr

def install_dependencies():
    """Install dependencies in the correct order."""
    print("🚀 Starting production dependency installation...")
    
    # Step 1: Install core dependencies first
    core_deps = [
        "numpy==1.26.4",
        "pandas==2.2.2",
        "requests==2.32.4",
        "python-dotenv==1.1.1"
    ]
    
    for dep in core_deps:
        success, _ = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            return False
    
    # Step 2: Install ML/AI dependencies
    ml_deps = [
        "sentence-transformers==2.7.0",
        "faiss-cpu==1.11.0",
        "cohere==4.57",
        "openai==1.91.0",
        "google-generativeai==0.8.5"
    ]
    
    for dep in ml_deps:
        success, _ = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            return False
    
    # Step 3: Install LangChain ecosystem
    langchain_deps = [
        "langchain==0.0.354",
        "langchain-core==0.1.53",
        "langchain-community==0.0.38",
        "langchain-text-splitters==0.0.2",
        "langchain-openai==0.2.14"
    ]
    
    for dep in langchain_deps:
        success, _ = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            return False
    
    # Step 4: Install web framework and utilities
    web_deps = [
        "fastapi==0.115.13",
        "uvicorn[standard]==0.34.3",
        "pydantic==2.11.7",
        "streamlit==1.46.0"
    ]
    
    for dep in web_deps:
        success, _ = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            return False
    
    # Step 5: Install remaining dependencies
    remaining_deps = [
        "email-validator==2.2.0",
        "beautifulsoup4==4.13.4",
        "python-multipart==0.0.20",
        "PyMuPDF==1.26.1",
        "pytesseract==0.3.13",
        "Pillow==10.4.0",
        "pdfminer.six==20231228",
        "psutil==5.9.8",
        "tqdm==4.67.1"
    ]
    
    for dep in remaining_deps:
        success, _ = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            return False
    
    return True

def verify_installation():
    """Verify that all critical packages are installed correctly."""
    print("🔍 Verifying installation...")
    
    critical_imports = [
        "import numpy",
        "import pandas",
        "import fastapi",
        "import uvicorn",
        "import streamlit",
        "import sentence_transformers",
        "import faiss",
        "import cohere",
        "import openai"
    ]
    
    for import_stmt in critical_imports:
        success, _ = run_command(f"python -c '{import_stmt}'", f"Testing {import_stmt}")
        if not success:
            print(f"❌ Failed to import: {import_stmt}")
            return False
    
    print("✅ All critical imports successful!")
    return True

def start_services():
    """Start the appropriate service based on environment."""
    print("🚀 Starting services...")
    
    # Check if we're in a web service environment
    if os.getenv('RENDER'):
        # Render environment - start the API
        print("🌐 Starting FastAPI service for Render...")
        cmd = "uvicorn ingestion_api.main:app --host 0.0.0.0 --port $PORT"
    else:
        # Local development
        print("🏠 Starting services for local development...")
        cmd = "uvicorn ingestion_api.main:app --reload --host 0.0.0.0 --port 8001"
    
    print(f"Running: {cmd}")
    os.system(cmd)

def main():
    """Main deployment function."""
    print("🚀 EMAIL RAG SYSTEM - PRODUCTION DEPLOYMENT")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    print("🎉 Deployment successful! Starting services...")
    
    # Start services
    start_services()

if __name__ == "__main__":
    main() 