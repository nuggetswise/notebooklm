#!/bin/bash
# deploy_cloudrun_free.sh - Cloud Run deployment optimized for FREE tier

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"
SERVICE_NAME="email-rag-backend"

echo "🚀 Deploying Email RAG to Cloud Run FREE tier..."

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

# Configure Docker for GCR
echo "🐳 Configuring Docker for Google Container Registry..."
gcloud auth configure-docker

# Create a simple Dockerfile for Cloud Run
echo "📝 Creating Cloud Run optimized Dockerfile..."
cat > Dockerfile.cloudrun << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements_production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY ingestion_api/ ./ingestion_api/
COPY rag/ ./rag/

# Create data directories in /tmp (Cloud Run allows writing to /tmp)
RUN mkdir -p /tmp/data/parsed_emails /tmp/data/vector_store /tmp/data/maildir

# Set environment variables for Cloud Run
ENV PYTHONPATH=/app
ENV NOMIC_INFERENCE_MODE=local
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/tmp/data
ENV PARSED_EMAILS_DIR=/tmp/data/parsed_emails
ENV VECTOR_STORE_DIR=/tmp/data/vector_store
ENV MAILDIR_DIR=/tmp/data/maildir

# Expose port (Cloud Run will set PORT environment variable)
EXPOSE 8080

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run the application with proper port handling
CMD exec uvicorn ingestion_api.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
EOF

# Build the container image
echo "📦 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME -f Dockerfile.cloudrun .

# Push to Container Registry
echo "📤 Pushing image to Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run with FREE tier optimizations
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8080 \
  --timeout 300 \
  --concurrency 80 \
  --cpu-throttling \
  --execution-environment gen2 \
  --set-env-vars="NOMIC_INFERENCE_MODE=local,ENVIRONMENT=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo "🎉 Cloud Run deployment complete!"
echo "🌐 Your Email RAG system is available at:"
echo "   Service URL: $SERVICE_URL"
echo "   API Docs: $SERVICE_URL/docs"
echo "   Health Check: $SERVICE_URL/health"
echo ""
echo "📝 Next steps:"
echo "1. Set your API keys:"
echo "   gcloud run services update $SERVICE_NAME --update-env-vars COHERE_API_KEY=your_key --region=$REGION"
echo ""
echo "2. Test the deployment:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "3. Set up email forwarding to:"
echo "   $SERVICE_URL/inbound-email"
echo ""
echo "💡 This deployment uses Cloud Run FREE tier:"
echo "   ✅ 2 million requests/month"
echo "   ✅ 360,000 vCPU-seconds/month"
echo "   ✅ 180,000 GiB-seconds/month"
echo "   ✅ 1GB network egress/month"
echo "   ✅ $0/month for minimal usage!"
echo ""
echo "🔧 To monitor usage:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "📊 To view logs:"
echo "   gcloud logs read --filter resource.type=cloud_run_revision --limit 50"

# Clean up
rm -f Dockerfile.cloudrun

echo ""
echo "✅ Deployment successful! Your Email RAG system is now running on Cloud Run FREE tier." 