# Panelin Agent V2 - Cloud Deployment Guide

This guide documents how to deploy the Panelin Agent V2 API to Google Cloud Run.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────────┐     ┌──────────────┐ │
│  │ Cloud Build  │────>│ Artifact Registry│────>│  Cloud Run   │ │
│  │  (CI/CD)     │     │  (Docker Images) │     │  (Service)   │ │
│  └──────────────┘     └──────────────────┘     └──────┬───────┘ │
│                                                        │         │
│  ┌──────────────┐                              ┌──────▼───────┐ │
│  │Secret Manager│──────────────────────────────│  Panelin API │ │
│  │  (API Keys)  │                              │  Container   │ │
│  └──────────────┘                              └──────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                ▲
                                │ HTTPS
                                ▼
                    ┌──────────────────────┐
                    │    GPT Actions       │
                    │  (OpenAI Custom GPT) │
                    └──────────────────────┘
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** (for local testing)
4. **Project ID** - Create or select a GCP project

## Quick Start

### 1. Set up GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Configure gcloud
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=$REGION \
  --description="Panelin Agent Docker images"
```

### 3. Create Service Account (Least Privilege)

```bash
# Create service account
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin Cloud Run Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Store Secrets (Optional - if using OpenAI)

```bash
# Create secret
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 5. Deploy to Cloud Run

#### Option A: Direct Deploy (Recommended for first time)

```bash
gcloud run deploy panelin-api \
  --source . \
  --region $REGION \
  --service-account panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated
```

#### Option B: Using Cloud Build (CI/CD)

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

### 6. Get the Service URL

```bash
gcloud run services describe panelin-api --region=$REGION --format='value(status.url)'
```

The URL will look like: `https://panelin-api-xxxxx-uc.a.run.app`

### 7. Update OpenAPI Schema

Update `deployment_bundle/openapi.json` with your Cloud Run URL:

```json
"servers": [
  {
    "url": "https://panelin-api-xxxxx-uc.a.run.app",
    "description": "Cloud Run Production Server"
  }
]
```

## Local Testing

### Build and run locally with Docker

```bash
# Build image
docker build -t panelin-api:local .

# Run container
docker run -p 8080:8080 panelin-api:local

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

## Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/` | Root health check | `{"status": "healthy", ...}` |
| `/health` | Liveness probe | `{"status": "healthy", ...}` |
| `/ready` | Readiness probe | `{"ready": true, "checks": {...}}` |

## Monitoring

### View Logs

```bash
gcloud run logs read panelin-api --region=$REGION --limit=100
```

### Set up Alerts

```bash
# Create notification channel first (email, Slack, etc.)
# Then create alerting policy for error rate
gcloud monitoring policies create \
  --notification-channels="projects/$PROJECT_ID/notificationChannels/YOUR_CHANNEL_ID" \
  --display-name="Panelin API Error Rate" \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
```

## CI/CD with GitHub

### Connect Repository to Cloud Build

1. Go to Cloud Build > Triggers in GCP Console
2. Click "Connect Repository"
3. Select GitHub and authorize
4. Create a trigger:
   - Event: Push to branch `main`
   - Build configuration: `cloudbuild.yaml`

### Staging vs Production

Create separate triggers with different substitutions:

**Staging:**
```yaml
substitutions:
  _SERVICE: panelin-api-staging
  _MIN_INSTANCES: "0"
  _MAX_INSTANCES: "3"
```

**Production:**
```yaml
substitutions:
  _SERVICE: panelin-api
  _MIN_INSTANCES: "1"
  _MAX_INSTANCES: "10"
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port (Cloud Run sets this) | Auto |
| `CLOUD_RUN_URL` | Service URL for OpenAPI | No |
| `OPENAI_API_KEY` | OpenAI API key (via Secret Manager) | No |

## Troubleshooting

### Container fails to start

```bash
# Check build logs
gcloud builds log <BUILD_ID>

# Check service logs
gcloud run logs read panelin-api --region=$REGION
```

### Slow cold starts

- Increase `--min-instances` to keep warm instances
- Optimize imports in `api.py`
- Use lighter base image if possible

### 503 Service Unavailable

- Check `/ready` endpoint for failed checks
- Verify knowledge base files are included in container
- Check memory limits (increase if OOM)

## Cost Estimation

Cloud Run pricing (as of 2024):
- CPU: ~$0.000024 per vCPU-second
- Memory: ~$0.0000025 per GiB-second
- Requests: ~$0.40 per million

With scale-to-zero and moderate traffic (~10k requests/month):
- Estimated cost: **$5-20/month**

## Security Checklist

- [ ] Service account with least privilege
- [ ] Secrets in Secret Manager (not environment variables)
- [ ] HTTPS only (Cloud Run default)
- [ ] Authentication configured (public vs IAM)
- [ ] VPC connector if accessing private resources
- [ ] Audit logging enabled

## Next Steps

1. **Custom Domain**: Configure custom domain in Cloud Run settings
2. **CDN**: Add Cloud CDN for better global performance
3. **WAF**: Consider Cloud Armor for DDoS protection
4. **Backup**: Set up regular exports of knowledge base data

## Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Container build instructions |
| `.dockerignore` | Files to exclude from container |
| `cloudbuild.yaml` | CI/CD pipeline configuration |
| `requirements.txt` | Pinned Python dependencies |
| `api.py` | FastAPI application with health endpoints |
| `deployment_bundle/openapi.json` | OpenAPI schema for GPT Actions |
