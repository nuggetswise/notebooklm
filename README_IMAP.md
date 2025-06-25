# Gmail IMAP Polling Script

This script polls Gmail via IMAP for Substack emails and forwards them to your RAG pipeline.

## 🚀 Quick Setup

### 1. Create Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Mac" (or your device)
3. Generate an app password
4. Copy the 16-character password

### 2. Configure Environment

```bash
# Copy the template
cp env.template .env

# Edit .env with your details
nano .env
```

Fill in:
- `GMAIL_EMAIL=mandipinder@gmail.com`
- `GMAIL_APP_PASSWORD=your_16_char_app_password`
- `GMAIL_LABEL=substackrag`
- `RAG_API_URL=http://localhost:8001/inbound-email`

### 3. Set up Gmail Filter

1. Go to Gmail Settings → Filters and Blocked Addresses
2. Create a new filter:
   - **From:** `substack.com`
   - **To:** `mandipinder@gmail.com`
3. Apply the filter:
   - ✅ Apply label: `substackrag`
   - ✅ Skip the Inbox
   - ✅ Mark as read (optional)

### 4. Test the Script

```bash
# Test once
python poll_and_forward.py once

# Test continuous mode (5-minute intervals)
python poll_and_forward.py continuous 300
```

## 📋 Usage

### Command Line Options

```bash
# Process emails once and exit
python poll_and_forward.py once

# Run continuously with 5-minute intervals
python poll_and_forward.py continuous 300

# Run continuously with 1-minute intervals
python poll_and_forward.py continuous 60
```

### Cron Setup

Add to your crontab (`crontab -e`):

```bash
# Run every 5 minutes
*/5 * * * * cd /Users/singhm/emailragnew && /Users/singhm/emailragnew/.venv/bin/python poll_and_forward.py once >> /Users/singhm/emailragnew/cron.log 2>&1
```

## 📊 Monitoring

### Log Files

- `poll_and_forward.log` - Main application logs
- `cron.log` - Cron job output (if using cron)
- `processed_imap_ids.txt` - List of processed email UIDs

### Check Status

```bash
# View recent logs
tail -f poll_and_forward.log

# Check processed emails
wc -l processed_imap_ids.txt

# Test connection
python poll_and_forward.py once
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify app password is correct
   - Ensure 2FA is enabled on Gmail
   - Check if app password is 16 characters

2. **Label Not Found**
   - Verify the label exists in Gmail
   - Check label name spelling
   - Script will fallback to INBOX if label not found

3. **API Connection Failed**
   - Verify RAG API is running
   - Check `RAG_API_URL` in `.env`
   - Test API endpoint manually

4. **No Emails Found**
   - Check Gmail filter is working
   - Verify emails are in the correct label
   - Check if emails are marked as unread

### Debug Mode

```bash
# Run with verbose logging
python -u poll_and_forward.py once 2>&1 | tee debug.log
```

## 🔒 Security Notes

- ✅ Uses Gmail App Passwords (not regular passwords)
- ✅ Stores processed email IDs locally
- ✅ Marks emails as read only after successful forwarding
- ✅ Includes proper error handling and logging
- ✅ Uses environment variables for sensitive data

## 📈 Performance

- **Memory Usage:** ~10-20MB
- **Network:** Minimal (only when emails found)
- **CPU:** Low (mostly idle when polling)
- **Storage:** Small log files and processed ID list

## 🔄 Integration

This script works alongside your existing:
- ✅ FastAPI email ingestion endpoint
- ✅ RAG pipeline with open-notebook format
- ✅ Streamlit frontend
- ✅ Existing Gmail API forwarder (different use case) 