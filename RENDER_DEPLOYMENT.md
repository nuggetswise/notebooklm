# 🚀 Render Deployment Guide

## Quick Deploy to Render

### Step 1: Connect Your Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `emailragnew` repository

### Step 2: Configure the Service

**Basic Settings:**
- **Name**: `email-rag-system`
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `master`

**Build Settings:**
- **Build Command**: `./build.sh`
- **Start Command**: `./start_render.sh`

**Environment Variables:**
```
COHERE_API_KEY=your_cohere_api_key
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 3: Advanced Settings

**Resources:**
- **Instance Type**: `Standard` (1GB RAM, 0.5 CPU)
- **Auto-Deploy**: `Yes`

**Health Check:**
- **Health Check Path**: `/health`

## 🐌 Why Render Takes Time

### Heavy Dependencies:
- **sentence-transformers** (~500MB)
- **PyMuPDF** (~100MB)
- **faiss-cpu** (~50MB)
- **numpy** (~50MB)

### Build Process:
1. **System dependencies** (2-3 minutes)
2. **Python packages** (5-10 minutes)
3. **ML model downloads** (3-5 minutes)
4. **Total**: 10-18 minutes

## ⚡ Optimization Tips

### 1. Use Render-Optimized Requirements
```bash
# Use requirements_render.txt instead of requirements.txt
# Contains pre-built wheels and lighter versions
```

### 2. Enable Build Cache
- Render caches dependencies between builds
- Subsequent deployments are faster

### 3. Use Standard Instance
- Avoid free tier for ML workloads
- Standard tier has better performance

## 🔧 Troubleshooting

### Build Timeout (15+ minutes)
```bash
# Check build logs for specific package issues
# Common culprits: sentence-transformers, PyMuPDF
```

### Memory Issues
```bash
# Upgrade to Standard instance (1GB RAM)
# Reduce workers: --workers 1
```

### Import Errors
```bash
# Verify all dependencies in requirements_render.txt
# Check for missing system libraries
```

## 📊 Monitoring

### Health Check
```bash
# Your app should respond to:
curl https://your-app.onrender.com/health
```

### Logs
- View logs in Render dashboard
- Real-time log streaming available

### Performance
- Monitor CPU and memory usage
- Scale up if needed

## 🌐 Access Points

Once deployed:
- **API**: `https://your-app.onrender.com`
- **Health**: `https://your-app.onrender.com/health`
- **Docs**: `https://your-app.onrender.com/docs`

## 🔒 Security

### Environment Variables
- Never commit API keys
- Use Render's environment variable system
- Rotate keys regularly

### HTTPS
- Render provides automatic HTTPS
- No additional configuration needed

## 💰 Cost Optimization

### Free Tier Limitations:
- **Build time**: 15 minutes max
- **Memory**: 512MB
- **Sleep**: After 15 minutes of inactivity

### Standard Tier ($7/month):
- **Build time**: 45 minutes
- **Memory**: 1GB
- **Always on**: No sleep

## 🚀 Alternative: Railway Deployment

If Render is too slow, try Railway:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

## ✅ Success Checklist

- [ ] Repository connected to Render
- [ ] Build command: `./build.sh`
- [ ] Start command: `./start_render.sh`
- [ ] Environment variables set
- [ ] Health check passing
- [ ] API responding
- [ ] Logs showing no errors

## 🆘 Common Issues

### 1. Build Timeout
**Solution**: Use `requirements_render.txt` with lighter dependencies

### 2. Memory Issues
**Solution**: Upgrade to Standard instance

### 3. Import Errors
**Solution**: Check `requirements_render.txt` includes all dependencies

### 4. Port Issues
**Solution**: Use `$PORT` environment variable in start script

---

**Expected Build Time**: 10-18 minutes for first deployment
**Subsequent Deployments**: 3-5 minutes (with cache)

🎯 **Patience is key for the first deployment!** 