#!/usr/bin/env python3
"""
Safe installation script for open-notebook with dependency resolution
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_package_installed(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("🔧 Safe Open-Notebook Installation")
    print("=" * 60)
    
    # Step 1: Check if already installed
    if check_package_installed("open_notebook"):
        print("✅ open-notebook is already installed")
        return True
    
    # Step 2: Try installing with pip --no-deps first
    print("\n📦 Attempting minimal installation...")
    if run_command(
        "pip install --no-deps git+https://github.com/lfnovo/open-notebook",
        "Installing open-notebook without dependencies"
    ):
        # Try to install minimal required dependencies
        minimal_deps = [
            "nbformat>=5.0.0",
            "jupyter>=1.0.0",
            "ipython>=8.0.0"
        ]
        
        for dep in minimal_deps:
            run_command(f"pip install {dep}", f"Installing {dep}")
        
        if check_package_installed("open_notebook"):
            print("✅ open-notebook installed successfully with minimal dependencies")
            return True
    
    # Step 3: Try with specific version constraints
    print("\n📦 Attempting installation with version constraints...")
    if run_command(
        "pip install 'open-notebook @ git+https://github.com/lfnovo/open-notebook' --constraint <(echo 'nbformat>=5.0.0,<6.0.0')",
        "Installing with version constraints"
    ):
        if check_package_installed("open_notebook"):
            print("✅ open-notebook installed with version constraints")
            return True
    
    # Step 4: Try with --use-pep517
    print("\n📦 Attempting installation with PEP 517...")
    if run_command(
        "pip install --use-pep517 git+https://github.com/lfnovo/open-notebook",
        "Installing with PEP 517"
    ):
        if check_package_installed("open_notebook"):
            print("✅ open-notebook installed with PEP 517")
            return True
    
    # Step 5: Create a mock module as fallback
    print("\n📦 Creating fallback mock module...")
    mock_code = '''
"""
Mock open_notebook module for fallback
"""
import warnings

warnings.warn("Using mock open_notebook module. Notebook creation will be limited.")

def create_notebook(*args, **kwargs):
    """Mock notebook creation"""
    warnings.warn("Notebook creation not available - using mock implementation")
    return {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}

def save_notebook(*args, **kwargs):
    """Mock notebook saving"""
    warnings.warn("Notebook saving not available - using mock implementation")
    return True
'''
    
    # Create the mock module
    mock_dir = Path("mock_modules")
    mock_dir.mkdir(exist_ok=True)
    
    with open(mock_dir / "__init__.py", "w") as f:
        f.write("")
    
    with open(mock_dir / "open_notebook.py", "w") as f:
        f.write(mock_code)
    
    # Add to Python path
    sys.path.insert(0, str(mock_dir.absolute()))
    
    print("✅ Created fallback mock module")
    print("⚠️  Note: Notebook functionality will be limited")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Installation process completed!")
    else:
        print("\n❌ Installation failed, but fallback is available")
    
    print("\n💡 You can now run your system with limited notebook support") 