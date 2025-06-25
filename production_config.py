#!/usr/bin/env python3
"""
Production Configuration for nuggetwise.io
Email RAG System Deployment
"""

import os
from pathlib import Path

# Domain Configuration
DOMAIN = "nuggetwise.io"
API_SUBDOMAIN = "api.nuggetwise.io"
FRONTEND_SUBDOMAIN = "rag.nuggetwise.io"
EMAIL_SUBDOMAIN = "emails.nuggetwise.io"

# Production URLs
PRODUCTION_CONFIG = {
    "development": {
        "rag_api_url": "http://localhost:8001/inbound-email",
        "frontend_url": "http://localhost:8501",
        "api_docs_url": "http://localhost:8001/docs"
    },
    "production": {
        "rag_api_url": f"https://{API_SUBDOMAIN}/inbound-email",
        "frontend_url": f"https://{FRONTEND_SUBDOMAIN}",
        "api_docs_url": f"https://{API_SUBDOMAIN}/docs"
    }
}

# Email Configuration
EMAIL_ALIASES = {
    "substack": f"substack@{DOMAIN}",
    "ai": f"ai@{DOMAIN}", 
    "newsletters": f"newsletters@{DOMAIN}",
    "general": f"emails@{DOMAIN}"
}

# Gmail Labels (for filtering)
GMAIL_LABELS = {
    "substack": "substackrag",
    "ai": "airag", 
    "newsletters": "newsletterrag",
    "general": "generalrag"
}

# Deployment Scripts
DEPLOYMENT_SCRIPTS = {
    "install_dependencies": [
        "sudo apt update",
        "sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx",
        "python3 -m venv .venv",
        "source .venv/bin/activate && pip install -r requirements.txt"
    ],
    "setup_nginx": [
        f"sudo cp nginx/api.{DOMAIN} /etc/nginx/sites-available/",
        f"sudo ln -s /etc/nginx/sites-available/api.{DOMAIN} /etc/nginx/sites-enabled/",
        "sudo nginx -t",
        "sudo systemctl reload nginx"
    ],
    "setup_ssl": [
        f"sudo certbot --nginx -d {API_SUBDOMAIN}",
        f"sudo certbot --nginx -d {FRONTEND_SUBDOMAIN}"
    ],
    "setup_systemd": [
        "sudo cp systemd/email-rag.service /etc/systemd/system/",
        "sudo systemctl daemon-reload",
        "sudo systemctl enable email-rag",
        "sudo systemctl start email-rag"
    ]
}

# Environment Variables Template
ENV_TEMPLATE = f"""
# Production Configuration for nuggetwise.io
GMAIL_EMAIL=mandipinder@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
GMAIL_LABEL=substackrag

# Production API URLs
RAG_API_URL=https://{API_SUBDOMAIN}/inbound-email
FRONTEND_URL=https://{FRONTEND_SUBDOMAIN}

# Database and Storage
DATA_DIR=/var/lib/email-rag
LOG_DIR=/var/log/email-rag

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS={API_SUBDOMAIN},{FRONTEND_SUBDOMAIN}

# Email Forwarding
SMTP2HTTP_URL=https://{API_SUBDOMAIN}/inbound-email
"""

def get_config(environment="development"):
    """Get configuration for specified environment."""
    return PRODUCTION_CONFIG.get(environment, PRODUCTION_CONFIG["development"])

def generate_nginx_config():
    """Generate nginx configuration for nuggetwise.io."""
    return f"""
# API Server Configuration
server {{
    listen 80;
    server_name {API_SUBDOMAIN};
    
    location / {{
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Health check endpoint
    location /health {{
        proxy_pass http://localhost:8001/health;
        access_log off;
    }}
}}

# Frontend Server Configuration  
server {{
    listen 80;
    server_name {FRONTEND_SUBDOMAIN};
    
    location / {{
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""

def generate_systemd_service():
    """Generate systemd service configuration."""
    return f"""
[Unit]
Description=Email RAG API Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/email-rag
Environment=PATH=/var/www/email-rag/.venv/bin
ExecStart=/var/www/email-rag/.venv/bin/uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

if __name__ == "__main__":
    print("🚀 Production Configuration for nuggetwise.io")
    print("=" * 50)
    
    # Create configuration files
    config_dir = Path("production")
    config_dir.mkdir(exist_ok=True)
    
    # Generate nginx config
    with open(config_dir / "nginx.conf", "w") as f:
        f.write(generate_nginx_config())
    
    # Generate systemd service
    with open(config_dir / "email-rag.service", "w") as f:
        f.write(generate_systemd_service())
    
    # Generate environment template
    with open(config_dir / ".env.production", "w") as f:
        f.write(ENV_TEMPLATE)
    
    print("✅ Generated production configuration files:")
    print(f"  📁 {config_dir}/nginx.conf")
    print(f"  📁 {config_dir}/email-rag.service") 
    print(f"  📁 {config_dir}/.env.production")
    print()
    print("🌐 Your production URLs will be:")
    print(f"  🔗 API: https://{API_SUBDOMAIN}")
    print(f"  🔗 Frontend: https://{FRONTEND_SUBDOMAIN}")
    print(f"  🔗 Email Management: https://{EMAIL_SUBDOMAIN}") 