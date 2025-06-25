#!/bin/bash

# Email RAG System - Server Information Script
# This script helps you get the information needed for email forwarding setup

echo "🌐 Email RAG System - Server Information"
echo "========================================"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get public IP
echo -e "${BLUE}📡 Getting your server's public IP...${NC}"
PUBLIC_IP=$(curl -s ifconfig.me)
echo -e "${GREEN}✅ Your server's public IP: ${YELLOW}$PUBLIC_IP${NC}"
echo

# Get local IP
echo -e "${BLUE}🏠 Getting your server's local IP...${NC}"
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}✅ Your server's local IP: ${YELLOW}$LOCAL_IP${NC}"
echo

# Check if services are running
echo -e "${BLUE}🔍 Checking if Email RAG services are running...${NC}"

# Check backend
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend API is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API is not running${NC}"
fi

# Check frontend
if curl -s http://localhost:8501 > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend is not running${NC}"
fi

# Check smtp2http
if sudo systemctl is-active --quiet smtp2http; then
    echo -e "${GREEN}✅ SMTP2HTTP is running${NC}"
else
    echo -e "${YELLOW}⚠️  SMTP2HTTP is not running${NC}"
fi

echo

# Display forwarding configuration
echo -e "${BLUE}📧 Email Forwarding Configuration${NC}"
echo "======================================"
echo
echo -e "${YELLOW}For ForwardEmail.net:${NC}"
echo "1. Go to https://forwardemail.net"
echo "2. Create alias: mandipinder@yourdomain.com"
echo "3. Set forwarding to: http://$PUBLIC_IP:2525/inbound-email"
echo "4. Enable 'Include original email'"
echo
echo -e "${YELLOW}For your domain provider:${NC}"
echo "1. Log into your domain provider"
echo "2. Set up email forwarding from mandipinder@yourdomain.com"
echo "3. Forward to: http://$PUBLIC_IP:2525/inbound-email"
echo
echo -e "${BLUE}🔗 Access URLs${NC}"
echo "=============="
echo -e "Backend API: ${GREEN}http://$PUBLIC_IP:8001${NC}"
echo -e "Frontend UI: ${GREEN}http://$PUBLIC_IP:8501${NC}"
echo -e "API Docs: ${GREEN}http://$PUBLIC_IP:8001/docs${NC}"
echo
echo -e "${BLUE}🧪 Test Commands${NC}"
echo "================"
echo "Test backend health:"
echo -e "${YELLOW}curl http://$PUBLIC_IP:8001/health${NC}"
echo
echo "Test email status:"
echo -e "${YELLOW}curl http://$PUBLIC_IP:8001/status${NC}"
echo
echo "Test RAG query:"
echo -e "${YELLOW}curl -X POST http://$PUBLIC_IP:8001/query \\${NC}"
echo -e "${YELLOW}  -H \"Content-Type: application/json\" \\${NC}"
echo -e "${YELLOW}  -d '{\"query\": \"test query\"}'${NC}"
echo
echo -e "${GREEN}🎉 Your Email RAG system is ready for email forwarding!${NC}" 