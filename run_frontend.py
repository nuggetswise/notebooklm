#!/usr/bin/env python3
"""
Streamlit Frontend Runner for Email RAG System
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit frontend"""
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🚀 Starting Email RAG Frontend...")
    print(f"📁 Working directory: {os.getcwd()}")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("🔗 Make sure the backend API is running on http://localhost:8001")
    print()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 