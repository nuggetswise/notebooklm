# Production Deployment Guide

## Overview
This guide covers deploying your Email RAG system to production with forwardemail.net integration.

## Prerequisites
- ✅ ForwardEmail.net alias configured
- ✅ API keys for Cohere and other services
- ✅ Production server (VPS, cloud instance, etc.)
- ✅ Domain name (optional but recommended)

## 1. Server Setup

### Choose Your Platform
- **VPS**: DigitalOcean, Linode, Vultr, AWS EC2
- **Cloud**: Google Cloud, Azure, AWS
- **Home Server**: Raspberry Pi, dedicated server

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum
- **OS**: Ubuntu 20.04+ or Debian 11+

## 2. System Installation

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Dependencies
```bash
# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv git curl wget -y

# Install system dependencies for OCR and PDF processing
sudo apt install tesseract-ocr tesseract-ocr-eng poppler-utils -y

# Install smtp2http
curl -L https://github.com/axllent/smtp2http/releases/latest/download/smtp2http-linux-amd64.tar.gz | tar xz
sudo mv smtp2http /usr/local/bin/
sudo chmod +x /usr/local/bin/smtp2http
```

## 3. Application Deployment

### Clone Repository
```bash
git clone <your-repo-url> /opt/emailrag
cd /opt/emailrag
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Set Environment Variables
```bash
# Create production environment file
cat > .env << EOF
# API Keys
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///data/email_index.db

# Email Processing
MAX_AGE_DAYS=30
DATA_DIR=/opt/emailrag/data
PARSED_EMAILS_DIR=/opt/emailrag/data/parsed_emails
MAILDIR_DIR=/opt/emailrag/data/maildir
VECTOR_STORE_DIR=/opt/emailrag/data/vector_store

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=info
EOF
```

### Create Data Directories
```bash
mkdir -p data/{parsed_emails,maildir,vector_store}
chmod 755 data
```

## 4. ForwardEmail.net Configuration

### Configure Your Alias
1. Go to [ForwardEmail.net](https://forwardemail.net)
2. Create a new alias: `your-alias@yourdomain.com`
3. Set forwarding to: `http://your-server-ip:2525/inbound-email`
4. Enable "Include original email" option

### Update smtp2http Configuration
```bash
# Edit smtp2http.yaml for production
cat > smtp2http.yaml << EOF
# Production smtp2http configuration
listen_addr: ":2525"
forward_url: "http://localhost:8001/inbound-email"
log_level: "info"
timeout: 30s
max_size: "10MB"
EOF
```

## 5. Systemd Service Setup

### Create Backend Service
```bash
sudo tee /etc/systemd/system/emailrag-backend.service > /dev/null << EOF
[Unit]
Description=Email RAG Backend API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/emailrag
Environment=PATH=/opt/emailrag/venv/bin
ExecStart=/opt/emailrag/venv/bin/uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Create SMTP2HTTP Service
```bash
sudo tee /etc/systemd/system/smtp2http.service > /dev/null << EOF
[Unit]
Description=SMTP to HTTP Bridge
After=network.target emailrag-backend.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/emailrag
ExecStart=/usr/local/bin/smtp2http -config /opt/emailrag/smtp2http.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Create Frontend Service (Optional)
```bash
sudo tee /etc/systemd/system/emailrag-frontend.service > /dev/null << EOF
[Unit]
Description=Email RAG Frontend
After=network.target emailrag-backend.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/emailrag/frontend
Environment=PATH=/opt/emailrag/venv/bin
ExecStart=/opt/emailrag/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Set Permissions and Enable Services
```bash
# Set ownership
sudo chown -R www-data:www-data /opt/emailrag

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable emailrag-backend
sudo systemctl enable smtp2http
sudo systemctl enable emailrag-frontend

# Start services
sudo systemctl start emailrag-backend
sudo systemctl start smtp2http
sudo systemctl start emailrag-frontend
```

## 6. Firewall Configuration

### Configure UFW
```bash
sudo ufw allow ssh
sudo ufw allow 2525/tcp  # SMTP2HTTP
sudo ufw allow 8001/tcp  # Backend API
sudo ufw allow 8501/tcp  # Frontend (if needed)
sudo ufw enable
```

## 7. Nginx Reverse Proxy (Recommended)

### Install Nginx
```bash
sudo apt install nginx -y
```

### Create Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/emailrag << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Frontend (optional)
    location / {
        proxy_pass http://localhost:8501/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/emailrag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 8. SSL Certificate (Recommended)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

## 9. Monitoring and Logs

### View Service Logs
```bash
# Backend logs
sudo journalctl -u emailrag-backend -f

# SMTP2HTTP logs
sudo journalctl -u smtp2http -f

# Frontend logs
sudo journalctl -u emailrag-frontend -f
```

### Check Service Status
```bash
sudo systemctl status emailrag-backend
sudo systemctl status smtp2http
sudo systemctl status emailrag-frontend
```

## 10. Testing Your Setup

### Test Email Forwarding
1. Send a test email to your forwardemail.net alias
2. Check logs: `sudo journalctl -u smtp2http -f`
3. Verify email processing: `curl http://localhost:8001/status`

### Test API Endpoints
```bash
# Health check
curl http://localhost:8001/health

# Get email status
curl http://localhost:8001/status

# Test RAG query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "label": null}'
```

## 11. Backup Strategy

### Create Backup Script
```bash
cat > /opt/emailrag/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/emailrag"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database and data
tar -czf $BACKUP_DIR/emailrag_data_$DATE.tar.gz \
  /opt/emailrag/data \
  /opt/emailrag/.env

# Keep only last 7 days of backups
find $BACKUP_DIR -name "emailrag_data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: emailrag_data_$DATE.tar.gz"
EOF

chmod +x /opt/emailrag/backup.sh
```

### Set Up Automated Backups
```bash
# Add to crontab
echo "0 2 * * * /opt/emailrag/backup.sh" | sudo crontab -
```

## 12. Security Considerations

### Environment Security
- ✅ Use strong API keys
- ✅ Keep system updated
- ✅ Use firewall
- ✅ Enable SSL
- ✅ Regular backups

### Application Security
- ✅ Validate email inputs
- ✅ Rate limiting (consider adding)
- ✅ Input sanitization
- ✅ Log monitoring

## 13. Troubleshooting

### Common Issues

**Service won't start:**
```bash
sudo systemctl status emailrag-backend
sudo journalctl -u emailrag-backend -n 50
```

**Email not being processed:**
```bash
# Check SMTP2HTTP logs
sudo journalctl -u smtp2http -f

# Test endpoint directly
curl -X POST http://localhost:8001/inbound-email \
  -H "Content-Type: message/rfc822" \
  --data-binary @test_email.eml
```

**RAG pipeline issues:**
```bash
# Check API keys
grep COHERE_API_KEY /opt/emailrag/.env

# Test RAG endpoint
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## 14. Performance Optimization

### For High Volume
- Increase server resources
- Add Redis for caching
- Use PostgreSQL instead of SQLite
- Implement rate limiting
- Add monitoring (Prometheus/Grafana)

### Database Optimization
```bash
# Optimize SQLite database
sqlite3 /opt/emailrag/data/email_index.db "VACUUM;"
```

## 15. Next Steps

1. **Test thoroughly** with your forwardemail.net alias
2. **Monitor logs** for any issues
3. **Set up alerts** for system health
4. **Consider scaling** if needed
5. **Add monitoring** tools
6. **Document customizations**

## Support

If you encounter issues:
1. Check service logs
2. Verify configuration
3. Test endpoints individually
4. Check firewall settings
5. Verify forwardemail.net configuration

Your Email RAG system is now ready for production! 🚀 