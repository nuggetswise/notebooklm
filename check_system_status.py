#!/usr/bin/env python3
"""
System Status Checker for Email RAG System
"""

import sys
import importlib
from pathlib import Path

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 Email RAG System - Dependency Check")
    print("=" * 60)
    
    # Core dependencies
    print("\n📦 Core Dependencies:")
    core_deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("cohere", "Cohere"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
        ("python_dotenv", "Python-dotenv"),
    ]
    
    core_status = []
    for module, name in core_deps:
        core_status.append(check_import(module, name))
    
    # Optional dependencies
    print("\n🔧 Optional Dependencies:")
    optional_deps = [
        ("fitz", "PyMuPDF"),
        ("pytesseract", "Pytesseract"),
        ("PIL", "Pillow"),
        ("bs4", "BeautifulSoup4"),
        ("open_notebook", "Open Notebook"),
    ]
    
    optional_status = []
    for module, name in optional_deps:
        optional_status.append(check_import(module, name))
    
    # Check if system can start
    print("\n🚀 System Startup Test:")
    try:
        # Test basic imports
        sys.path.append(str(Path(__file__).parent))
        
        # Test ingestion API
        from ingestion_api.config import config
        print("✅ Ingestion API config")
        
        from ingestion_api.database import db
        print("✅ Database module")
        
        from rag.email_pipeline import pipeline
        print("✅ RAG pipeline")
        
        from rag.embedder import embedder
        print("✅ Embedder")
        
        from rag.generator import generator
        print("✅ Generator")
        
        print("\n🎉 System is ready to run!")
        
    except Exception as e:
        print(f"❌ System startup failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"Core dependencies: {sum(core_status)}/{len(core_status)} working")
    print(f"Optional dependencies: {sum(optional_status)}/{len(optional_status)} available")
    
    if all(core_status):
        print("✅ All core dependencies are available!")
        print("💡 The system should work properly.")
    else:
        print("⚠️ Some core dependencies are missing.")
        print("💡 Run: pip install -r requirements_minimal.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 