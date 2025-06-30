# 🌐 GCP Deployment URLs for emailrag99

## 📋 Project Information
- **Project ID**: `emailrag99`
- **Region**: `us-central1` (recommended)
- **Services**: Cloud Run (Backend + Frontend)

---

## 🔗 User-Facing URLs

### **Option 1: Cloud Run Default URLs (Free)**

#### **Backend API (FastAPI)**
```
https://email-rag-backend-xxxxx-uc.a.run.app
```
**Example**: `https://email-rag-backend-abc123-uc.a.run.app`

#### **Frontend UI (Streamlit)**
```
https://email-rag-frontend-xxxxx-uc.a.run.app
```
**Example**: `https://email-rag-frontend-def456-uc.a.run.app`

#### **API Documentation**
```
https://email-rag-backend-xxxxx-uc.a.run.app/docs
```
**Example**: `https://email-rag-backend-abc123-uc.a.run.app/docs`

### **Option 2: Custom Domain URLs (Paid)**

#### **With Custom Domain**
```
Backend API: https://api.emailrag99.com
Frontend UI: https://app.emailrag99.com
API Docs: https://api.emailrag99.com/docs
```

#### **With Subdomain**
```
Backend API: https://emailrag99-api.yourdomain.com
Frontend UI: https://emailrag99-app.yourdomain.com
API Docs: https://emailrag99-api.yourdomain.com/docs
```

---

## 🚀 Deployment Commands

### **1. Deploy Backend (FastAPI)**
```bash
# Deploy to Cloud Run
gcloud run deploy email-rag-backend \
  --image gcr.io/emailrag99/email-rag-backend \
  --platform managed \
  --region us-central1 \
  --project emailrag99 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 1

# Output will show the URL like:
# Service URL: https://email-rag-backend-abc123-uc.a.run.app
```

### **2. Deploy Frontend (Streamlit)**
```bash
# Deploy to Cloud Run
gcloud run deploy email-rag-frontend \
  --image gcr.io/emailrag99/email-rag-frontend \
  --platform managed \
  --region us-central1 \
  --project emailrag99 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 1

# Output will show the URL like:
# Service URL: https://email-rag-frontend-def456-uc.a.run.app
```

---

## 🔧 URL Configuration

### **Environment Variables for Frontend**
```bash
# Set the backend URL in frontend environment
gcloud run services update email-rag-frontend \
  --update-env-vars BACKEND_URL=https://email-rag-backend-abc123-uc.a.run.app \
  --region us-central1 \
  --project emailrag99
```

### **Update Email Forwarding Configuration**
```bash
# Update Gmail forwarding to use new backend URL
# In your Gmail settings or forwarding script:
BACKEND_URL="https://email-rag-backend-abc123-uc.a.run.app/inbound-email"
```

---

## 🌍 Custom Domain Setup (Optional)

### **1. Map Custom Domain to Backend**
```bash
# Map custom domain to backend service
gcloud run domain-mappings create \
  --service email-rag-backend \
  --domain api.emailrag99.com \
  --region us-central1 \
  --project emailrag99
```

### **2. Map Custom Domain to Frontend**
```bash
# Map custom domain to frontend service
gcloud run domain-mappings create \
  --service email-rag-frontend \
  --domain app.emailrag99.com \
  --region us-central1 \
  --project emailrag99
```

### **3. DNS Configuration**
```bash
# Add these DNS records to your domain:
# Type: CNAME
# Name: api
# Value: ghs.googlehosted.com

# Type: CNAME  
# Name: app
# Value: ghs.googlehosted.com
```

---

## 📱 User Experience URLs

### **Primary User Interface**
```
Main App: https://email-rag-frontend-xxxxx-uc.a.run.app
```

### **API Access Points**
```
Health Check: https://email-rag-backend-xxxxx-uc.a.run.app/health
API Docs: https://email-rag-backend-xxxxx-uc.a.run.app/docs
Email Processing: https://email-rag-backend-xxxxx-uc.a.run.app/inbound-email
RAG Queries: https://email-rag-backend-xxxxx-uc.a.run.app/query
```

### **Admin/Developer URLs**
```
System Stats: https://email-rag-backend-xxxxx-uc.a.run.app/stats
Performance: https://email-rag-backend-xxxxx-uc.a.run.app/performance
Personas: https://email-rag-backend-xxxxx-uc.a.run.app/personas
Prompts: https://email-rag-backend-xxxxx-uc.a.run.app/prompts
```

---

## 🔒 Security & Access

### **Public Access (Default)**
- ✅ **Frontend**: Publicly accessible
- ✅ **Backend API**: Publicly accessible
- ✅ **API Documentation**: Publicly accessible

### **Restricted Access (Optional)**
```bash
# Remove public access
gcloud run services update email-rag-backend \
  --no-allow-unauthenticated \
  --region us-central1 \
  --project emailrag99

# Add IAM authentication
gcloud run services add-iam-policy-binding email-rag-backend \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker" \
  --region us-central1 \
  --project emailrag99
```

---

## 📊 URL Structure Summary

### **Default Cloud Run URLs**
```
Backend: https://email-rag-backend-{hash}-uc.a.run.app
Frontend: https://email-rag-frontend-{hash}-uc.a.run.app
```

### **Custom Domain URLs**
```
Backend: https://api.emailrag99.com
Frontend: https://app.emailrag99.com
```

### **Alternative Custom URLs**
```
Backend: https://emailrag99-api.yourdomain.com
Frontend: https://emailrag99-app.yourdomain.com
```

---

## 🎯 Quick Start URLs

### **For Users**
1. **Main App**: `https://email-rag-frontend-xxxxx-uc.a.run.app`
2. **API Docs**: `https://email-rag-backend-xxxxx-uc.a.run.app/docs`

### **For Developers**
1. **Backend API**: `https://email-rag-backend-xxxxx-uc.a.run.app`
2. **Health Check**: `https://email-rag-backend-xxxxx-uc.a.run.app/health`
3. **System Stats**: `https://email-rag-backend-xxxxx-uc.a.run.app/stats`

### **For Email Forwarding**
1. **Email Endpoint**: `https://email-rag-backend-xxxxx-uc.a.run.app/inbound-email`

---

## 🔄 URL Updates

### **After Deployment**
```bash
# Get the actual URLs after deployment
gcloud run services list --region us-central1 --project emailrag99

# Output will show:
# SERVICE              REGION       URL
# email-rag-backend    us-central1  https://email-rag-backend-abc123-uc.a.run.app
# email-rag-frontend   us-central1  https://email-rag-frontend-def456-uc.a.run.app
```

### **Update Configuration Files**
```bash
# Update your .env file with the new URLs
echo "BACKEND_URL=https://email-rag-backend-abc123-uc.a.run.app" >> .env
echo "FRONTEND_URL=https://email-rag-frontend-def456-uc.a.run.app" >> .env
```

---

## 🌐 URL Examples for emailrag99

### **Most Likely URLs (After Deployment)**
```
Backend: https://email-rag-backend-abc123-uc.a.run.app
Frontend: https://email-rag-frontend-def456-uc.a.run.app
API Docs: https://email-rag-backend-abc123-uc.a.run.app/docs
Health: https://email-rag-backend-abc123-uc.a.run.app/health
```

### **Custom Domain URLs (If You Set Up)**
```
Backend: https://api.emailrag99.com
Frontend: https://app.emailrag99.com
API Docs: https://api.emailrag99.com/docs
Health: https://api.emailrag99.com/health
```

---

## 🎉 Final User-Facing URLs

### **Primary User Interface**
```
🌐 Main App: https://email-rag-frontend-xxxxx-uc.a.run.app
📚 API Docs: https://email-rag-backend-xxxxx-uc.a.run.app/docs
🔍 Health Check: https://email-rag-backend-xxxxx-uc.a.run.app/health
```

### **Email Processing**
```
📧 Email Endpoint: https://email-rag-backend-xxxxx-uc.a.run.app/inbound-email
```

**Note**: The `xxxxx` part will be replaced with a unique hash generated by Cloud Run when you deploy. The actual URLs will be shown in the deployment output. 