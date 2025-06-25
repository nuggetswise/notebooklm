#!/usr/bin/env python3
"""
World-class installation script for open-notebook with robust dependency resolution.
This script uses multiple strategies to handle complex dependency conflicts.
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

def create_isolated_environment():
    """Create an isolated environment for open-notebook installation."""
    print("🔧 Creating isolated environment for open-notebook...")
    
    # Create a temporary directory for isolated installation
    temp_dir = tempfile.mkdtemp(prefix="open_notebook_install_")
    print(f"📁 Temporary directory: {temp_dir}")
    
    # Create a minimal requirements file for open-notebook
    requirements_content = """# Minimal requirements for open-notebook
open-notebook @ git+https://github.com/lfnovo/open-notebook
"""
    
    requirements_file = os.path.join(temp_dir, "requirements.txt")
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    return temp_dir, requirements_file

def install_with_constraints():
    """Install open-notebook with strict version constraints."""
    print("🎯 Attempting installation with strict version constraints...")
    
    # Create a constraints file to pin versions
    constraints_content = """# Version constraints to avoid conflicts
langchain==0.3.26
langchain-core==0.3.66
langchain-community==0.3.26
langchain-openai==0.3.25
openai==1.91.0
pydantic==2.9.2
streamlit==1.46.0
"""
    
    constraints_file = "constraints.txt"
    with open(constraints_file, 'w') as f:
        f.write(constraints_content)
    
    # Try installation with constraints
    cmd = f"{sys.executable} -m pip install -c {constraints_file} git+https://github.com/lfnovo/open-notebook"
    success, _ = run_command(cmd, "Installing open-notebook with constraints")
    
    # Clean up
    os.remove(constraints_file)
    return success

def install_with_legacy_resolver():
    """Install using legacy dependency resolver."""
    print("🔄 Attempting installation with legacy resolver...")
    
    cmd = f"{sys.executable} -m pip install --use-deprecated=legacy-resolver git+https://github.com/lfnovo/open-notebook"
    success, _ = run_command(cmd, "Installing open-notebook with legacy resolver")
    return success

def install_with_no_deps():
    """Install open-notebook without dependencies, then install deps separately."""
    print("🔧 Attempting installation without dependencies...")
    
    # Step 1: Install open-notebook without deps
    cmd1 = f"{sys.executable} -m pip install --no-deps git+https://github.com/lfnovo/open-notebook"
    success1, _ = run_command(cmd1, "Installing open-notebook without dependencies")
    
    if not success1:
        return False
    
    # Step 2: Install core dependencies manually
    core_deps = [
        "langchain>=0.3.26",
        "langchain-core>=0.3.66", 
        "langchain-community>=0.3.26",
        "langchain-openai>=0.3.25",
        "openai>=1.86.0,<2.0.0",
        "pydantic>=2.9.2",
        "streamlit>=1.45.0"
    ]
    
    for dep in core_deps:
        success, _ = run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}")
        if not success:
            print(f"⚠️  Warning: Failed to install {dep}")
    
    return True

def install_in_isolated_env():
    """Install in an isolated environment and copy to main environment."""
    print("🏝️  Attempting installation in isolated environment...")
    
    temp_dir, requirements_file = create_isolated_environment()
    
    try:
        # Create a new virtual environment in temp directory
        venv_path = os.path.join(temp_dir, "venv")
        cmd1 = f"{sys.executable} -m venv {venv_path}"
        success1, _ = run_command(cmd1, "Creating isolated virtual environment")
        
        if not success1:
            return False
        
        # Activate and install in isolated environment
        if os.name == 'nt':  # Windows
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        else:  # Unix/Linux/macOS
            python_path = os.path.join(venv_path, "bin", "python")
            pip_path = os.path.join(venv_path, "bin", "pip")
        
        # Install in isolated environment
        cmd2 = f"{pip_path} install -r {requirements_file}"
        success2, _ = run_command(cmd2, "Installing in isolated environment")
        
        if not success2:
            return False
        
        # Copy open-notebook to main environment
        site_packages = os.path.join(venv_path, "lib", "python3.11", "site-packages")
        open_notebook_path = os.path.join(site_packages, "opennotebook")
        
        if os.path.exists(open_notebook_path):
            # Get main environment site-packages
            import site
            main_site_packages = site.getsitepackages()[0]
            target_path = os.path.join(main_site_packages, "opennotebook")
            
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            shutil.copytree(open_notebook_path, target_path)
            print("✅ Successfully copied open-notebook to main environment")
            return True
        
        return False
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

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

def main():
    print("🚀 Starting world-class open-notebook installation...")
    print("=" * 60)
    
    # Strategy 1: Try with constraints
    print("\n📋 Strategy 1: Installation with version constraints")
    if install_with_constraints():
        if verify_installation():
            print("\n🎉 SUCCESS: open-notebook installed with constraints!")
            return True
    
    # Strategy 2: Try with legacy resolver
    print("\n📋 Strategy 2: Installation with legacy resolver")
    if install_with_legacy_resolver():
        if verify_installation():
            print("\n🎉 SUCCESS: open-notebook installed with legacy resolver!")
            return True
    
    # Strategy 3: Try without dependencies
    print("\n📋 Strategy 3: Installation without dependencies")
    if install_with_no_deps():
        if verify_installation():
            print("\n🎉 SUCCESS: open-notebook installed without dependencies!")
            return True
    
    # Strategy 4: Try in isolated environment
    print("\n📋 Strategy 4: Installation in isolated environment")
    if install_in_isolated_env():
        if verify_installation():
            print("\n🎉 SUCCESS: open-notebook installed in isolated environment!")
            return True
    
    # All strategies failed
    print("\n❌ All installation strategies failed")
    print("\n🔧 Manual installation steps:")
    print("1. Create a fresh virtual environment")
    print("2. Install dependencies one by one:")
    print("   pip install langchain==0.3.26")
    print("   pip install langchain-core==0.3.66")
    print("   pip install langchain-community==0.3.26")
    print("   pip install openai==1.91.0")
    print("   pip install langchain-openai==0.3.25")
    print("   pip install git+https://github.com/lfnovo/open-notebook")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 