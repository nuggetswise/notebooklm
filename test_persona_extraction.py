#!/usr/bin/env python3
"""
Test script for persona extraction functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from ingestion_api.persona_extractor import persona_extractor

def test_persona_extraction():
    """Test persona extraction with various email sender formats."""
    
    test_cases = [
        # Display name formats
        "Nate from Nate's Substack <newsletter@substack.com>",
        "Ami Vora <amivora@substack.com>",
        "Ethan Evans <ethan@example.com>",
        "Wes Kao <wes@example.com>",
        "Noah Smith <noah@example.com>",
        
        # Email-only formats
        "john.doe@example.com",
        "jane_smith@company.com",
        "bob-wilson@startup.io",
        
        # Complex formats
        "Dr. Sarah Johnson via LinkedIn <sarah@linkedin.com>",
        "Team Newsletter <newsletter@company.com>",
        "Support Team <support@service.com>",
        
        # Edge cases
        "newsletter@substack.com",
        "noreply@example.com",
        "admin@company.com"
    ]
    
    print("🧪 Testing Persona Extraction")
    print("=" * 50)
    
    for sender in test_cases:
        print(f"\n📧 Testing: {sender}")
        
        # Extract first name
        first_name = persona_extractor.extract_first_name(sender)
        print(f"   First Name: {first_name or 'Not found'}")
        
        # Create persona
        persona = persona_extractor.create_persona(
            sender=sender,
            subject="Test email about AI and technology",
            content="This is a test email discussing artificial intelligence, machine learning, and startup technology trends."
        )
        
        print(f"   Persona ID: {persona['id']}")
        print(f"   Persona Type: {persona['persona_type']}")
        print(f"   Topics: {', '.join(persona['topics']) if persona['topics'] else 'None'}")
        print(f"   Email Count: {persona['email_count']}")

def test_persona_context():
    """Test persona context generation."""
    
    print("\n\n🎭 Testing Persona Context Generation")
    print("=" * 50)
    
    test_senders = [
        "Nate from Nate's Substack <newsletter@substack.com>",
        "Ami Vora <amivora@substack.com>",
        "Ethan Evans <ethan@example.com>"
    ]
    
    for sender in test_senders:
        # Create persona first
        persona_extractor.create_persona(
            sender=sender,
            subject="AI and Technology Update",
            content="Latest developments in artificial intelligence and machine learning."
        )
        
        # Get context
        context = persona_extractor.get_persona_context(sender)
        print(f"\n📧 {sender}")
        print(f"   Context: {context}")

def test_persona_api():
    """Test persona API endpoints."""
    
    print("\n\n🔌 Testing Persona API Endpoints")
    print("=" * 50)
    
    import requests
    import json
    
    base_url = "http://localhost:8000"
    
    try:
        # Test getting all personas
        response = requests.get(f"{base_url}/personas")
        if response.status_code == 200:
            personas = response.json()
            print(f"✅ Found {len(personas)} personas")
            for persona in personas[:3]:  # Show first 3
                print(f"   - {persona['first_name']} ({persona['sender']})")
        else:
            print(f"❌ Error getting personas: {response.status_code}")
        
        # Test getting persona context
        test_sender = "Nate from Nate's Substack <newsletter@substack.com>"
        response = requests.get(f"{base_url}/personas/context/{test_sender}")
        if response.status_code == 200:
            context = response.json()
            print(f"\n✅ Persona context for {test_sender}:")
            print(f"   {context['context']}")
        else:
            print(f"❌ Error getting persona context: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_persona_extraction()
    test_persona_context()
    test_persona_api()
    
    print("\n\n✅ Persona extraction test completed!")
    print("\nTo see all personas, check: data/personas.json") 