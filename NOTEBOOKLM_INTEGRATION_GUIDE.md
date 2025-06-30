# NotebookLM Integration Guide for Email RAG

## Overview

This guide shows how to deploy your Email RAG system to Cloud Run with full NotebookLM integration using your existing Google Cloud project (`emailrag99`).

## Prerequisites

✅ **Already Set Up:**
- Google Cloud Project: `emailrag99`
- Region: `us-central1`
- NotebookLM Connection: `projects/emailrag99/locations/us-central1/connections/notebooklm`

## Quick Deployment

### 1. One-Command Deployment

```bash
chmod +x deploy_cloudrun_notebooklm.sh
./deploy_cloudrun_notebooklm.sh
```

This script will:
- ✅ Use your existing project (`emailrag99`)
- ✅ Connect to your NotebookLM instance
- ✅ Deploy to Cloud Run FREE tier
- ✅ Set up all necessary APIs and permissions
- ✅ Create optimized configuration for serverless

### 2. What Gets Deployed

**Cloud Run Service:**
- **Name:** `email-rag-backend`
- **URL:** `https://email-rag-backend-xxxxx-uc.a.run.app`
- **Region:** `us-central1`
- **Tier:** FREE (2M requests/month, 360K vCPU-seconds/month)

**NotebookLM Integration:**
- **Connection:** `projects/emailrag99/locations/us-central1/connections/notebooklm`
- **Permissions:** AI Platform User role
- **APIs:** Cloud Run, Cloud Build, AI Platform, Notebooks

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gmail/IMAP    │───▶│  Cloud Run       │───▶│   NotebookLM    │
│   Forwarding    │    │  Email RAG API   │    │   Connection    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  /tmp Storage    │
                       │  (Ephemeral)     │
                       └──────────────────┘
```

## Key Features

### 🚀 Serverless Architecture
- **Cold Start Optimized:** Lazy loading of models
- **Memory Efficient:** 1GB RAM, CPU throttling enabled
- **Auto-scaling:** 0-1 instances based on demand
- **Free Tier:** $0/month for typical usage

### 🔗 NotebookLM Integration
- **Direct Connection:** Uses your existing NotebookLM instance
- **AI Platform Access:** Full integration with Google's AI services
- **Context Sharing:** Email data can be analyzed in NotebookLM
- **Real-time Processing:** Immediate email ingestion and indexing

### 📧 Email Processing
- **IMAP Support:** Direct email fetching
- **Forwarding Endpoint:** `/inbound-email` for webhook processing
- **Vector Search:** Semantic search across email content
- **RAG Queries:** Natural language questions about emails

## Configuration

### Environment Variables

The deployment automatically sets these environment variables:

```bash
NOMIC_INFERENCE_MODE=local          # Use local embedding model
ENVIRONMENT=production              # Production mode
DATA_DIR=/tmp/data                  # Ephemeral storage
PARSED_EMAILS_DIR=/tmp/data/parsed_emails
VECTOR_STORE_DIR=/tmp/data/vector_store
MAILDIR_DIR=/tmp/data/maildir
GOOGLE_CLOUD_PROJECT=emailrag99     # Your project
NOTEBOOKLM_CONNECTION=projects/emailrag99/locations/us-central1/connections/notebooklm
```

### API Keys Setup

After deployment, set your API keys:

```bash
# Set Cohere API key for embeddings
gcloud run services update email-rag-backend \
  --update-env-vars COHERE_API_KEY=your_cohere_key \
  --region=us-central1

# Set other API keys as needed
gcloud run services update email-rag-backend \
  --update-env-vars OPENAI_API_KEY=your_openai_key \
  --region=us-central1
```

## Usage Examples

### 1. Health Check

```bash
curl https://email-rag-backend-xxxxx-uc.a.run.app/health
```

### 2. RAG Query

```bash
curl -X POST https://email-rag-backend-xxxxx-uc.a.run.app/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What emails did I receive about project updates?",
    "label": "substack.com",
    "max_age_days": 30
  }'
```

### 3. Email Ingestion

```bash
# Forward emails to the endpoint
curl -X POST https://email-rag-backend-xxxxx-uc.a.run.app/inbound-email \
  -H "Content-Type: message/rfc822" \
  --data-binary @email.eml
```

### 4. NotebookLM Integration Test

```bash
python test_notebooklm_integration.py
```

## Monitoring & Management

### View Service Status

```bash
gcloud run services describe email-rag-backend --region=us-central1
```

### View Logs

```bash
gcloud logs read --filter resource.type=cloud_run_revision --limit 50
```

### Monitor Usage

```bash
# Check Cloud Run usage
gcloud run services list --region=us-central1

# Check NotebookLM connection
gcloud ai connections describe projects/emailrag99/locations/us-central1/connections/notebooklm
```

### Update Service

```bash
# Update environment variables
gcloud run services update email-rag-backend \
  --update-env-vars NEW_VAR=value \
  --region=us-central1

# Redeploy with new code
./deploy_cloudrun_notebooklm.sh
```

## Cost Analysis

### Free Tier Limits (Monthly)
- **Requests:** 2,000,000
- **vCPU-seconds:** 360,000 (100 hours)
- **GiB-seconds:** 180,000 (50 hours)
- **Network egress:** 1GB

### Typical Usage (Personal Email)
- **Daily emails:** 50-100
- **Monthly requests:** ~3,000
- **Storage:** Ephemeral (no cost)
- **Cost:** $0/month ✅

### If You Exceed Free Tier
- **Additional requests:** $0.40 per million
- **Additional vCPU-seconds:** $0.00002400 per second
- **Additional GiB-seconds:** $0.00000250 per second
- **Network egress:** $0.12 per GB

## Troubleshooting

### Common Issues

**1. Cold Start Timeouts**
```bash
# Increase timeout
gcloud run services update email-rag-backend \
  --timeout=600 \
  --region=us-central1
```

**2. Memory Issues**
```bash
# Increase memory
gcloud run services update email-rag-backend \
  --memory=2Gi \
  --region=us-central1
```

**3. NotebookLM Connection Issues**
```bash
# Check connection status
gcloud ai connections describe projects/emailrag99/locations/us-central1/connections/notebooklm

# Recreate connection if needed
gcloud ai connections delete notebooklm --location=us-central1
gcloud ai connections create notebooklm --location=us-central1
```

**4. API Key Issues**
```bash
# Check environment variables
gcloud run services describe email-rag-backend --region=us-central1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
```

### Debug Mode

Enable debug logging:

```bash
gcloud run services update email-rag-backend \
  --update-env-vars LOG_LEVEL=DEBUG \
  --region=us-central1
```

## Next Steps

### 1. Set Up Email Forwarding

Configure your email provider to forward emails to:
```
https://email-rag-backend-xxxxx-uc.a.run.app/inbound-email
```

### 2. Test Integration

Run the test script:
```bash
python test_notebooklm_integration.py
```

### 3. Customize Prompts

Edit `rag/prompts.json` to customize RAG responses.

### 4. Scale Up (If Needed)

If you need more resources:
```bash
gcloud run services update email-rag-backend \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --region=us-central1
```

## Benefits of This Approach

✅ **Zero Cost:** Free tier covers typical usage
✅ **Serverless:** No server management required
✅ **NotebookLM Integration:** Full AI platform access
✅ **Auto-scaling:** Handles traffic spikes automatically
✅ **Google Cloud Native:** Leverages your existing infrastructure
✅ **Production Ready:** Optimized for reliability and performance

## Support

If you encounter issues:

1. **Check logs:** `gcloud logs read --filter resource.type=cloud_run_revision`
2. **Verify project:** `gcloud config get-value project`
3. **Test connection:** `python test_notebooklm_integration.py`
4. **Check quotas:** Google Cloud Console → IAM & Admin → Quotas

Your Email RAG system is now fully integrated with NotebookLM and running on Google Cloud's free tier! 🎉 