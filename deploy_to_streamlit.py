#!/usr/bin/env python3
"""
Deployment script for Streamlit Cloud
This script prepares the email RAG system for deployment on Streamlit Cloud
"""

import os
import shutil
import subprocess
from pathlib import Path

def create_streamlit_app():
    """Create a standalone Streamlit app for deployment"""
    
    # Create deployment directory
    deploy_dir = Path("streamlit_deployment")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy frontend app
    shutil.copy("frontend/app.py", deploy_dir / "app.py")
    
    # Copy requirements
    shutil.copy("frontend/requirements.txt", deploy_dir / "requirements.txt")
    
    # Copy data directory
    if os.path.exists("data"):
        shutil.copytree("data", deploy_dir / "data", dirs_exist_ok=True)
    
    # Copy backend modules
    backend_dirs = ["ingestion_api", "rag"]
    for dir_name in backend_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, deploy_dir / dir_name, dirs_exist_ok=True)
    
    # Copy environment template
    if os.path.exists("env.template"):
        shutil.copy("env.template", deploy_dir / ".env.template")
    
    # Create .streamlit directory and config
    streamlit_dir = deploy_dir / ".streamlit"
    streamlit_dir.mkdir(exist_ok=True)
    
    with open(streamlit_dir / "config.toml", "w") as f:
        f.write("""
[server]
maxUploadSize = 200
enableXsrfProtection = false
enableCORS = false

[browser]
gatherUsageStats = false
""")
    
    # Create README for deployment
    with open(deploy_dir / "README.md", "w") as f:
        f.write("""
# Email RAG Assistant - Streamlit Deployment

This is a standalone Streamlit app for the Email RAG Assistant.

## Setup

1. Upload this directory to Streamlit Cloud
2. Set the following environment variables in Streamlit Cloud:
   - `COHERE_API_KEY`: Your Cohere API key
   - `GMAIL_EMAIL`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: Your Gmail app password

## Features

- Email RAG system focused on substack.com emails
- Sender-based filtering
- Persona-aware responses
- Multi-pane notebook-style interface

## Data

The app uses a SQLite database stored in the `data/` directory.
""")
    
    print(f"✅ Created deployment package in: {deploy_dir}")
    print("📁 Files included:")
    for file_path in deploy_dir.rglob("*"):
        if file_path.is_file():
            print(f"  - {file_path.relative_to(deploy_dir)}")
    
    return deploy_dir

def main():
    print("🚀 Preparing Email RAG Assistant for Streamlit Cloud deployment...")
    
    deploy_dir = create_streamlit_app()
    
    print("\n📋 Next steps:")
    print("1. Go to https://share.streamlit.io/")
    print("2. Connect your GitHub repository")
    print("3. Set the app path to: streamlit_deployment/app.py")
    print("4. Add your environment variables:")
    print("   - COHERE_API_KEY")
    print("   - GMAIL_EMAIL") 
    print("   - GMAIL_APP_PASSWORD")
    print("5. Deploy!")
    
    print(f"\n📁 Your deployment files are ready in: {deploy_dir}")

if __name__ == "__main__":
    main() 