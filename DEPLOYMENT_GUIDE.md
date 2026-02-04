# Panelin Agent V2 - Cloud Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Panelin Agent V2 API to Google Cloud Run. The deployment uses containerization with Docker, Artifact Registry for image storage, and Cloud Build for CI/CD automation.

## Architecture

```
GitHub Repository
      ↓
Cloud Build (CI/CD)
      ↓
Artifact Registry (Docker Images)
      ↓
Cloud Run (Containerized API)
      ↓
HTTPS Public Endpoint
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud Project** created
3. **gcloud CLI** installed and authenticated
4. **Docker** installed (for local testing)
5. **Git** configured with repository access

## Initial Setup

### 1. Install and Configure gcloud CLI

```bash
# Install gcloud (if not already installed)
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Initialize gcloud
gcloud init

# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Authenticate
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 2. Enable Required Google Cloud APIs

```bash
# Enable necessary APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com
```

### 3. Create Artifact Registry Repository

```bash
# Create Docker repository for storing container images
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin Agent V2 API container images"

# Verify creation
gcloud artifacts repositories list --location=us-central1
```

### 4. Create Service Account (Optional but Recommended)

```bash
# Create a dedicated service account for Cloud Run
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin API Cloud Run Service Account" \
  --description="Service account for running Panelin API on Cloud Run"

# Grant necessary permissions (adjust based on your needs)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 5. Set Up Secrets (if needed)

```bash
# Create secrets in Secret Manager
# Example: OpenAI API Key (if using LangChain features)
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY \
  --replication-policy="automatic" \
  --data-file=-

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Deployment Methods

### Method 1: Manual Deployment (Recommended for First Deployment)

#### Step 1: Build and Test Locally

```bash
# Build the Docker image locally
docker build -t panelin-api:local .

# Test locally
docker run -p 8080:8080 -e PORT=8080 panelin-api:local

# In another terminal, test the API
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

#### Step 2: Deploy to Cloud Run

```bash
# Deploy using source-based deployment (Cloud Run builds the image)
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated

# Note: Remove --allow-unauthenticated if you want IAM-based authentication
```

#### Step 3: Verify Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe panelin-api \
  --region us-central1 \
  --format 'value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test the deployed service
curl $SERVICE_URL/health
curl $SERVICE_URL/ready
curl "$SERVICE_URL/products?family=ISOPANEL"
```

#### Step 4: Update OpenAPI Schema

```bash
# Update the API code with the actual Cloud Run URL
# Edit: Copia de panelin_agent_v2/api.py
# Replace: https://panelin-api-XXXXXX-uc.a.run.app
# With: $SERVICE_URL

# Then redeploy
gcloud run deploy panelin-api \
  --source . \
  --region us-central1
```

### Method 2: Cloud Build Deployment (Automated CI/CD)

#### Step 1: Submit Build Manually

```bash
# Submit build using Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_REPO=panelin,_SERVICE=panelin-api
```

#### Step 2: Set Up Automated Triggers (GitHub Integration)

```bash
# Connect your GitHub repository
gcloud beta builds triggers create github \
  --repo-name=your-repo-name \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --description="Deploy Panelin API on push to main"

# For feature branches (e.g., staging)
gcloud beta builds triggers create github \
  --repo-name=your-repo-name \
  --repo-owner=your-github-username \
  --branch-pattern="^staging$" \
  --build-config=cloudbuild.yaml \
  --substitutions=_SERVICE=panelin-api-staging \
  --description="Deploy Panelin API staging on push to staging branch"
```

### Method 3: Pre-built Image Deployment

```bash
# Build and push image manually
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:v1.0.0 .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:v1.0.0

# Deploy from Artifact Registry
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:v1.0.0 \
  --region us-central1 \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated
```

## Configuration Options

### Resource Limits

Adjust based on your traffic and performance needs:

```bash
--memory 512Mi        # Options: 128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi
--cpu 1               # Options: 1, 2, 4, 6, 8 (requires >= 2Gi memory for >1 CPU)
--timeout 300         # Max request timeout in seconds (max: 3600)
--concurrency 80      # Max concurrent requests per instance (default: 80)
```

### Auto-scaling

```bash
--min-instances 0     # Scale to zero when no traffic (cost-effective)
--max-instances 10    # Maximum number of instances
```

For production with SLA requirements, consider:

```bash
--min-instances 1     # Keep 1 instance warm (reduce cold starts)
--max-instances 100   # Allow more scaling
```

### Access Control

**Public API (no authentication):**
```bash
--allow-unauthenticated
```

**IAM-authenticated (recommended for internal use):**
```bash
--no-allow-unauthenticated

# Grant access to specific users/service accounts
gcloud run services add-iam-policy-binding panelin-api \
  --region=us-central1 \
  --member="user:email@example.com" \
  --role="roles/run.invoker"
```

**Identity-Aware Proxy (IAP) for advanced auth:**
```bash
# Configure IAP through Google Cloud Console
# Console → Security → Identity-Aware Proxy → Cloud Run
```

### Environment Variables and Secrets

```bash
# Set environment variables
gcloud run services update panelin-api \
  --region us-central1 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=info"

# Mount secrets
gcloud run services update panelin-api \
  --region us-central1 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

## Monitoring and Observability

### View Logs

```bash
# Real-time logs
gcloud run services logs tail panelin-api --region us-central1

# Recent logs
gcloud run services logs read panelin-api --region us-central1 --limit 100
```

### Set Up Monitoring Alerts

1. Go to **Google Cloud Console → Monitoring → Alerting**
2. Create alert policies for:
   - Error rate > 5%
   - P95 latency > 1000ms
   - Request count anomalies
   - Instance count > threshold

### Enable Cloud Trace

```bash
# Install OpenTelemetry (add to requirements.txt)
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-gcp-trace

# Cloud Trace is automatically enabled for Cloud Run
# View traces: Console → Trace
```

## Cost Optimization

### Pricing Model

Cloud Run charges for:
- **CPU**: Only while processing requests
- **Memory**: Only while processing requests
- **Requests**: $0.40 per million requests (after free tier)
- **Networking**: Standard egress charges

### Free Tier (per month)

- 2 million requests
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds of compute time

### Cost-Saving Tips

1. **Scale to zero**: Use `--min-instances 0` for development/staging
2. **Right-size resources**: Start small (512Mi/1CPU) and scale up if needed
3. **Use CDN**: Cache static content with Cloud CDN
4. **Optimize cold starts**: Keep container image small (<500MB)
5. **Monitor usage**: Set budget alerts in Cloud Console

## Troubleshooting

### Container Fails to Start

```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log [BUILD_ID]

# Check Cloud Run logs
gcloud run services logs read panelin-api --region us-central1 --limit 50
```

### 503 Service Unavailable

- Check `/ready` endpoint is returning 200
- Verify all dependencies are included in the container
- Ensure sufficient memory allocation
- Check for cold start timeouts

### High Latency

- Enable Cloud Trace to identify bottlenecks
- Consider increasing CPU/memory
- Use `--min-instances 1` to avoid cold starts
- Implement caching for expensive operations

### Permission Errors

```bash
# Grant service account necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/[REQUIRED_ROLE]"
```

## Rollback and Blue-Green Deployment

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list --service panelin-api --region us-central1

# Rollback to specific revision
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-revisions=[REVISION_NAME]=100
```

### Blue-Green Deployment

```bash
# Deploy new version without traffic
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:v2.0.0 \
  --region us-central1 \
  --no-traffic

# Gradually shift traffic
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-revisions=panelin-api-v2=10,panelin-api-v1=90

# Complete migration
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-latest
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data
2. **Enable IAM authentication** for internal APIs
3. **Implement rate limiting** to prevent abuse
4. **Use HTTPS only** (automatic with Cloud Run)
5. **Regular dependency updates** to patch vulnerabilities
6. **Enable VPC connector** for private resource access
7. **Implement request validation** in the API
8. **Use least-privilege service accounts**

## Next Steps

1. ✅ Deploy to staging environment
2. ✅ Test all API endpoints
3. ✅ Set up monitoring and alerts
4. ✅ Configure custom domain (optional)
5. ✅ Set up CI/CD pipeline
6. ✅ Implement health checks and SLOs
7. ✅ Document API for consumers
8. ✅ Plan for disaster recovery

## Custom Domain Setup (Optional)

```bash
# Map custom domain
gcloud run services update panelin-api \
  --region us-central1

# Then in Cloud Console:
# Cloud Run → panelin-api → Manage Custom Domains
# Add your domain and follow DNS configuration steps
```

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Checklist

Before going to production:

- [ ] All health checks passing (`/health`, `/ready`)
- [ ] Secrets configured in Secret Manager
- [ ] Service account with least privilege created
- [ ] Resource limits appropriate for expected load
- [ ] Monitoring and alerting configured
- [ ] Error tracking enabled
- [ ] Backup and rollback strategy documented
- [ ] Load testing completed
- [ ] API documentation published
- [ ] Cost budgets and alerts set up
- [ ] Security review completed
- [ ] Disaster recovery plan documented

---

**Deployment Status**: Ready for Production ✅  
**Last Updated**: 2026-02-04  
**Version**: 2.0.0
