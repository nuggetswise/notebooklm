#!/bin/bash

# Email RAG System - Production Setup Script
# This script helps set up the Email RAG system for production deployment

set -e  # Exit on any error

echo "🚀 Email RAG System - Production Setup"
echo "======================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if we're in the right directory
if [ ! -f "ingestion_api/main.py" ]; then
    print_error "Please run this script from the Email RAG project root directory"
    exit 1
fi

print_status "Starting production setup..."

# Step 1: Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install system dependencies
print_status "Installing system dependencies..."
sudo apt install python3 python3-pip python3-venv git curl wget nginx certbot python3-certbot-nginx -y
sudo apt install tesseract-ocr tesseract-ocr-eng poppler-utils -y
print_success "System dependencies installed"

# Step 3: Install smtp2http
print_status "Installing smtp2http..."
if [ ! -f "/usr/local/bin/smtp2http" ]; then
    curl -L https://github.com/axllent/smtp2http/releases/latest/download/smtp2http-linux-amd64.tar.gz | tar xz
    sudo mv smtp2http /usr/local/bin/
    sudo chmod +x /usr/local/bin/smtp2http
    print_success "smtp2http installed"
else
    print_warning "smtp2http already installed"
fi

# Step 4: Create virtual environment
print_status "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 5: Install Python dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Step 6: Create data directories
print_status "Creating data directories..."
mkdir -p data/{parsed_emails,maildir,vector_store}
chmod 755 data
print_success "Data directories created"

# Step 7: Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# API Keys - PLEASE UPDATE THESE WITH YOUR ACTUAL KEYS
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///data/email_index.db

# Email Processing
MAX_AGE_DAYS=30
DATA_DIR=$(pwd)/data
PARSED_EMAILS_DIR=$(pwd)/data/parsed_emails
MAILDIR_DIR=$(pwd)/data/maildir
VECTOR_STORE_DIR=$(pwd)/data/vector_store

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=info
EOF
    print_success "Environment file created"
    print_warning "Please edit .env file with your actual API keys"
else
    print_warning "Environment file already exists"
fi

# Step 8: Update smtp2http configuration
print_status "Updating smtp2http configuration..."
cat > smtp2http.yaml << EOF
# Production smtp2http configuration
listen_addr: ":2525"
forward_url: "http://localhost:8001/inbound-email"
log_level: "info"
timeout: 30s
max_size: "10MB"
EOF
print_success "smtp2http configuration updated"

# Step 9: Create systemd services
print_status "Creating systemd services..."

# Backend service
sudo tee /etc/systemd/system/emailrag-backend.service > /dev/null << EOF
[Unit]
Description=Email RAG Backend API
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# SMTP2HTTP service
sudo tee /etc/systemd/system/smtp2http.service > /dev/null << EOF
[Unit]
Description=SMTP to HTTP Bridge
After=network.target emailrag-backend.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/smtp2http -config $(pwd)/smtp2http.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
sudo tee /etc/systemd/system/emailrag-frontend.service > /dev/null << EOF
[Unit]
Description=Email RAG Frontend
After=network.target emailrag-backend.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)/frontend
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd services created"

# Step 10: Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable emailrag-backend
sudo systemctl enable smtp2http
sudo systemctl enable emailrag-frontend

# Start services
sudo systemctl start emailrag-backend
sleep 3
sudo systemctl start smtp2http
sleep 2
sudo systemctl start emailrag-frontend

print_success "Services started"

# Step 11: Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 2525/tcp  # SMTP2HTTP
sudo ufw allow 8001/tcp  # Backend API
sudo ufw allow 8501/tcp  # Frontend
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
print_success "Firewall configured"

# Step 12: Create backup script
print_status "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$(dirname "$0")/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database and data
tar -czf $BACKUP_DIR/emailrag_data_$DATE.tar.gz \
  data \
  .env

# Keep only last 7 days of backups
find $BACKUP_DIR -name "emailrag_data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: emailrag_data_$DATE.tar.gz"
EOF

chmod +x backup.sh
print_success "Backup script created"

# Step 13: Test the setup
print_status "Testing the setup..."
sleep 5

# Test backend health
if curl -s http://localhost:8001/health > /dev/null; then
    print_success "Backend API is running"
else
    print_error "Backend API is not responding"
fi

# Test frontend
if curl -s http://localhost:8501 > /dev/null; then
    print_success "Frontend is running"
else
    print_error "Frontend is not responding"
fi

# Check service status
print_status "Checking service status..."
sudo systemctl status emailrag-backend --no-pager -l
echo
sudo systemctl status smtp2http --no-pager -l
echo
sudo systemctl status emailrag-frontend --no-pager -l

echo
echo "🎉 Production setup completed!"
echo "=============================="
echo
echo "📋 Next steps:"
echo "1. Edit .env file with your actual API keys"
echo "2. Configure your forwardemail.net alias to point to: http://$(curl -s ifconfig.me):2525/inbound-email"
echo "3. Test email forwarding by sending an email to your alias"
echo "4. Access your system:"
echo "   - Backend API: http://localhost:8001"
echo "   - Frontend UI: http://localhost:8501"
echo "   - API Docs: http://localhost:8001/docs"
echo
echo "📚 Useful commands:"
echo "  - View logs: sudo journalctl -u emailrag-backend -f"
echo "  - Restart services: sudo systemctl restart emailrag-backend"
echo "  - Check status: sudo systemctl status emailrag-backend"
echo "  - Create backup: ./backup.sh"
echo
echo "🔧 Optional: Set up Nginx reverse proxy and SSL (see PRODUCTION_DEPLOYMENT.md)"
echo
print_success "Setup complete! Your Email RAG system is ready for production." 