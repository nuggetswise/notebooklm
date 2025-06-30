#!/bin/bash
# deploy_cloudrun_source.sh - Cloud Run deployment using source-based build (no Docker build needed)

set -e

PROJECT_ID="emailrag99"
REGION="us-central1"
SERVICE_NAME="email-rag-backend"

echo "🚀 Deploying Email RAG to Cloud Run using source-based build..."

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
gcloud services enable source.googleapis.com --project=$PROJECT_ID

# Create Cloud Run service configuration
echo "📝 Creating Cloud Run service configuration..."
cat > service.yaml << 'EOF'
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: email-rag-backend
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/email-rag-backend
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: PYTHONPATH
          value: "/app"
        - name: NOMIC_INFERENCE_MODE
          value: "local"
        - name: ENVIRONMENT
          value: "production"
        - name: PYTHONUNBUFFERED
          value: "1"
        - name: DATA_DIR
          value: "/tmp/data"
        - name: PARSED_EMAILS_DIR
          value: "/tmp/data/parsed_emails"
        - name: VECTOR_STORE_DIR
          value: "/tmp/data/vector_store"
        - name: MAILDIR_DIR
          value: "/tmp/data/maildir"
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
EOF

# Create .gcloudignore file
echo "📝 Creating .gcloudignore file..."
cat > .gcloudignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database files
*.db
*.sqlite
*.sqlite3

# Vector store files
data/vector_store/
*.bin
*.pkl

# Email data
data/parsed_emails/
data/maildir/

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Test files
test_*.py
*_test.py
test_*.eml

# Backup files
*.bak
*.backup

# Jupyter Notebooks
.ipynb_checkpoints
*.ipynb

# Git
.git/
.gitignore

# Documentation
*.md
docs/

# Deployment files
Dockerfile*
docker-compose*
deploy_*.sh
EOF

# Deploy using source-based build
echo "🚀 Deploying to Cloud Run using source-based build..."
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
rm -f service.yaml .gcloudignore

echo ""
echo "✅ Deployment successful! Your Email RAG system is now running on Cloud Run FREE tier." 