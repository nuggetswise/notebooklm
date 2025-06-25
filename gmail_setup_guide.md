# Gmail.com Email Forwarding Setup for Email RAG System

## Overview
Since Gmail.com has restrictions on forwarding to unverified addresses, we'll use a combination of Gmail filters and manual forwarding to get emails into your RAG system.

## Method 1: Gmail Filters + Manual Forwarding (Recommended)

### Step 1: Set up Gmail Filters
1. **Go to Gmail Settings** → **Filters and Blocked Addresses**
2. **Click "Create a new filter"**
3. **Set up filter criteria:**
   - **Subject:** `Label: AI` (or whatever label pattern you want)
   - **Has the words:** `Label: AI` (or your preferred label)
4. **Click "Create filter"**
5. **Select actions:**
   - ✅ **Forward it to:** (we'll set this up in Step 2)
   - ✅ **Mark it as read**
   - ✅ **Apply the label:** Create a new label like "RAG-Processed"
6. **Click "Create filter"**

### Step 2: Set up Forwarding Address
1. **Go to Gmail Settings** → **Forwarding and POP/IMAP**
2. **Click "Add a forwarding address"**
3. **Enter:** `rag-system@yourdomain.com` (if you have a domain)
   - **OR** use a service like [ForwardEmail.net](https://forwardemail.net) to create a forwarding address
4. **Gmail will send a verification email**
5. **Click the verification link in the email**

### Step 3: Alternative - Use Email Forwarding Service
If you don't have a domain, use a free service:

#### Option A: ForwardEmail.net
1. Go to [ForwardEmail.net](https://forwardemail.net)
2. Create a free account
3. Set up forwarding from `yourname@forwardemail.net` to your smtp2http server
4. Use this address in your Gmail forwarding settings

#### Option B: ImprovMX
1. Go to [ImprovMX.com](https://improvmx.com)
2. Create a free account
3. Set up forwarding to your smtp2http server

## Method 2: Gmail API + Webhook (Advanced)

### Step 1: Set up Gmail API
1. **Go to Google Cloud Console**
2. **Create a new project**
3. **Enable Gmail API**
4. **Create credentials (OAuth 2.0)**
5. **Download the credentials JSON file**

### Step 2: Create Gmail Webhook Script
```python
# gmail_webhook.py
import os
import base64
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
RAG_API_URL = "http://localhost:8001/inbound-email"

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def forward_email_to_rag(email_id):
    service = get_gmail_service()
    
    # Get the raw email
    message = service.users().messages().get(
        userId='me', id=email_id, format='raw'
    ).execute()
    
    # Decode the raw email
    raw_email = base64.urlsafe_b64decode(message['raw'])
    
    # Forward to RAG API
    response = requests.post(
        RAG_API_URL,
        data=raw_email,
        headers={'Content-Type': 'message/rfc822'}
    )
    
    if response.status_code == 200:
        print(f"Email {email_id} forwarded successfully")
    else:
        print(f"Error forwarding email {email_id}: {response.text}")

def check_new_emails():
    service = get_gmail_service()
    
    # Get recent messages with label
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='subject:"Label: AI"',
        maxResults=10
    ).execute()
    
    messages = results.get('messages', [])
    
    for message in messages:
        forward_email_to_rag(message['id'])

if __name__ == '__main__':
    check_new_emails()
```

## Method 3: Manual Testing Setup

### Step 1: Download smtp2http
1. Go to [smtp2http releases](https://github.com/chrusty/smtp2http/releases)
2. Download the version for your OS (macOS in your case)
3. Make it executable: `chmod +x smtp2http`

### Step 2: Run smtp2http
```bash
./smtp2http --config smtp2http.yaml
```

### Step 3: Test with Manual Email
1. Create a test email with subject: `Label: AI - Test Email`
2. Save it as `test_email.eml`
3. Send it to your smtp2http server:
```bash
curl -X POST http://localhost:8001/inbound-email \
  --data-binary @test_email.eml \
  --header "Content-Type: message/rfc822"
```

## Quick Start (Recommended for Testing)

### Step 1: Install smtp2http
```bash
# Download smtp2http for macOS
curl -L -o smtp2http https://github.com/chrusty/smtp2http/releases/latest/download/smtp2http-darwin-amd64
chmod +x smtp2http
```

### Step 2: Start smtp2http
```bash
./smtp2http --listen-addr ":2525" --forward-url "http://localhost:8001/inbound-email"
```

### Step 3: Test Email Forwarding
1. Create a test email file:
```bash
cat > test_email.eml << 'EOF'
From: test@gmail.com
To: your-email@gmail.com
Subject: Label: AI - Test Email for RAG
Date: $(date -R)
Content-Type: text/plain

This is a test email for the RAG system.
EOF
```

2. Send it to your API:
```bash
curl -X POST http://localhost:8001/inbound-email \
  --data-binary @test_email.eml \
  --header "Content-Type: message/rfc822"
```

3. Check your RAG system at http://localhost:8501

## Troubleshooting

### Common Issues:
1. **Port 2525 blocked:** Use a different port (e.g., 2526)
2. **Gmail verification failed:** Use a forwarding service like ForwardEmail.net
3. **API not responding:** Check that your FastAPI server is running on port 8001

### Check Logs:
- smtp2http logs will show incoming SMTP connections
- FastAPI logs will show POST requests to `/inbound-email`
- Check the Streamlit frontend for processed emails

## Next Steps
1. Set up Gmail filters for automatic processing
2. Configure a forwarding service for production use
3. Set up monitoring and alerts for the email processing pipeline 