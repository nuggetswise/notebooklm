#!/usr/bin/env python3
"""
Gmail Forwarder for Email RAG System
Forwards emails from Gmail to the RAG API using Gmail API
"""

import os
import base64
import time
import json
import requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
RAG_API_URL = "http://localhost:8001/inbound-email"
CREDENTIALS_FILE = 'gmail_credentials.json'
TOKEN_FILE = 'gmail_token.pickle'
PROCESSED_IDS_FILE = 'processed_email_ids.json'

class GmailForwarder:
    def __init__(self):
        self.service = None
        self.processed_ids = self.load_processed_ids()
        
    def load_processed_ids(self):
        """Load list of already processed email IDs"""
        try:
            with open(PROCESSED_IDS_FILE, 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def save_processed_ids(self):
        """Save list of processed email IDs"""
        with open(PROCESSED_IDS_FILE, 'w') as f:
            json.dump(list(self.processed_ids), f)
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    print(f"❌ {CREDENTIALS_FILE} not found!")
                    print("Please download your Gmail API credentials from Google Cloud Console")
                    print("and save them as 'gmail_credentials.json'")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def forward_email_to_rag(self, email_id, subject):
        """Forward a single email to the RAG API"""
        try:
            # Get the raw email
            message = self.service.users().messages().get(
                userId='me', id=email_id, format='raw'
            ).execute()
            
            # Decode the raw email
            raw_email = base64.urlsafe_b64decode(message['raw'])
            
            # Forward to RAG API
            response = requests.post(
                RAG_API_URL,
                data=raw_email,
                headers={'Content-Type': 'message/rfc822'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Email '{subject}' forwarded successfully")
                self.processed_ids.add(email_id)
                return True
            else:
                print(f"❌ Error forwarding email '{subject}': {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing email '{subject}': {e}")
            return False
    
    def check_new_emails(self, label_pattern="Label: AI", max_results=10):
        """Check for new emails with the specified label pattern"""
        if not self.service:
            print("❌ Gmail service not authenticated")
            return
        
        try:
            # Search for emails with the label pattern
            query = f'subject:"{label_pattern}"'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("📧 No new emails found")
                return
            
            print(f"📧 Found {len(messages)} emails to process")
            
            for message in messages:
                email_id = message['id']
                
                # Skip if already processed
                if email_id in self.processed_ids:
                    continue
                
                # Get email details
                email_details = self.service.users().messages().get(
                    userId='me', id=email_id, format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                headers = email_details['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                print(f"📨 Processing: {subject} (from {sender})")
                
                # Forward to RAG
                self.forward_email_to_rag(email_id, subject)
                
                # Small delay to avoid rate limiting
                time.sleep(1)
            
            # Save processed IDs
            self.save_processed_ids()
            
        except Exception as e:
            print(f"❌ Error checking emails: {e}")
    
    def run_continuous(self, interval=60, label_pattern="Label: AI"):
        """Run continuously, checking for new emails every interval seconds"""
        print(f"🚀 Starting Gmail forwarder...")
        print(f"📧 Checking for emails with pattern: '{label_pattern}'")
        print(f"⏰ Checking every {interval} seconds")
        print(f"🔗 Forwarding to: {RAG_API_URL}")
        print("=" * 50)
        
        while True:
            try:
                self.check_new_emails(label_pattern)
                print(f"⏰ Next check in {interval} seconds...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n👋 Stopping Gmail forwarder...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(interval)

def main():
    """Main function"""
    forwarder = GmailForwarder()
    
    # Authenticate
    if not forwarder.authenticate_gmail():
        return
    
    print("✅ Gmail authentication successful!")
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # Check once
            forwarder.check_new_emails()
        elif sys.argv[1] == "continuous":
            # Run continuously
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            forwarder.run_continuous(interval)
        else:
            print("Usage: python gmail_forwarder.py [once|continuous] [interval_seconds]")
    else:
        # Default: check once
        forwarder.check_new_emails()

if __name__ == "__main__":
    main() 