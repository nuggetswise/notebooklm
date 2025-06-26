#!/usr/bin/env python3
"""
Aggressive fix for NumPy compatibility crisis.
Completely removes NumPy 2.x and reinstalls everything with NumPy 1.x.
"""

import subprocess
import sys
import os

def run_command(cmd, description, capture_output=True, check=True):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        if capture_output:
            print(f"✅ {description} completed successfully")
        return True, result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False, e.stderr if capture_output else None

def fix_numpy_crisis():
    """Fix the NumPy 2.x compatibility crisis."""
    print("🚨 CRITICAL: Fixing NumPy 2.x compatibility crisis...")
    
    # Step 1: Completely remove all problematic packages
    packages_to_remove = [
        "numpy", "pandas", "faiss-cpu", "scikit-learn", "scipy", 
        "matplotlib", "seaborn", "pytesseract", "sentence-transformers"
    ]
    
    print("🗑️ Removing all problematic packages...")
    for package in packages_to_remove:
        run_command(f"{sys.executable} -m pip uninstall -y {package}", f"Removing {package}", check=False)
    
    # Step 2: Install NumPy 1.x first
    print("📦 Installing NumPy 1.x...")
    success, _ = run_command(f"{sys.executable} -m pip install 'numpy<2.0'", "Installing NumPy 1.x")
    if not success:
        print("❌ Failed to install NumPy 1.x")
        return False
    
    # Step 3: Install compatible versions in correct order
    compatible_packages = [
        "scipy==1.7.3",
        "pandas==2.2.2", 
        "scikit-learn==1.0.2",
        "faiss-cpu==1.7.4",
        "sentence-transformers==2.2.2",
        "pytesseract==0.3.10"
    ]
    
    print("📦 Installing compatible packages...")
    for package in compatible_packages:
        success, _ = run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}")
        if not success:
            print(f"⚠️ Warning: Failed to install {package}")
    
    # Step 4: Verify NumPy version
    success, output = run_command(f"{sys.executable} -c 'import numpy; print(numpy.__version__)'", "Checking NumPy version")
    if success:
        print(f"✅ NumPy version: {output.strip()}")
    
    return True

def test_imports():
    """Test if all critical imports work."""
    print("🧪 Testing critical imports...")
    
    test_imports = [
        "import numpy",
        "import pandas", 
        "import faiss",
        "import sklearn",
        "from sentence_transformers import SentenceTransformer"
    ]
    
    for import_stmt in test_imports:
        success, _ = run_command(f"{sys.executable} -c '{import_stmt}'", f"Testing {import_stmt}")
        if not success:
            print(f"❌ Failed to import: {import_stmt}")
            return False
    
    print("✅ All critical imports successful!")
    return True

if __name__ == "__main__":
    print("🚨 NUMERIC COMPATIBILITY CRISIS FIX")
    print("=" * 50)
    
    # Fix NumPy crisis
    if fix_numpy_crisis():
        print("✅ NumPy crisis fixed!")
        
        # Test imports
        if test_imports():
            print("🎉 All systems operational!")
        else:
            print("⚠️ Some imports still failing")
    else:
        print("❌ Failed to fix NumPy crisis") 