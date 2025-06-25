#!/usr/bin/env python3
"""
Test script for open-notebook integration.
Run this after the open-notebook installation completes.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def test_open_notebook_import():
    """Test if open-notebook can be imported."""
    try:
        from opennotebook.models import Notebook, Block
        print("✅ Open-notebook imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Open-notebook import failed: {e}")
        return False

def test_notebook_creation():
    """Test creating a sample notebook."""
    try:
        from opennotebook.models import Notebook, Block
        
        # Create sample blocks
        blocks = [
            Block(
                type='text',
                text='This is a test email body content.'
            ),
            Block(
                type='pdf',
                text='This is extracted PDF content from an attachment.',
                metadata={
                    'filename': 'test.pdf',
                    'content_type': 'application/pdf',
                    'size': 1024
                }
            ),
            Block(
                type='image',
                text='This is OCR text from an image attachment.',
                metadata={
                    'filename': 'test.jpg',
                    'content_type': 'image/jpeg',
                    'size': 2048
                }
            )
        ]
        
        # Create notebook
        notebook = Notebook(
            id=str(uuid.uuid4()),
            title='Test Email Subject',
            blocks=blocks,
            metadata={
                'sender': 'test@example.com',
                'date': datetime.utcnow().isoformat(),
                'label': 'Test',
                'has_attachments': True,
                'attachment_count': 2,
                'source': 'email'
            }
        )
        
        # Save to JSON
        notebooks_dir = Path("notebooks")
        notebooks_dir.mkdir(exist_ok=True)
        
        notebook_path = notebooks_dir / f"{notebook.id}.json"
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook.dict(), f, indent=2, default=str)
        
        print(f"✅ Test notebook created: {notebook_path}")
        
        # Test loading back
        with open(notebook_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        loaded_notebook = Notebook(**loaded_data)
        print(f"✅ Test notebook loaded successfully with {len(loaded_notebook.blocks)} blocks")
        
        return True
        
    except Exception as e:
        print(f"❌ Notebook creation test failed: {e}")
        return False

def test_parser_integration():
    """Test the parser integration."""
    try:
        from ingestion_api.parser import parser
        
        # Create sample email data
        email_data = {
            'subject': 'Test Email with Attachments',
            'sender': 'test@example.com',
            'date': datetime.utcnow(),
            'label': 'Test',
            'body': 'This is the email body content.',
            'attachments': [
                {
                    'filename': 'test.pdf',
                    'content_type': 'application/pdf',
                    'size': 1024,
                    'extracted_text': 'This is PDF content.'
                },
                {
                    'filename': 'test.jpg',
                    'content_type': 'image/jpeg',
                    'size': 2048,
                    'extracted_text': 'This is OCR text from image.'
                }
            ],
            'full_content': 'Combined content',
            'has_attachments': True,
            'attachment_count': 2
        }
        
        # Test notebook creation
        email_id = str(uuid.uuid4())
        parser._create_notebook(email_data, email_id)
        
        print("✅ Parser integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Parser integration test failed: {e}")
        return False

def test_document_source():
    """Test the document source integration."""
    try:
        from rag.document_source import notebook_source
        
        # Test loading documents
        documents = notebook_source.load_documents()
        print(f"✅ Document source loaded {len(documents)} documents")
        
        if documents:
            # Test chunking
            chunked_docs = notebook_source.chunk_documents(documents)
            print(f"✅ Document source created {len(chunked_docs)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Document source test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing open-notebook integration...")
    print("=" * 50)
    
    tests = [
        ("Open-notebook Import", test_open_notebook_import),
        ("Notebook Creation", test_notebook_creation),
        ("Parser Integration", test_parser_integration),
        ("Document Source", test_document_source)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Open-notebook integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 