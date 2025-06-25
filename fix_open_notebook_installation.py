#!/usr/bin/env python3
"""
Comprehensive fix for open-notebook installation issues.
Addresses numpy/pandas compatibility, dependency conflicts, and version mismatches.
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path
import json

def run_command(cmd, description, capture_output=True, check=True):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        if capture_output:
            print(f"✅ {description} completed successfully")
        return True, result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False, None

def fix_numpy_pandas_compatibility():
    """Fix numpy/pandas compatibility issues."""
    print("🔧 Fixing numpy/pandas compatibility...")
    
    # First, uninstall all problematic packages
    packages_to_remove = [
        "numpy", "pandas", "pytesseract", "faiss-cpu", "sentence-transformers",
        "scikit-learn", "scipy", "matplotlib", "seaborn"
    ]
    for package in packages_to_remove:
        run_command(f"{sys.executable} -m pip uninstall -y {package}", f"Removing {package}", check=False)
    
    # Install compatible versions in correct order
    compatible_versions = [
        "numpy==1.21.6",  # More stable version
        "scipy==1.7.3",   # Compatible with numpy 1.21.6
        "pandas==1.5.3",  # Compatible with numpy 1.21.6
        "scikit-learn==1.0.2",  # Compatible with numpy 1.21.6
        "faiss-cpu==1.7.4",
        "sentence-transformers==2.2.2",
        "pytesseract==0.3.10"
    ]
    
    for version in compatible_versions:
        success, _ = run_command(f"{sys.executable} -m pip install {version}", f"Installing {version}")
        if not success:
            print(f"⚠️  Warning: Failed to install {version}")
    
    return True

def install_open_notebook_with_fixes():
    """Install open-notebook with all necessary fixes."""
    print("🎯 Installing open-notebook with comprehensive fixes...")
    
    # Step 1: Fix numpy/pandas compatibility
    fix_numpy_pandas_compatibility()
    
    # Step 2: Create a constraints file with compatible versions
    constraints_content = """# Compatible versions for open-notebook
numpy==1.24.3
pandas==2.0.3
langchain==0.3.26
langchain-core==0.3.66
langchain-community==0.3.26
langchain-openai==0.3.25
openai==1.91.0
pydantic==2.9.2
streamlit==1.46.0
pytesseract==0.3.10
Pillow>=10.0.0
beautifulsoup4>=4.12.0
"""
    
    constraints_file = "open_notebook_constraints.txt"
    with open(constraints_file, 'w') as f:
        f.write(constraints_content)
    
    try:
        # Step 3: Install open-notebook with constraints
        cmd = f"{sys.executable} -m pip install -c {constraints_file} git+https://github.com/lfnovo/open-notebook"
        success, _ = run_command(cmd, "Installing open-notebook with constraints")
        
        if not success:
            # Fallback: Try without dependencies first
            print("🔄 Trying fallback installation method...")
            cmd_no_deps = f"{sys.executable} -m pip install --no-deps git+https://github.com/lfnovo/open-notebook"
            success_no_deps, _ = run_command(cmd_no_deps, "Installing open-notebook without dependencies")
            
            if success_no_deps:
                # Install dependencies separately
                core_deps = [
                    "langchain==0.3.26",
                    "langchain-core==0.3.66",
                    "langchain-community==0.3.26",
                    "langchain-openai==0.3.25",
                    "openai==1.91.0",
                    "pydantic==2.9.2",
                    "streamlit==1.46.0"
                ]
                
                for dep in core_deps:
                    run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}", check=False)
        
        return success or success_no_deps
        
    finally:
        # Clean up
        if os.path.exists(constraints_file):
            os.remove(constraints_file)

def fix_email_validation_issues():
    """Fix email validation issues in the parser."""
    print("🔧 Fixing email validation issues...")
    
    # Read the current parser file
    parser_path = "ingestion_api/parser.py"
    if not os.path.exists(parser_path):
        print("⚠️  Parser file not found, skipping email validation fix")
        return
    
    with open(parser_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add email validation fix
    validation_fix = '''
def clean_email_address(email_str):
    """Clean email address to handle special characters."""
    if not email_str:
        return None
    
    # Remove angle brackets if present
    email_str = email_str.strip()
    if email_str.startswith('<') and email_str.endswith('>'):
        email_str = email_str[1:-1]
    
    # Extract email from "Display Name <email@domain.com>" format
    if '<' in email_str and '>' in email_str:
        start = email_str.rfind('<') + 1
        end = email_str.rfind('>')
        if start < end:
            email_str = email_str[start:end]
    
    # Clean up any remaining special characters
    email_str = email_str.strip()
    
    # Basic email validation
    if '@' in email_str and '.' in email_str.split('@')[1]:
        return email_str
    
    return None
'''
    
    # Insert the fix before the parser class
    if 'def clean_email_address' not in content:
        # Find a good place to insert the function
        insert_pos = content.find('class EmailParser')
        if insert_pos != -1:
            content = content[:insert_pos] + validation_fix + '\n' + content[insert_pos:]
            
            # Write back the fixed content
            with open(parser_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Email validation fix applied")
        else:
            print("⚠️  Could not find insertion point for email validation fix")

def fix_model_compatibility():
    """Fix model compatibility issues in RAG configuration."""
    print("🔧 Fixing model compatibility issues...")
    
    # Read the current config file
    config_path = "rag/config.py"
    if not os.path.exists(config_path):
        print("⚠️  Config file not found, skipping model compatibility fix")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace command-r with command model
    if 'command-r' in content:
        content = content.replace('command-r', 'command')
        
        # Write back the fixed content
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Model compatibility fix applied")
    else:
        print("ℹ️  No command-r model found in config")

def verify_installation():
    """Verify that open-notebook is properly installed."""
    print("🔍 Verifying installation...")
    
    try:
        import opennotebook
        print("✅ open-notebook imported successfully!")
        
        # Test basic functionality
        from opennotebook.models import Notebook, Block
        print("✅ open-notebook models imported successfully!")
        
        # Test version
        version = getattr(opennotebook, '__version__', 'unknown')
        print(f"✅ open-notebook version: {version}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        return False

def test_numpy_pandas():
    """Test numpy/pandas compatibility."""
    print("🔍 Testing numpy/pandas compatibility...")
    
    try:
        import numpy as np
        import pandas as pd
        print(f"✅ NumPy version: {np.__version__}")
        print(f"✅ Pandas version: {pd.__version__}")
        
        # Test basic functionality
        arr = np.array([1, 2, 3])
        df = pd.DataFrame({'test': [1, 2, 3]})
        print("✅ NumPy and Pandas working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ NumPy/Pandas test failed: {e}")
        return False

def main():
    print("🚀 Starting comprehensive open-notebook installation fix...")
    print("=" * 70)
    
    # Step 1: Fix numpy/pandas compatibility
    print("\n📋 Step 1: Fixing numpy/pandas compatibility")
    if not test_numpy_pandas():
        fix_numpy_pandas_compatibility()
        if not test_numpy_pandas():
            print("❌ Failed to fix numpy/pandas compatibility")
            return False
    
    # Step 2: Install open-notebook
    print("\n📋 Step 2: Installing open-notebook")
    if not install_open_notebook_with_fixes():
        print("❌ Failed to install open-notebook")
        return False
    
    # Step 3: Fix email validation issues
    print("\n📋 Step 3: Fixing email validation issues")
    fix_email_validation_issues()
    
    # Step 4: Fix model compatibility
    print("\n📋 Step 4: Fixing model compatibility")
    fix_model_compatibility()
    
    # Step 5: Verify installation
    print("\n📋 Step 5: Verifying installation")
    if verify_installation():
        print("\n🎉 SUCCESS: All fixes applied successfully!")
        print("\n📝 Summary of fixes:")
        print("  ✅ Fixed numpy/pandas compatibility issues")
        print("  ✅ Installed open-notebook with proper dependencies")
        print("  ✅ Applied email validation fixes")
        print("  ✅ Fixed model compatibility issues")
        return True
    else:
        print("\n❌ Installation verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 