import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from ingestion_api.parser import EmailParser
from ingestion_api.database import EmailDatabase
from ingestion_api.models import EmailMetadata

class TestEmailParser:
    """Test email parsing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.parser = EmailParser()
        
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "data"
        self.test_data_dir.mkdir()
        (self.test_data_dir / "parsed_emails").mkdir()
        (self.test_data_dir / "maildir").mkdir()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_simple_email(self):
        """Test parsing a simple text email."""
        # Create a simple MIME email
        email_content = f"""From: test@example.com
To: recipient@example.com
Subject: Test Email
Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}
Content-Type: text/plain

This is a test email body.
"""
        
        # Parse the email
        result = self.parser.parse_email(email_content.encode('utf-8'))
        
        # Verify basic fields
        assert result['subject'] == 'Test Email'
        assert result['sender'] == 'test@example.com'
        assert result['label'] == 'AI'  # Default label
        assert 'test email body' in result['body'].lower()
        assert result['has_attachments'] == False
        assert result['attachment_count'] == 0
    
    def test_parse_email_with_label(self):
        """Test parsing email with label in subject."""
        email_content = f"""From: test@example.com
To: recipient@example.com
Subject: Label: Fintech - Important Update
Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}
Content-Type: text/plain

This is a fintech related email.
"""
        
        result = self.parser.parse_email(email_content.encode('utf-8'))
        
        assert result['label'] == 'Fintech'
        assert 'fintech related' in result['body'].lower()
    
    def test_save_parsed_email(self):
        """Test saving parsed email to file."""
        email_data = {
            'subject': 'Test Subject',
            'sender': 'test@example.com',
            'date': datetime.utcnow(),
            'label': 'Test',
            'full_content': 'This is test content.'
        }
        
        email_id = "test-123"
        filepath = self.parser.save_parsed_email(email_data, email_id)
        
        assert filepath != ""
        assert os.path.exists(filepath)
        
        # Verify file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Subject' in content
            assert 'test@example.com' in content
            assert 'This is test content.' in content

class TestEmailDatabase:
    """Test database operations."""
    
    def setup_method(self):
        """Set up test database."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_email_index.db")
        self.db = EmailDatabase(self.db_path)
    
    def teardown_method(self):
        """Clean up test database."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_insert_and_retrieve_email(self):
        """Test inserting and retrieving email metadata."""
        email = EmailMetadata(
            subject="Test Email",
            sender="test@example.com",
            date=datetime.utcnow(),
            label="Test",
            parsed_path="/tmp/test.txt"
        )
        
        # Insert email
        success = self.db.insert_email(email)
        assert success == True
        
        # Retrieve email
        retrieved = self.db.get_email_by_id(email.id)
        assert retrieved is not None
        assert retrieved.subject == "Test Email"
        assert retrieved.sender == "test@example.com"
        assert retrieved.label == "Test"
    
    def test_get_emails_by_label(self):
        """Test retrieving emails by label."""
        # Insert multiple emails with different labels
        email1 = EmailMetadata(
            subject="Test Email 1",
            sender="test1@example.com",
            date=datetime.utcnow(),
            label="AI",
            parsed_path="/tmp/test1.txt"
        )
        
        email2 = EmailMetadata(
            subject="Test Email 2",
            sender="test2@example.com",
            date=datetime.utcnow(),
            label="Fintech",
            parsed_path="/tmp/test2.txt"
        )
        
        self.db.insert_email(email1)
        self.db.insert_email(email2)
        
        # Get emails by label
        ai_emails = self.db.get_emails_by_label("AI")
        assert len(ai_emails) == 1
        assert ai_emails[0].subject == "Test Email 1"
        
        fintech_emails = self.db.get_emails_by_label("Fintech")
        assert len(fintech_emails) == 1
        assert fintech_emails[0].subject == "Test Email 2"
    
    def test_get_labels(self):
        """Test retrieving all unique labels."""
        # Insert emails with different labels
        email1 = EmailMetadata(
            subject="Test Email 1",
            sender="test1@example.com",
            date=datetime.utcnow(),
            label="AI",
            parsed_path="/tmp/test1.txt"
        )
        
        email2 = EmailMetadata(
            subject="Test Email 2",
            sender="test2@example.com",
            date=datetime.utcnow(),
            label="Fintech",
            parsed_path="/tmp/test2.txt"
        )
        
        email3 = EmailMetadata(
            subject="Test Email 3",
            sender="test3@example.com",
            date=datetime.utcnow(),
            label="AI",
            parsed_path="/tmp/test3.txt"
        )
        
        self.db.insert_email(email1)
        self.db.insert_email(email2)
        self.db.insert_email(email3)
        
        labels = self.db.get_labels()
        assert "AI" in labels
        assert "Fintech" in labels
        assert len(labels) == 2

if __name__ == "__main__":
    # Run basic tests
    print("Running email ingestion tests...")
    
    # Test parser
    test_parser = TestEmailParser()
    test_parser.setup_method()
    
    print("Testing simple email parsing...")
    test_parser.test_parse_simple_email()
    
    print("Testing email with label...")
    test_parser.test_parse_email_with_label()
    
    print("Testing email saving...")
    test_parser.test_save_parsed_email()
    
    test_parser.teardown_method()
    
    # Test database
    test_db = TestEmailDatabase()
    test_db.setup_method()
    
    print("Testing database operations...")
    test_db.test_insert_and_retrieve_email()
    test_db.test_get_emails_by_label()
    test_db.test_get_labels()
    
    test_db.teardown_method()
    
    print("✅ All tests passed!") 