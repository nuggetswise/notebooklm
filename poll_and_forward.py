#!/usr/bin/env python3
"""
IMAP-based Gmail Polling and Forwarding Script
Forwards Substack emails from Gmail to the RAG API using IMAP
"""

import os
import imaplib
import email
import requests
import logging
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from email.header import decode_header
import re

# Load environment variables
load_dotenv()

# Configuration
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'mandipinder@gmail.com')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
GMAIL_LABEL = os.getenv('GMAIL_LABEL', 'substackrag')
RAG_API_URL = os.getenv('RAG_API_URL', 'http://localhost:8001/inbound-email')
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('poll_and_forward.log')
    ]
)
logger = logging.getLogger(__name__)

class GmailIMAPForwarder:
    """IMAP-based Gmail forwarder for Substack emails"""
    
    def __init__(self):
        self.imap = None
        self.processed_ids = set()
        self.load_processed_ids()
    
    def load_processed_ids(self):
        """Load list of already processed email IDs"""
        try:
            processed_file = Path('processed_imap_ids.txt')
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    self.processed_ids = set(line.strip() for line in f if line.strip())
                logger.info(f"Loaded {len(self.processed_ids)} processed email IDs")
        except Exception as e:
            logger.error(f"Error loading processed IDs: {e}")
    
    def save_processed_ids(self):
        """Save list of processed email IDs"""
        try:
            with open('processed_imap_ids.txt', 'w') as f:
                for email_id in self.processed_ids:
                    f.write(f"{email_id}\n")
        except Exception as e:
            logger.error(f"Error saving processed IDs: {e}")
    
    def connect_imap(self):
        """Connect to Gmail IMAP server"""
        try:
            logger.info(f"Connecting to {IMAP_SERVER}:{IMAP_PORT}")
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            
            # Login with email and app password (clean up all types of spaces)
            logger.info(f"Logging in as {GMAIL_EMAIL}")
            clean_password = re.sub(r'\s+', '', GMAIL_APP_PASSWORD)  # Remove all whitespace including \xa0
            self.imap.login(GMAIL_EMAIL, clean_password)
            
            logger.info("✅ IMAP connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            return False
    
    def disconnect_imap(self):
        """Disconnect from IMAP server"""
        if self.imap:
            try:
                self.imap.logout()
                logger.info("IMAP connection closed")
            except Exception as e:
                logger.error(f"Error closing IMAP connection: {e}")
    
    def get_label_mailbox(self):
        """Get the mailbox name for the specified label"""
        try:
            # List all mailboxes
            status, mailboxes = self.imap.list()
            if status != 'OK':
                logger.error("Failed to list mailboxes")
                return None
            
            # Look for the label mailbox
            for mailbox in mailboxes:
                mailbox_str = mailbox.decode('utf-7')
                if GMAIL_LABEL.lower() in mailbox_str.lower():
                    # Extract mailbox name
                    mailbox_name = mailbox_str.split('"')[-2] if '"' in mailbox_str else GMAIL_LABEL
                    logger.info(f"Found label mailbox: {mailbox_name}")
                    return mailbox_name
            
            logger.warning(f"Label '{GMAIL_LABEL}' not found, trying INBOX")
            return 'INBOX'
            
        except Exception as e:
            logger.error(f"Error getting label mailbox: {e}")
            return 'INBOX'
    
    def fetch_all_emails(self, mailbox_name):
        """Fetch ALL emails from the specified mailbox (both read and unread)"""
        try:
            # Select the mailbox
            status, messages = self.imap.select(mailbox_name)
            if status != 'OK':
                logger.error(f"Failed to select mailbox: {mailbox_name}")
                return []
            
            # Search for ALL messages (not just unread)
            status, message_numbers = self.imap.search(None, 'ALL')
            if status != 'OK':
                logger.error("Failed to search for messages")
                return []
            
            if not message_numbers[0]:
                logger.info("No messages found in mailbox")
                return []
            
            # Get message numbers
            email_numbers = message_numbers[0].split()
            logger.info(f"Found {len(email_numbers)} total messages in {mailbox_name}")
            
            return email_numbers
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def get_email_content(self, email_number):
        """Get raw email content for a specific message"""
        try:
            # Fetch the email
            status, message_data = self.imap.fetch(email_number, '(RFC822)')
            if status != 'OK':
                logger.error(f"Failed to fetch email {email_number}")
                return None, None
            
            # Parse the email
            raw_email = message_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Get email ID (UID)
            status, uid_data = self.imap.fetch(email_number, '(UID)')
            if status == 'OK':
                uid = uid_data[0].decode().split()[2].rstrip(')')
            else:
                uid = str(email_number.decode())
            
            return raw_email, uid
            
        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return None, None
    
    def forward_email_to_rag(self, raw_email, uid, subject):
        """Forward email to RAG API"""
        try:
            # Send to RAG API
            response = requests.post(
                RAG_API_URL,
                data=raw_email,
                headers={'Content-Type': 'message/rfc822'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email '{subject}' (UID: {uid}) forwarded successfully")
                self.processed_ids.add(uid)
                return True
            else:
                logger.error(f"❌ Error forwarding email '{subject}': HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error forwarding email '{subject}': {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error forwarding email '{subject}': {e}")
            return False
    
    def mark_email_as_read(self, email_number):
        """Mark email as read"""
        try:
            self.imap.store(email_number, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def process_emails(self):
        """Main function to process unread emails"""
        if not self.connect_imap():
            return 0
        
        try:
            # Get the mailbox for the label
            mailbox_name = self.get_label_mailbox()
            
            # Fetch all emails
            email_numbers = self.fetch_all_emails(mailbox_name)
            
            if not email_numbers:
                return 0
            
            processed_count = 0
            
            for email_number in email_numbers:
                try:
                    # Get email content
                    raw_email, uid = self.get_email_content(email_number)
                    if not raw_email or not uid:
                        continue
                    
                    # Skip if already processed
                    if uid in self.processed_ids:
                        logger.info(f"Skipping already processed email UID: {uid}")
                        continue
                    
                    # Parse email for subject
                    email_message = email.message_from_bytes(raw_email)
                    subject = decode_header(email_message['Subject'])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='ignore')
                    subject = subject or 'No Subject'
                    
                    sender = email_message.get('From', 'Unknown')
                    date = email_message.get('Date', 'Unknown')
                    
                    logger.info(f"📨 Processing: {subject} (from {sender})")
                    
                    # Forward to RAG
                    if self.forward_email_to_rag(raw_email, uid, subject):
                        # Mark as read only if forwarding was successful
                        self.mark_email_as_read(email_number)
                        processed_count += 1
                    
                    # Small delay to avoid overwhelming the API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_number}: {e}")
                    continue
            
            # Save processed IDs
            self.save_processed_ids()
            
            return processed_count
            
        finally:
            self.disconnect_imap()

    def debug_mailboxes(self):
        """Debug function to list all available mailboxes and their contents"""
        try:
            logger.info("🔍 Debugging mailbox contents...")
            
            # List all mailboxes
            status, mailboxes = self.imap.list()
            if status != 'OK':
                logger.error("Failed to list mailboxes")
                return
            
            logger.info("📁 Available mailboxes:")
            for mailbox in mailboxes:
                mailbox_str = mailbox.decode('utf-7')
                logger.info(f"  - {mailbox_str}")
            
            # Check INBOX contents
            logger.info("📧 Checking INBOX contents...")
            status, messages = self.imap.select('INBOX')
            if status == 'OK':
                status, message_numbers = self.imap.search(None, 'ALL')
                if status == 'OK' and message_numbers[0]:
                    email_count = len(message_numbers[0].split())
                    logger.info(f"  - INBOX has {email_count} total messages")
                    
                    # Check for unread messages
                    status, unread_numbers = self.imap.search(None, 'UNSEEN')
                    if status == 'OK' and unread_numbers[0]:
                        unread_count = len(unread_numbers[0].split())
                        logger.info(f"  - INBOX has {unread_count} unread messages")
                    else:
                        logger.info("  - INBOX has 0 unread messages")
                else:
                    logger.info("  - INBOX is empty")
            
            # Check if substackrag label exists
            logger.info("🏷️ Checking for substackrag label...")
            for mailbox in mailboxes:
                mailbox_str = mailbox.decode('utf-7')
                if 'substackrag' in mailbox_str.lower():
                    logger.info(f"  - Found substackrag label: {mailbox_str}")
                    
                    # Try to select it and count messages
                    try:
                        mailbox_name = mailbox_str.split('"')[-2] if '"' in mailbox_str else 'substackrag'
                        status, messages = self.imap.select(mailbox_name)
                        if status == 'OK':
                            status, message_numbers = self.imap.search(None, 'ALL')
                            if status == 'OK' and message_numbers[0]:
                                email_count = len(message_numbers[0].split())
                                logger.info(f"  - substackrag has {email_count} messages")
                            else:
                                logger.info("  - substackrag is empty")
                    except Exception as e:
                        logger.error(f"  - Error checking substackrag: {e}")
                    break
            else:
                logger.info("  - substackrag label not found")
                
        except Exception as e:
            logger.error(f"Error debugging mailboxes: {e}")

def main():
    """Main function"""
    # Validate environment variables
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        logger.error("❌ Missing required environment variables!")
        logger.error("Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD in your .env file")
        return
    
    logger.info("🚀 Starting Gmail IMAP forwarder...")
    logger.info(f"📧 Email: {GMAIL_EMAIL}")
    logger.info(f"🏷️  Label: {GMAIL_LABEL}")
    logger.info(f"🔗 API URL: {RAG_API_URL}")
    logger.info("=" * 50)
    
    forwarder = GmailIMAPForwarder()
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # Process once
            count = forwarder.process_emails()
            logger.info(f"📊 Processed {count} emails")
        elif sys.argv[1] == "debug":
            # Debug mode - just check mailboxes
            if forwarder.connect_imap():
                forwarder.debug_mailboxes()
                forwarder.disconnect_imap()
        elif sys.argv[1] == "continuous":
            # Run continuously
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 5 minutes default
            logger.info(f"⏰ Running continuously, checking every {interval} seconds")
            
            while True:
                try:
                    count = forwarder.process_emails()
                    if count > 0:
                        logger.info(f"📊 Processed {count} emails")
                    logger.info(f"⏰ Next check in {interval} seconds...")
                    time.sleep(interval)
                except KeyboardInterrupt:
                    logger.info("👋 Stopping Gmail IMAP forwarder...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in main loop: {e}")
                    time.sleep(interval)
        else:
            logger.error("Usage: python poll_and_forward.py [once|debug|continuous] [interval_seconds]")
    else:
        # Default: process once
        count = forwarder.process_emails()
        logger.info(f"📊 Processed {count} emails")

if __name__ == "__main__":
    main() 