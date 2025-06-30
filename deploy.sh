#!/bin/bash
# deploy.sh - Automated GCP deployment script for Email RAG System

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"

echo "🚀 Deploying Email RAG System to GCP..."

# Check if gcloud is configured
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: gcloud not authenticated. Please run 'gcloud auth login' first."
    exit 1
fi

# Check if project exists
if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
    echo "❌ Error: Project $PROJECT_ID not found. Please create it first."
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable gmail.googleapis.com --project=$PROJECT_ID
gcloud services enable storage.googleapis.com --project=$PROJECT_ID

# Configure Docker for GCR
echo "🐳 Configuring Docker for Google Container Registry..."
gcloud auth configure-docker

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
  --port 8001 \
  --timeout 300 \
  --concurrency 80

# Get backend URL
BACKEND_URL=$(gcloud run services describe email-rag-backend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo "✅ Backend deployed at: $BACKEND_URL"

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
  --timeout 300 \
  --concurrency 80 \
  --set-env-vars="BACKEND_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe email-rag-frontend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo "✅ Frontend deployed at: $FRONTEND_URL"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Test health check
echo "🔍 Testing health check..."
if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "⚠️  Backend health check failed - service may still be starting"
fi

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend: $BACKEND_URL"
echo "📚 API Docs: $BACKEND_URL/docs"
echo "🔍 Health: $BACKEND_URL/health"
echo ""
echo "📝 Next steps:"
echo "1. Set your API keys in Cloud Run environment variables"
echo "2. Configure Gmail integration"
echo "3. Test email processing"
echo "4. Set up monitoring and billing alerts"
echo ""
echo "💡 To set environment variables, run:"
echo "gcloud run services update email-rag-backend --update-env-vars-file .env.gcp --region=$REGION --project=$PROJECT_ID" 