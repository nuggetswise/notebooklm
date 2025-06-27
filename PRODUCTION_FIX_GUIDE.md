# 🚨 Production Fix Guide

## Issue: "Backend modules not available: No module named 'fastapi'"

This error occurs when the production environment is missing required dependencies.

## 🔧 Quick Fix (Recommended)

### Option 1: Use the Fix Script
```bash
# Run the automated fix script
./fix_production.sh
```

### Option 2: Manual Fix
```bash
# 1. Create virtual environment
python3 -m venv venv_production
source venv_production/bin/activate

# 2. Install dependencies
pip install -r requirements_production.txt

# 3. Test installation
python -c "import fastapi, groq, cohere; print('✅ All dependencies installed!')"
```

## 🚀 Complete Production Deployment

### Step 1: Run Full Deployment Script
```bash
# This will set up everything for production
./deploy_production.sh
```

### Step 2: Configure Environment
```bash
# Edit your .env file with API keys
nano .env
```

Required API keys:
- `COHERE_API_KEY`
- `GROQ_API_KEY` 
- `GEMINI_API_KEY` (optional)
- `OPENAI_API_KEY` (optional)

### Step 3: Start the System
```bash
# Option A: Manual start
./start_production.sh

# Option B: Systemd services (recommended for production)
sudo systemctl enable emailrag-backend
sudo systemctl enable emailrag-frontend
sudo systemctl start emailrag-backend
sudo systemctl start emailrag-frontend
```

## 📋 What Each Script Does

### `fix_production.sh`
- Installs missing dependencies
- Tests the installation
- Quick fix for immediate issues

### `deploy_production.sh`
- Creates production virtual environment
- Installs all dependencies
- Sets up systemd services
- Creates startup scripts
- Sets proper permissions

### `start_production.sh`
- Starts backend API with multiple workers
- Starts frontend in headless mode
- Runs both services in background

## 🔍 Health Check

```bash
# Check system health
./health_check.sh

# Check service status
sudo systemctl status emailrag-backend
sudo systemctl status emailrag-frontend

# View logs
sudo journalctl -u emailrag-backend -f
sudo journalctl -u emailrag-frontend -f
```

## 🌐 Access Points

Once running:
- **Frontend**: http://your-server-ip:8501
- **Backend API**: http://your-server-ip:8001
- **API Docs**: http://your-server-ip:8001/docs
- **Health Check**: http://your-server-ip:8001/health

## 🛠️ Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   sudo lsof -ti:8001 | xargs kill -9
   sudo lsof -ti:8501 | xargs kill -9
   ```

2. **Permission denied**
   ```bash
   chmod +x *.sh
   sudo chown -R $USER:$USER .
   ```

3. **Virtual environment not activated**
   ```bash
   source venv_production/bin/activate
   ```

4. **Missing API keys**
   ```bash
   cp env.template .env
   # Edit .env with your actual API keys
   ```

### Dependency Issues:

If you get specific import errors:

```bash
# Install specific missing packages
pip install fastapi uvicorn groq cohere google-generativeai streamlit

# Or reinstall all dependencies
pip install -r requirements_production.txt --force-reinstall
```

## 📊 Monitoring

### Check System Resources:
```bash
# CPU and memory usage
htop

# Disk usage
df -h

# Process status
ps aux | grep -E "(uvicorn|streamlit)"
```

### Log Monitoring:
```bash
# Real-time logs
tail -f logs/app.log

# System logs
sudo journalctl -u emailrag-backend -f
```

## 🔒 Security Considerations

1. **Firewall**: Only expose necessary ports
   ```bash
   sudo ufw allow 8001
   sudo ufw allow 8501
   ```

2. **API Keys**: Never commit .env file
   ```bash
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

3. **HTTPS**: Use reverse proxy for production
   ```bash
   # Example with nginx
   sudo apt install nginx
   # Configure nginx for SSL termination
   ```

## ✅ Success Checklist

- [ ] All dependencies installed
- [ ] Virtual environment activated
- [ ] API keys configured in .env
- [ ] Backend API responding on port 8001
- [ ] Frontend accessible on port 8501
- [ ] Health check passing
- [ ] Email processing working
- [ ] RAG queries working

## 🆘 Emergency Recovery

If everything breaks:

```bash
# 1. Stop all services
sudo systemctl stop emailrag-backend emailrag-frontend

# 2. Clean environment
rm -rf venv_production

# 3. Reinstall from scratch
./deploy_production.sh

# 4. Restart services
sudo systemctl start emailrag-backend emailrag-frontend
```

## 📞 Support

If you continue to have issues:

1. Check the logs: `sudo journalctl -u emailrag-backend -f`
2. Verify API keys are set correctly
3. Ensure all dependencies are installed
4. Check system resources (CPU, memory, disk)

---

**Remember**: Always test in a staging environment before deploying to production! 🎯 