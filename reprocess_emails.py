#!/usr/bin/env python3
"""
Script to reprocess existing parsed email files and insert them into the database
with the new sender domain labeling system.
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
import re

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from ingestion_api.parser import EmailParser
from ingestion_api.database import EmailDatabase
from ingestion_api.models import EmailMetadata, PersonaInfo

def extract_email_data_from_file(file_path: str) -> dict:
    """Extract email data from a parsed email file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into metadata and body
        lines = content.split('\n')
        metadata_section = []
        body_section = []
        in_body = False
        
        for line in lines:
            if line.startswith('-' * 80):
                in_body = True
                continue
            if in_body:
                body_section.append(line)
            else:
                metadata_section.append(line)
        
        # Parse metadata
        metadata = {}
        for line in metadata_section:
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        # Extract sender domain as label
        sender = metadata.get('From', metadata.get('Sender', 'unknown@example.com'))
        match = re.search(r'@([A-Za-z0-9.-]+)', sender)
        domain_label = match.group(1).lower() if match else "unknown"
        
        # Create email data structure
        email_data = {
            'subject': metadata.get('Subject', 'No Subject'),
            'sender': sender,
            'date': datetime.utcnow(),  # We'll use current time since original date might not be available
            'label': domain_label,
            'body': '\n'.join(body_section),
            'attachments': [],
            'full_content': content,
            'has_attachments': False,
            'attachment_count': 0,
            'persona': None
        }
        
        return email_data
        
    except Exception as e:
        print(f"Error extracting email data from {file_path}: {e}")
        return None

def reprocess_emails():
    """Reprocess all parsed email files and insert them into the database."""
    parser = EmailParser()
    db = EmailDatabase()
    
    # Get all parsed email files
    parsed_emails_dir = Path("data/parsed_emails")
    if not parsed_emails_dir.exists():
        print("Parsed emails directory not found")
        return
    
    email_files = list(parsed_emails_dir.glob("*.txt"))
    print(f"Found {len(email_files)} parsed email files")
    
    processed_count = 0
    error_count = 0
    
    for file_path in email_files:
        try:
            # Extract email data from file
            email_data = extract_email_data_from_file(str(file_path))
            if not email_data:
                error_count += 1
                continue
            
            # Generate email ID
            email_id = str(uuid.uuid4())
            
            # Create email metadata
            email_metadata = EmailMetadata(
                id=email_id,
                subject=email_data['subject'],
                sender=email_data['sender'],
                date=email_data['date'],
                label=email_data['label'],
                parsed_path=str(file_path),
                has_attachments=email_data['has_attachments'],
                attachment_count=email_data['attachment_count'],
                persona=PersonaInfo(**email_data['persona']) if email_data.get('persona') else None
            )
            
            # Insert into database
            if db.insert_email(email_metadata):
                processed_count += 1
                print(f"✓ Processed: {email_data['subject']} -> {email_data['label']}")
            else:
                error_count += 1
                print(f"✗ Failed to insert: {email_data['subject']}")
                
        except Exception as e:
            error_count += 1
            print(f"✗ Error processing {file_path}: {e}")
    
    print(f"\nReprocessing complete:")
    print(f"✓ Successfully processed: {processed_count}")
    print(f"✗ Errors: {error_count}")
    
    # Show new labels
    labels = db.get_labels()
    print(f"\nAvailable labels: {labels}")

if __name__ == "__main__":
    reprocess_emails() 