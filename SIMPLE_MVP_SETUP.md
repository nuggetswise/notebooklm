# 🎯 Simple MVP: Parse Substack Emails from Gmail

**Goal**: Parse Substack newsletters from `mandipinder@gmail.com` using your existing IMAP polling script.

## 📋 **What You Have:**
- ✅ `mvp.nuggetwise.io` subdomain
- ✅ `mandipinder@gmail.com` with Substack emails
- ✅ IMAP polling script (`poll_and_forward.py`)
- ✅ FastAPI backend for processing emails

## 🚀 **Simple Setup (3 Steps):**

### **Step 1: Set Up Gmail Filter**
```bash
# In Gmail Settings → Filters and Blocked Addresses
# Create filter:
# From: substack.com
# To: mandipinder@gmail.com
# Apply: Label "substackrag" + Skip Inbox
```

### **Step 2: Configure IMAP Polling**
```bash
# Copy environment template
cp env.template .env

# Edit .env file
nano .env
```

**Fill in `.env`:**
```bash
GMAIL_EMAIL=mandipinder@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
GMAIL_LABEL=substackrag
RAG_API_URL=http://localhost:8001/inbound-email
```

### **Step 3: Run the System**
```bash
# Start your RAG API
python start_system.py

# In another terminal, run IMAP polling
python poll_and_forward.py continuous 300  # Check every 5 minutes
```

## 🔧 **Gmail App Password Setup:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Mac"
3. Generate 16-character password
4. Copy to your `.env` file

## 🧪 **Test It:**
```bash
# Test once
python poll_and_forward.py once

# Check logs
tail -f poll_and_forward.log

# View processed emails
curl http://localhost:8001/status
```

## 🎯 **That's It!**

Your system will:
- ✅ Poll Gmail every 5 minutes
- ✅ Find unread emails in "substackrag" label  
- ✅ Forward them to your RAG API
- ✅ Parse and store them
- ✅ Mark emails as read

**No domain setup needed!** Just localhost for now.

## 📊 **Monitor:**
```bash
# Check if emails are being processed
tail -f poll_and_forward.log

# View your RAG frontend
# Open: http://localhost:8501
```

**Simple and focused!** 🎯 