# 🚀 GCP Setup Guide for Email RAG System

## 📋 Prerequisites
- **GCP Project ID**: `emailrag99`
- **Google Cloud CLI**: Installed and configured
- **Docker**: Installed (for building containers)
- **Domain**: Optional (for custom URLs)

---

## 🎯 Step-by-Step GCP Setup

### **Step 1: Enable Required APIs**

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com --project=emailrag99

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com --project=emailrag99

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com --project=emailrag99

# Enable Gmail API (for email integration)
gcloud services enable gmail.googleapis.com --project=emailrag99

# Enable Cloud Storage API (for file storage)
gcloud services enable storage.googleapis.com --project=emailrag99
```

### **Step 2: Set Up Authentication**

```bash
# Login to Google Cloud
gcloud auth login

# Set the project
gcloud config set project emailrag99

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Verify your configuration
gcloud config list
```

### **Step 3: Create Docker Images**

#### **Build Backend Image**
```bash
# Navigate to your project directory
cd /Users/singhm/emailragnew

# Build the backend Docker image
docker build -t gcr.io/emailrag99/email-rag-backend -f Dockerfile.backend .

# Push to Google Container Registry
docker push gcr.io/emailrag99/email-rag-backend
```

#### **Build Frontend Image**
```bash
# Build the frontend Docker image
docker build -t gcr.io/emailrag99/email-rag-frontend -f Dockerfile.frontend .

# Push to Google Container Registry
docker push gcr.io/emailrag99/email-rag-frontend
```

### **Step 4: Deploy to Cloud Run**

#### **Deploy Backend (FastAPI)**
```bash
gcloud run deploy email-rag-backend \
  --image gcr.io/emailrag99/email-rag-backend \
  --platform managed \
  --region us-central1 \
  --project emailrag99 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8001 \
  --set-env-vars="COHERE_API_KEY=your_cohere_key,GROQ_API_KEY=your_groq_key,GEMINI_API_KEY=your_gemini_key,OPENAI_API_KEY=your_openai_key"
```

#### **Deploy Frontend (Streamlit)**
```bash
gcloud run deploy email-rag-frontend \
  --image gcr.io/emailrag99/email-rag-frontend \
  --platform managed \
  --region us-central1 \
  --project emailrag99 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8501 \
  --set-env-vars="BACKEND_URL=https://email-rag-backend-xxxxx-uc.a.run.app"
```

### **Step 5: Get Your URLs**

```bash
# List all deployed services
gcloud run services list --region us-central1 --project emailrag99

# Output will show:
# SERVICE              REGION       URL
# email-rag-backend    us-central1  https://email-rag-backend-abc123-uc.a.run.app
# email-rag-frontend   us-central1  https://email-rag-frontend-def456-uc.a.run.app
```

### **Step 6: Update Frontend with Backend URL**

```bash
# Replace xxxxx with your actual backend hash
gcloud run services update email-rag-frontend \
  --update-env-vars BACKEND_URL=https://email-rag-backend-abc123-uc.a.run.app \
  --region us-central1 \
  --project emailrag99
```

---

## 🐳 Dockerfile Setup

### **Create Dockerfile.backend**
```dockerfile
# Dockerfile.backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingestion_api/ ./ingestion_api/
COPY rag/ ./rag/
COPY data/ ./data/

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "ingestion_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### **Create Dockerfile.frontend**
```dockerfile
# Dockerfile.frontend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

---

## 🔧 Environment Configuration

### **Create .env.gcp file**
```bash
# .env.gcp
COHERE_API_KEY=your_cohere_api_key
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Gmail Integration
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
GMAIL_LABEL=substackrag

# GCP Configuration
PROJECT_ID=emailrag99
REGION=us-central1
ENVIRONMENT=production
LOG_LEVEL=INFO

# Email Processing
MAX_AGE_DAYS=30
DEFAULT_LABEL=substack.com
```

### **Set Environment Variables in Cloud Run**
```bash
# Set environment variables for backend
gcloud run services update email-rag-backend \
  --update-env-vars-file .env.gcp \
  --region us-central1 \
  --project emailrag99
```

---

## 🌐 Custom Domain Setup (Optional)

### **Step 1: Map Custom Domain**
```bash
# Map custom domain to backend
gcloud run domain-mappings create \
  --service email-rag-backend \
  --domain api.emailrag99.com \
  --region us-central1 \
  --project emailrag99

# Map custom domain to frontend
gcloud run domain-mappings create \
  --service email-rag-frontend \
  --domain app.emailrag99.com \
  --region us-central1 \
  --project emailrag99
```

### **Step 2: Configure DNS**
Add these DNS records to your domain registrar:
```
Type: CNAME
Name: api
Value: ghs.googlehosted.com

Type: CNAME
Name: app
Value: ghs.googlehosted.com
```

---

## 📧 Gmail Integration Setup

### **Step 1: Create Gmail API Credentials**
```bash
# Go to Google Cloud Console
# Navigate to: APIs & Services > Credentials
# Create OAuth 2.0 Client ID for web application
# Download the JSON file as gmail-credentials.json
```

### **Step 2: Set Up Gmail Forwarding**
```bash
# Update your Gmail forwarding script with the new backend URL
# In poll_and_forward.py or gmail_forwarder.py:
RAG_API_URL = "https://email-rag-backend-abc123-uc.a.run.app/inbound-email"
```

### **Step 3: Test Email Processing**
```bash
# Test the email endpoint
curl -X POST https://email-rag-backend-abc123-uc.a.run.app/inbound-email \
  -H "Content-Type: message/rfc822" \
  --data-binary @test_email.eml
```

---

## 🔍 Monitoring & Logging

### **View Logs**
```bash
# View backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=email-rag-backend" --project=emailrag99

# View frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=email-rag-frontend" --project=emailrag99
```

### **Monitor Performance**
```bash
# Check service status
gcloud run services describe email-rag-backend --region=us-central1 --project=emailrag99

# View metrics in Google Cloud Console
# Navigate to: Cloud Run > email-rag-backend > Metrics
```

---

## 🔒 Security Configuration

### **Set Up IAM (Optional)**
```bash
# Remove public access (if needed)
gcloud run services update email-rag-backend \
  --no-allow-unauthenticated \
  --region us-central1 \
  --project emailrag99

# Add specific users
gcloud run services add-iam-policy-binding email-rag-backend \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker" \
  --region us-central1 \
  --project emailrag99
```

### **Set Up VPC (Optional)**
```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create emailrag99-connector \
  --network default \
  --region us-central1 \
  --range 10.8.0.0/28 \
  --project emailrag99

# Attach to Cloud Run service
gcloud run services update email-rag-backend \
  --vpc-connector emailrag99-connector \
  --region us-central1 \
  --project emailrag99
```

---

## 🚀 Deployment Script

### **Create deploy.sh**
```bash
#!/bin/bash
# deploy.sh

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"

echo "🚀 Deploying Email RAG System to GCP..."

# Build and push images
echo "📦 Building Docker images..."
docker build -t gcr.io/$PROJECT_ID/email-rag-backend -f Dockerfile.backend .
docker build -t gcr.io/$PROJECT_ID/email-rag-frontend -f Dockerfile.frontend .

echo "📤 Pushing images to Container Registry..."
docker push gcr.io/$PROJECT_ID/email-rag-backend
docker push gcr.io/$PROJECT_ID/email-rag-frontend

# Deploy backend
echo "🔧 Deploying backend..."
gcloud run deploy email-rag-backend \
  --image gcr.io/$PROJECT_ID/email-rag-backend \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8001

# Get backend URL
BACKEND_URL=$(gcloud run services describe email-rag-backend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

# Deploy frontend
echo "🎨 Deploying frontend..."
gcloud run deploy email-rag-frontend \
  --image gcr.io/$PROJECT_ID/email-rag-frontend \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8501 \
  --set-env-vars="BACKEND_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe email-rag-frontend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend: $BACKEND_URL"
echo "📚 API Docs: $BACKEND_URL/docs"
echo "🔍 Health: $BACKEND_URL/health"
```

### **Make it executable and run**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🧪 Testing Your Deployment

### **Test Health Check**
```bash
curl https://email-rag-backend-abc123-uc.a.run.app/health
```

### **Test API Documentation**
```bash
# Open in browser
open https://email-rag-backend-abc123-uc.a.run.app/docs
```

### **Test Frontend**
```bash
# Open in browser
open https://email-rag-frontend-def456-uc.a.run.app
```

### **Test Email Processing**
```bash
# Create a test email
cat > test_email.eml << 'EOF'
From: test@gmail.com
To: your-email@gmail.com
Subject: Test Email for RAG System
Date: $(date -R)
Content-Type: text/plain

This is a test email for the RAG system.
EOF

# Send to your API
curl -X POST https://email-rag-backend-abc123-uc.a.run.app/inbound-email \
  --data-binary @test_email.eml \
  --header "Content-Type: message/rfc822"
```

---

## 📊 Cost Monitoring

### **Set Up Billing Alerts**
```bash
# Go to Google Cloud Console
# Navigate to: Billing > Budgets & Alerts
# Create budget alert for $10/month
```

### **Monitor Usage**
```bash
# Check Cloud Run usage
gcloud run services list --region=us-central1 --project=emailrag99

# Check billing
gcloud billing accounts list
```

---

## 🎉 Final Checklist

### **✅ Pre-Deployment**
- [ ] GCP project `emailrag99` created
- [ ] Required APIs enabled
- [ ] gcloud CLI configured
- [ ] Docker installed
- [ ] API keys ready (Cohere, Groq, Gemini, OpenAI)

### **✅ Deployment**
- [ ] Docker images built and pushed
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed to Cloud Run
- [ ] Environment variables set
- [ ] URLs obtained and configured

### **✅ Post-Deployment**
- [ ] Health check passes
- [ ] Frontend loads correctly
- [ ] API documentation accessible
- [ ] Email processing tested
- [ ] Gmail integration configured

### **✅ Optional**
- [ ] Custom domain configured
- [ ] Monitoring set up
- [ ] Security configured
- [ ] Billing alerts set

---

## 🆘 Troubleshooting

### **Common Issues**

#### **1. Permission Denied**
```bash
# Ensure you have the right permissions
gcloud projects add-iam-policy-binding emailrag99 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.admin"
```

#### **2. Image Build Fails**
```bash
# Check Docker is running
docker ps

# Build with verbose output
docker build -t gcr.io/emailrag99/email-rag-backend -f Dockerfile.backend . --progress=plain
```

#### **3. Service Won't Start**
```bash
# Check logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=email-rag-backend" --project=emailrag99

# Check environment variables
gcloud run services describe email-rag-backend --region=us-central1 --project=emailrag99
```

#### **4. Cold Start Issues**
```bash
# Set minimum instances to 1 (will cost more)
gcloud run services update email-rag-backend \
  --min-instances 1 \
  --region us-central1 \
  --project emailrag99
```

---

**🎯 You're ready to deploy!** Follow the steps above to get your Email RAG system running on GCP with project ID `emailrag99`. 