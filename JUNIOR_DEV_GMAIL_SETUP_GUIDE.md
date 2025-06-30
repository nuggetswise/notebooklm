# Gmail Forwarding Setup Guide for Junior Developers

## 🎯 Objective
Set up automatic email forwarding from Gmail to your Email RAG system so that emails can be automatically processed and made searchable.

## 📋 Prerequisites
- A Gmail account
- Basic understanding of command line/terminal
- Python 3.7+ installed
- Access to your Email RAG system (running on localhost:8001)

## 🚀 Quick Start (Choose One Method)

### Method 1: IMAP Polling (Recommended for Beginners)
This method polls your Gmail account for new emails and forwards them automatically.

#### Step 1: Set up Gmail App Password
1. Go to your [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Go to **App passwords**
4. Select **Mail** and **Other (Custom name)**
5. Name it "Email RAG System"
6. **Copy the 16-character password** (you'll need this!)

#### Step 2: Configure Environment Variables
Create a `.env` file in your project root:
```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
GMAIL_LABEL=substackrag
RAG_API_URL=http://localhost:8001/inbound-email
```

#### Step 3: Install Dependencies
```bash
pip install python-dotenv requests
```

#### Step 4: Run the IMAP Forwarder
```bash
python poll_and_forward.py
```

#### Step 5: Set up Gmail Labels
1. In Gmail, create a label called "substackrag" (or whatever you set in GMAIL_LABEL)
2. Move emails you want to process into this label
3. The script will automatically forward all emails in this label

### Method 2: Gmail API (More Advanced)
This method uses Gmail's API for more precise control.

#### Step 1: Set up Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Desktop application**
6. Download the JSON credentials file
7. Rename it to `gmail_credentials.json` and place it in your project root

#### Step 2: Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

#### Step 3: Run the Gmail API Forwarder
```bash
python gmail_forwarder.py continuous
```

### Method 3: SMTP to HTTP Bridge (For Production)
This method uses an SMTP server that forwards emails to your HTTP API.

#### Step 1: Download smtp2http
```bash
# For macOS/Linux
curl -L -o smtp2http https://github.com/chrusty/smtp2http/releases/latest/download/smtp2http-darwin-amd64
chmod +x smtp2http
```

#### Step 2: Configure smtp2http
Create `smtp2http.yaml`:
```yaml
listen_addr: ":2525"
forward_url: "http://localhost:8001/inbound-email"
log_level: "info"
```

#### Step 3: Start smtp2http
```bash
./smtp2http --config smtp2http.yaml
```

#### Step 4: Set up Gmail Forwarding
1. In Gmail Settings → **Forwarding and POP/IMAP**
2. Add forwarding address: `your-server-ip:2525`
3. Verify the forwarding address

## 🔧 Testing Your Setup

### Test with a Sample Email
Create a test email file:
```bash
cat > test_email.eml << 'EOF'
From: test@gmail.com
To: your-email@gmail.com
Subject: Test Email for RAG System
Date: $(date -R)
Content-Type: text/plain

This is a test email for the RAG system.
EOF
```

Send it to your API:
```bash
curl -X POST http://localhost:8001/inbound-email \
  --data-binary @test_email.eml \
  --header "Content-Type: message/rfc822"
```

### Verify Processing
1. Check your RAG system at `http://localhost:8501`
2. Look for the test email in the interface
3. Try searching for content from the email

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "Authentication failed" (IMAP)
**Solution:**
- Double-check your app password (16 characters, no spaces)
- Ensure 2-Step Verification is enabled
- Try regenerating the app password

#### Issue: "Connection refused" (API)
**Solution:**
- Make sure your RAG system is running on port 8001
- Check if the API endpoint `/inbound-email` exists
- Verify firewall settings

#### Issue: "Gmail API credentials not found"
**Solution:**
- Ensure `gmail_credentials.json` is in the project root
- Verify the file contains valid OAuth 2.0 credentials
- Check file permissions

#### Issue: "No emails found"
**Solution:**
- Verify the Gmail label exists and contains emails
- Check the label name matches your configuration
- Ensure emails are actually in the specified label

### Debug Commands

#### Check Gmail Labels (IMAP)
```bash
python poll_and_forward.py debug
```

#### Test Gmail API Connection
```bash
python gmail_forwarder.py once
```

#### Check smtp2http Logs
```bash
./smtp2http --config smtp2http.yaml --log-level debug
```

## 📊 Monitoring

### Log Files
- `poll_and_forward.log` - IMAP forwarder logs
- `processed_imap_ids.txt` - List of processed emails
- `gmail_token.pickle` - Gmail API authentication token

### Key Metrics to Watch
- Number of emails processed per run
- Success/failure rates
- Processing time per email
- API response times

## 🔄 Automation

### Run as Background Service
```bash
# Using nohup
nohup python poll_and_forward.py > forwarder.log 2>&1 &

# Using systemd (Linux)
sudo systemctl enable email-rag-forwarder
sudo systemctl start email-rag-forwarder
```

### Cron Job (Check Every 5 Minutes)
```bash
# Add to crontab
*/5 * * * * cd /path/to/your/project && python poll_and_forward.py
```

## 🛡️ Security Best Practices

1. **Never commit credentials** - Use `.env` files and add them to `.gitignore`
2. **Use app passwords** - Don't use your main Gmail password
3. **Limit API scopes** - Only request necessary permissions
4. **Monitor logs** - Regularly check for unusual activity
5. **Use HTTPS** - In production, ensure all API calls use HTTPS

## 📚 Next Steps

1. **Set up monitoring** - Create alerts for failed forwards
2. **Add email filtering** - Only process specific types of emails
3. **Implement retry logic** - Handle temporary failures gracefully
4. **Add rate limiting** - Respect Gmail's API limits
5. **Create backup methods** - Have fallback forwarding options

## 🆘 Getting Help

### Check These First:
1. Read the logs in detail
2. Verify all configuration values
3. Test with a simple email first
4. Check if your RAG system is running

### Common Debug Questions:
- What error message are you seeing?
- Which method are you using (IMAP/API/SMTP)?
- Is your RAG system running and accessible?
- Have you set up the Gmail label correctly?

### Resources:
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [IMAP Protocol Reference](https://tools.ietf.org/html/rfc3501)
- [smtp2http Documentation](https://github.com/chrusty/smtp2http)

---

**Remember:** Start with Method 1 (IMAP) if you're new to this. It's the most straightforward and reliable for most use cases! 