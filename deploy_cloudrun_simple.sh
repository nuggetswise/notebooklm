#!/bin/bash
# deploy_cloudrun_simple.sh - Simplest Cloud Run deployment using built-in Python runtime

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"
SERVICE_NAME="email-rag-backend"

echo "🚀 Deploying Email RAG to Cloud Run (simplest method)..."

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

# Create a simple requirements.txt for Cloud Run
echo "📝 Creating optimized requirements.txt..."
cat > requirements_cloudrun.txt << 'EOF'
# Core dependencies (minimal for Cloud Run)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.3
python-multipart==0.0.6
python-dotenv==1.0.0
requests==2.31.0
pytz==2024.1
psutil==5.9.8

# Email processing (minimal)
email-validator==2.1.0
beautifulsoup4==4.12.2
lxml==4.9.3

# Vector search and embeddings (optimized)
numpy==1.24.4
faiss-cpu==1.7.4
sentence-transformers==2.2.2
huggingface-hub==0.19.4
nomic==2.0.0

# LLM providers (only what you need)
cohere==4.37
groq==0.5.0
google-generativeai==0.3.2
openai==1.3.0

# Utilities (minimal)
pandas==2.0.3
tqdm==4.66.1
python-dateutil==2.8.2
EOF

# Create a simple main.py for Cloud Run
echo "📝 Creating Cloud Run optimized main.py..."
cat > main_cloudrun.py << 'EOF'
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app
from ingestion_api.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Deploy using the simplest method
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
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
  --set-env-vars="NOMIC_INFERENCE_MODE=local,ENVIRONMENT=production,DATA_DIR=/tmp/data,PARSED_EMAILS_DIR=/tmp/data/parsed_emails,VECTOR_STORE_DIR=/tmp/data/vector_store,MAILDIR_DIR=/tmp/data/maildir"

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

# Clean up temporary files
rm -f requirements_cloudrun.txt main_cloudrun.py

echo ""
echo "✅ Deployment successful! Your Email RAG system is now running on Cloud Run FREE tier." 