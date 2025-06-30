#!/bin/bash
# deploy_simple_test.sh - Deploy simple test version to verify Cloud Run works

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"
SERVICE_NAME="notebooknugget"

echo "🚀 Deploying simple test version to Cloud Run service: $SERVICE_NAME"

# Check if gcloud is configured
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: gcloud not authenticated. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Deploy the simple test version
echo "🚀 Deploying simple test version..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 1 \
  --min-instances 0 \
  --port 8080 \
  --timeout 300 \
  --concurrency 80 \
  --cpu-throttling \
  --execution-environment gen2 \
  --set-env-vars="ENVIRONMENT=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo "🎉 Simple test deployment complete!"
echo "🌐 Your test API is available at:"
echo "   Service URL: $SERVICE_URL"
echo "   Health Check: $SERVICE_URL/health"
echo "   Test Endpoint: $SERVICE_URL/test"
echo ""
echo "📝 Testing the deployment:"
echo "   curl $SERVICE_URL/health"
echo "   curl $SERVICE_URL/test"
echo ""
echo "✅ If this works, we can then deploy the full Email RAG application."

echo ""
echo "✅ Simple test deployment successful!" 