# Quick Deployment for mandipinder@gmail.com Email RAG

## What You're Getting
- **Personal Email RAG System** for mandipinder@gmail.com
- **Real-time email processing** via your domain forwarding
- **AI-powered Q&A** over your emails
- **Web interface** to query your email history

## Step 1: Choose Your Server

**Option A: VPS (Recommended)**
- DigitalOcean Droplet ($5-10/month)
- Linode Nanode ($5/month)
- Vultr VPS ($5/month)

**Option B: Home Server**
- Raspberry Pi 4 (8GB RAM)
- Old laptop/desktop

**Minimum Requirements:**
- 2GB RAM
- 10GB storage
- Ubuntu 20.04+ or Debian 11+

## Step 2: Deploy the System

### On Your Server:
```bash
# 1. Clone your Email RAG system
git clone <your-repo-url> /opt/emailrag
cd /opt/emailrag

# 2. Run the production setup script
chmod +x setup_production.sh
./setup_production.sh
```

### Update API Keys:
```bash
# Edit the .env file with your actual keys
nano .env

# Add your API keys:
COHERE_API_KEY=your_actual_cohere_key
OPENAI_API_KEY=your_actual_openai_key
```

## Step 3: Configure Email Forwarding

### Get Your Server's Public IP:
```bash
curl ifconfig.me
# Note this IP address
```

### Set Up Forwarding:

**If using ForwardEmail.net:**
1. Go to [ForwardEmail.net](https://forwardemail.net)
2. Create new alias: `mandipinder@yourdomain.com`
3. Set forwarding to: `http://YOUR_SERVER_IP:2525/inbound-email`
4. Enable "Include original email"

**If using your domain provider:**
1. Log into your domain provider
2. Go to email/DNS settings
3. Set up email forwarding from `mandipinder@yourdomain.com`
4. Forward to: `http://YOUR_SERVER_IP:2525/inbound-email`

## Step 4: Test Your Setup

### Send a Test Email:
1. Send email to `mandipinder@yourdomain.com`
2. Check if it's processed:
```bash
curl http://localhost:8001/status
```

### Access Your Email RAG:
- **Web Interface**: http://YOUR_SERVER_IP:8501
- **API Docs**: http://YOUR_SERVER_IP:8001/docs

## Step 5: Query Your Emails

### Via Web Interface:
1. Open http://YOUR_SERVER_IP:8501
2. Ask questions like:
   - "What emails did I get from John last week?"
   - "Find emails about project deadlines"
   - "What attachments did I receive this month?"

### Via API:
```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find emails about invoices", "label": null}'
```

## Step 6: Optional - Add Domain & SSL

### Set Up Domain:
1. Point your domain to your server IP
2. Configure Nginx (see PRODUCTION_DEPLOYMENT.md)
3. Add SSL certificate with Let's Encrypt

### Access via Domain:
- **Web Interface**: https://yourdomain.com
- **API**: https://yourdomain.com/api

## What Happens Next

1. **Emails arrive** → Forwarded to your server
2. **System processes** → Extracts text, metadata, attachments
3. **AI embeds** → Creates searchable vectors
4. **You query** → Get intelligent answers about your emails

## Monitoring

### Check System Status:
```bash
# View logs
sudo journalctl -u emailrag-backend -f

# Check service status
sudo systemctl status emailrag-backend
sudo systemctl status smtp2http
```

### Backup Your Data:
```bash
# Manual backup
./backup.sh

# Automatic daily backups (already set up)
```

## Troubleshooting

**Email not being processed:**
```bash
# Check SMTP2HTTP logs
sudo journalctl -u smtp2http -f

# Test endpoint directly
curl -X POST http://localhost:8001/inbound-email \
  -H "Content-Type: message/rfc822" \
  --data-binary @test_email.eml
```

**RAG not working:**
```bash
# Check API keys
grep COHERE_API_KEY .env

# Test RAG endpoint
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## Your Email RAG is Ready! 🎉

You now have:
- ✅ Personal email processing for mandipinder@gmail.com
- ✅ AI-powered search and Q&A over your emails
- ✅ Web interface to interact with your email data
- ✅ Real-time processing of new emails

**Start using it:**
1. Send emails to `mandipinder@yourdomain.com`
2. Access the web interface
3. Ask questions about your emails
4. Get intelligent answers powered by AI!

## Next Steps

1. **Test thoroughly** with your email forwarding
2. **Customize the interface** if needed
3. **Add more email accounts** if desired
4. **Set up monitoring** and alerts
5. **Scale up** if you get high email volume

Your personal Email RAG system is now live and ready to help you manage and query your emails intelligently! 🚀 