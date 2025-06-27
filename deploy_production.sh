#!/bin/bash

# Production Deployment Script for Email RAG System
# This script sets up the system for production deployment

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements_production.txt" ]; then
    print_error "requirements_production.txt not found. Please run this script from the project root."
    exit 1
fi

print_status "Setting up production environment..."

# 1. Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv_production
source venv_production/bin/activate

# 2. Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# 3. Install production dependencies
print_status "Installing production dependencies..."
pip install -r requirements_production.txt

# 4. Create necessary directories
print_status "Creating data directories..."
mkdir -p data/parsed_emails
mkdir -p data/maildir
mkdir -p data/vector_store
mkdir -p logs

# 5. Set proper permissions
print_status "Setting permissions..."
chmod 755 data
chmod 755 logs

# 6. Check if .env exists, if not create from template
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        print_warning "Please edit .env file with your actual API keys before starting the system."
    else
        print_error "env.template not found. Please create .env file manually."
    fi
fi

# 7. Test the installation
print_status "Testing installation..."
python -c "
import fastapi
import uvicorn
import cohere
import groq
import google.generativeai as genai
import streamlit
print('✅ All core dependencies installed successfully!')
"

# 8. Create production startup script
print_status "Creating production startup script..."
cat > start_production.sh << 'EOF'
#!/bin/bash

# Production startup script
set -e

echo "🚀 Starting Email RAG System in production mode..."

# Activate virtual environment
source venv_production/bin/activate

# Set production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Start the backend API
echo "Starting backend API..."
uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001 --workers 2 &

# Wait a moment for backend to start
sleep 3

# Start the frontend
echo "Starting frontend..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &

echo "✅ Email RAG System started successfully!"
echo "Backend API: http://localhost:8001"
echo "Frontend: http://localhost:8501"
echo "API Docs: http://localhost:8001/docs"

# Keep the script running
wait
EOF

chmod +x start_production.sh

# 9. Create systemd service files (optional)
print_status "Creating systemd service files..."
sudo tee /etc/systemd/system/emailrag-backend.service > /dev/null << EOF
[Unit]
Description=Email RAG Backend API
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv_production/bin
ExecStart=$(pwd)/venv_production/bin/uvicorn ingestion_api.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/emailrag-frontend.service > /dev/null << EOF
[Unit]
Description=Email RAG Frontend
After=network.target emailrag-backend.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv_production/bin
ExecStart=$(pwd)/venv_production/bin/streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 10. Create health check script
print_status "Creating health check script..."
cat > health_check.sh << 'EOF'
#!/bin/bash

# Health check script
echo "🔍 Checking system health..."

# Check backend
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is not responding"
fi

# Check frontend
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

# Check disk space
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️ Disk usage: ${DISK_USAGE}% (high)"
fi
EOF

chmod +x health_check.sh

print_status "Production deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: ./start_production.sh"
echo "3. Or enable systemd services:"
echo "   sudo systemctl enable emailrag-backend"
echo "   sudo systemctl enable emailrag-frontend"
echo "   sudo systemctl start emailrag-backend"
echo "   sudo systemctl start emailrag-frontend"
echo ""
echo "🔍 Health check: ./health_check.sh"
echo "📊 Logs: journalctl -u emailrag-backend -f"
echo ""
print_status "Deployment complete! 🎉" 