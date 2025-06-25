"""
Integration tests for the complete Email RAG system
Tests end-to-end functionality from email ingestion to RAG querying
"""

import pytest
import requests
import time
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:8501"

class TestCompleteSystem:
    """Test the complete Email RAG system integration"""
    
    def test_backend_health(self):
        """Test that the backend API is running and healthy"""
        try:
            response = requests.get(f"{API_BASE_URL}/status", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "total_count" in data
            assert "emails" in data
            print("✅ Backend API is healthy")
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Backend API not available: {e}")
    
    def test_frontend_health(self):
        """Test that the frontend is running"""
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            assert response.status_code == 200
            assert "Streamlit" in response.text
            print("✅ Frontend is running")
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Frontend not available: {e}")
    
    def test_email_ingestion_workflow(self):
        """Test complete email ingestion workflow"""
        # Test email ingestion
        test_email_path = Path(__file__).parent.parent / "test_email.eml"
        assert test_email_path.exists(), "Test email file not found"
        
        with open(test_email_path, 'rb') as f:
            email_content = f.read()
        try:
            response = requests.post(
                f"{API_BASE_URL}/inbound-email",
                data=email_content,
                headers={"Content-Type": "message/rfc822"},
                timeout=10
            )
            assert response.status_code == 200
            print("✅ Email ingestion successful")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Check that email was stored
            status_response = requests.get(f"{API_BASE_URL}/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["total_count"] > 0
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Email ingestion test failed: {e}")
    
    def test_rag_query_workflow(self):
        """Test complete RAG query workflow"""
        try:
            # Test RAG query
            query_data = {
                "question": "What is this email about?",
                "label": "AI",
                "days_back": 30
            }
            
            response = requests.post(
                f"{API_BASE_URL}/query",
                json=query_data,
                timeout=10
            )
            assert response.status_code == 200
            
            result = response.json()
            assert "answer" in result
            assert "metadata" in result
            print("✅ RAG query successful")
            
            # Test that we got a meaningful response
            assert len(result["answer"]) > 10, "Answer too short"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"RAG query test failed: {e}")
    
    def test_api_endpoints(self):
        """Test all major API endpoints"""
        try:
            # Test labels endpoint
            response = requests.get(f"{API_BASE_URL}/labels")
            assert response.status_code == 200
            labels_data = response.json()
            assert "labels" in labels_data
            print("✅ Labels endpoint working")
            
            # Test status endpoint (which returns emails)
            response = requests.get(f"{API_BASE_URL}/status")
            assert response.status_code == 200
            status_data = response.json()
            assert "emails" in status_data
            print("✅ Status endpoint working")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API endpoints test failed: {e}")
    
    def test_frontend_api_integration(self):
        """Test that frontend can communicate with backend APIs"""
        try:
            # Test that frontend can access backend status
            response = requests.get(f"{API_BASE_URL}/status")
            assert response.status_code == 200
            
            # Test that frontend can get labels
            response = requests.get(f"{API_BASE_URL}/labels")
            assert response.status_code == 200
            
            print("✅ Frontend-backend integration working")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Frontend integration test failed: {e}")

def test_system_requirements():
    """Test that all system requirements are met"""
    # Check data directories exist
    data_dir = Path("data")
    parsed_dir = data_dir / "parsed_emails"
    maildir_dir = data_dir / "maildir"
    
    assert data_dir.exists(), "Data directory not found"
    assert parsed_dir.exists(), "Parsed emails directory not found"
    assert maildir_dir.exists(), "Maildir directory not found"
    
    # Check database exists
    db_path = data_dir / "email_index.db"
    assert db_path.exists(), "Database file not found"
    
    print("✅ System requirements met")

if __name__ == "__main__":
    # Run integration tests
    print("🧪 Running Email RAG System Integration Tests")
    print("=" * 50)
    
    # Test system requirements
    test_system_requirements()
    
    # Create test instance
    test_instance = TestCompleteSystem()
    
    # Run tests
    test_instance.test_backend_health()
    test_instance.test_frontend_health()
    test_instance.test_email_ingestion_workflow()
    test_instance.test_rag_query_workflow()
    test_instance.test_api_endpoints()
    test_instance.test_frontend_api_integration()
    
    print("=" * 50)
    print("🎉 All integration tests completed!")
    print("📧 Email RAG System is fully operational!") 