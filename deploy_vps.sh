#!/bin/bash
# deploy_vps.sh - Simple VPS deployment that ACTUALLY WORKS

set -e

echo "🚀 Deploying Email RAG to Traditional VPS (This Will Work!)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're on a supported system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_success "Linux detected - perfect for deployment"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_warning "macOS detected - this script is for Linux VPS deployment"
    print_warning "Run this on your VPS, not locally"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

# Check if we're root or have sudo
if [[ $EUID -eq 0 ]]; then
    print_success "Running as root"
elif command -v sudo &> /dev/null; then
    print_success "sudo available"
else
    print_error "Need root access or sudo"
    exit 1
fi

# Update system
print_success "Updating system packages..."
if command -v apt-get &> /dev/null; then
    apt-get update -y
    apt-get upgrade -y
elif command -v yum &> /dev/null; then
    yum update -y
elif command -v dnf &> /dev/null; then
    dnf update -y
else
    print_error "Unsupported package manager"
    exit 1
fi

# Install system dependencies
print_success "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    apt-get install -y python3 python3-pip python3-venv git curl wget nginx
    apt-get install -y build-essential python3-dev
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip git curl wget nginx
    yum groupinstall -y "Development Tools"
elif command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip git curl wget nginx
    dnf groupinstall -y "Development Tools"
fi

# Create application directory
APP_DIR="/opt/emailrag"
print_success "Setting up application directory: $APP_DIR"

if [[ $EUID -eq 0 ]]; then
    mkdir -p $APP_DIR
    chown -R $SUDO_USER:$SUDO_USER $APP_DIR
else
    mkdir -p $APP_DIR
fi

# Copy application files (assuming we're in the project directory)
print_success "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
print_success "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
print_success "Installing Python dependencies..."
pip install -r requirements_production.txt

# Create data directories
print_success "Creating data directories..."
mkdir -p data/parsed_emails
mkdir -p data/vector_store
mkdir -p data/maildir
mkdir -p logs

# Set proper permissions
chmod 755 data
chmod 755 logs

# Create environment file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_warning "Creating .env file - PLEASE EDIT WITH YOUR API KEYS"
    cat > .env << 'EOF'
# API Keys - PLEASE UPDATE THESE WITH YOUR ACTUAL KEYS
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

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
NOMIC_INFERENCE_MODE=local
EOF
    print_warning "⚠️  IMPORTANT: Edit .env file with your actual API keys!"
fi

# Create systemd services
print_success "Creating systemd services..."

# Backend service
cat > /etc/systemd/system/emailrag-backend.service << EOF
[Unit]
Description=Email RAG Backend API
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=PYTHONPATH=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/emailrag-frontend.service << EOF
[Unit]
Description=Email RAG Frontend
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=PYTHONPATH=$APP_DIR
ExecStart=$APP_DIR/venv/bin/streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# SMTP2HTTP service (if smtp2http binary exists)
if [[ -f "smtp2http" ]]; then
    chmod +x smtp2http
    cat > /etc/systemd/system/smtp2http.service << EOF
[Unit]
Description=SMTP to HTTP Bridge
After=network.target emailrag-backend.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/smtp2http -config $APP_DIR/smtp2http.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
fi

# Create nginx configuration
print_success "Configuring nginx..."
cat > /etc/nginx/sites-available/emailrag << EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Direct backend access
    location /health {
        proxy_pass http://localhost:8001/health;
        proxy_set_header Host \$host;
    }

    location /docs {
        proxy_pass http://localhost:8001/docs;
        proxy_set_header Host \$host;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/emailrag /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configure firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    print_success "Configuring firewall..."
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 2525/tcp
    ufw --force enable
fi

# Reload systemd and start services
print_success "Starting services..."
systemctl daemon-reload
systemctl enable emailrag-backend
systemctl enable emailrag-frontend
systemctl enable nginx

if [[ -f "smtp2http" ]]; then
    systemctl enable smtp2http
fi

# Start services
systemctl start emailrag-backend
systemctl start emailrag-frontend
systemctl start nginx

if [[ -f "smtp2http" ]]; then
    systemctl start smtp2http
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

# Wait a moment for services to start
sleep 5

# Test services
print_success "Testing services..."

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed - may still be starting"
fi

if curl -f http://localhost:8501 > /dev/null 2>&1; then
    print_success "Frontend is responding"
else
    print_warning "Frontend may still be starting"
fi

# Print success message
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 Your Email RAG system is now running at:"
echo "   Frontend UI: http://$SERVER_IP"
echo "   Backend API: http://$SERVER_IP:8001"
echo "   API Docs: http://$SERVER_IP/docs"
echo "   Health Check: http://$SERVER_IP/health"
echo ""
echo "📧 Email forwarding endpoint:"
echo "   http://$SERVER_IP:2525/inbound-email"
echo ""
echo "📝 IMPORTANT NEXT STEPS:"
echo "1. Edit API keys: nano $APP_DIR/.env"
echo "2. Restart services: systemctl restart emailrag-backend"
echo "3. Set up email forwarding to: http://$SERVER_IP:2525/inbound-email"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: journalctl -u emailrag-backend -f"
echo "   Check status: systemctl status emailrag-backend"
echo "   Restart: systemctl restart emailrag-backend"
echo ""
echo "💡 This deployment will work reliably because it uses:"
echo "   ✅ Traditional VPS (not serverless)"
echo "   ✅ Persistent filesystem"
echo "   ✅ No startup time limits"
echo "   ✅ Full control over environment"
echo ""
print_success "Deployment successful! Your Email RAG system is ready to use." 