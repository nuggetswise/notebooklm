#!/usr/bin/env python3
"""Test open-notebook integration"""

def test_import():
    try:
        from opennotebook.models import Notebook, Block
        print("✅ Open-notebook imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_import() 