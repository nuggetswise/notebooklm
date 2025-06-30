#!/bin/bash
# deploy_notebooknugget.sh - Deploy Email RAG to the existing notebooknugget service

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"
SERVICE_NAME="notebooknugget"

echo "🚀 Deploying Email RAG to existing Cloud Run service: $SERVICE_NAME"

# Check if gcloud is configured
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: gcloud not authenticated. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

# Deploy using source-based build to the existing service
echo "🚀 Deploying to existing Cloud Run service: $SERVICE_NAME"
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
  --set-env-vars="NOMIC_INFERENCE_MODE=local,ENVIRONMENT=production,DATA_DIR=/tmp/data,PARSED_EMAILS_DIR=/tmp/data/parsed_emails,VECTOR_STORE_DIR=/tmp/data/vector_store,MAILDIR_DIR=/tmp/data/maildir,PYTHONPATH=/app,PYTHONUNBUFFERED=1"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Your Email RAG system is available at:"
echo "   Service URL: $SERVICE_URL"
echo "   API Docs: $SERVICE_URL/docs"
echo "   Health Check: $SERVICE_URL/health"
echo ""
echo "📝 Next steps:"
echo "1. Test the deployment:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "2. Set your API keys (if needed):"
echo "   gcloud run services update $SERVICE_NAME --update-env-vars COHERE_API_KEY=your_key --region=$REGION"
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
echo "   gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --limit 50"

echo ""
echo "✅ Deployment successful! Your Email RAG system is now running on Cloud Run." 