# Panelin API - Cloud Run Deployment Guide

## Overview

This guide covers deploying the Panelin Agent V2 API to Google Cloud Run, providing a production-ready, auto-scaling, HTTPS-enabled endpoint.

## Architecture

```
+----------------+     +------------------+     +----------------+
|   ChatGPT      | --> |   Cloud Run      | --> |   Knowledge    |
|   Custom GPT   |     |   panelin-api    |     |   Base (JSON)  |
+----------------+     +------------------+     +----------------+
                              |
                              v
                       +--------------+
                       | Artifact     |
                       | Registry     |
                       +--------------+
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Enable required APIs:**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     artifactregistry.googleapis.com \
     secretmanager.googleapis.com
   ```

## Quick Start (One-Command Deploy)

```bash
cd "Copia de panelin_agent_v2"
gcloud run deploy panelin-api --source . --region us-central1 --allow-unauthenticated
```

This will:
1. Build the Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Print the service URL

## Detailed Deployment Steps

### 1. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"
```

### 2. Build and Push Docker Image

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build the image
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT/panelin/panelin-api:latest .

# Push to registry
docker push us-central1-docker.pkg.dev/YOUR_PROJECT/panelin/panelin-api:latest
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT/panelin/panelin-api:latest \
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

### 4. Get Service URL

```bash
gcloud run services describe panelin-api \
  --region us-central1 \
  --format='value(status.url)'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | HTTP port (set by Cloud Run) | 8080 |
| `CLOUD_RUN_URL` | Service URL for OpenAPI | - |
| `OPENAI_API_KEY` | For LangGraph agent (optional) | - |

### Setting Environment Variables

```bash
gcloud run services update panelin-api \
  --region us-central1 \
  --set-env-vars "CLOUD_RUN_URL=https://panelin-api-xxxxx-uc.a.run.app"
```

## Secrets Management

For sensitive values like API keys:

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy panelin-api \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  ...
```

## Health Checks

The API exposes health check endpoints for Cloud Run:

- **Liveness Probe:** `GET /health`
  - Returns 200 if service is running
  - Used by Cloud Run to determine if container is alive

- **Readiness Probe:** `GET /ready`
  - Returns 200 if service can accept traffic
  - Checks: pricing rules, product catalog, quotation engine
  - Returns 503 if any check fails

### Configure Custom Health Checks

```bash
gcloud run services update panelin-api \
  --region us-central1 \
  --liveness-probe-http-get-path=/health \
  --startup-probe-http-get-path=/ready
```

## CI/CD with Cloud Build

The repository includes `cloudbuild.yaml` for automated deployments.

### Setup Cloud Build Trigger

```bash
# Connect your GitHub repository
gcloud builds triggers create github \
  --repo-name=your-repo \
  --repo-owner=your-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --substitutions="_REGION=us-central1,_SERVICE=panelin-api,_REPO=panelin"
```

### Trigger Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `_REGION` | Cloud Run region | us-central1 |
| `_SERVICE` | Cloud Run service name | panelin-api |
| `_REPO` | Artifact Registry repository | panelin |

## Monitoring & Observability

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" \
  --limit 100
```

### Create Alert Policy

```bash
# Alert on high error rate
gcloud alpha monitoring policies create \
  --display-name="Panelin API Error Rate" \
  --condition-display-name="Error Rate > 1%" \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
```

## Updating the OpenAPI Schema

After deployment, update the `servers` entry in `deployment_bundle/openapi.json`:

```json
"servers": [
  {
    "url": "https://panelin-api-xxxxx-uc.a.run.app",
    "description": "Cloud Run Production"
  }
]
```

## Cost Optimization

- **Scale to zero:** `--min-instances 0` (default) stops billing when idle
- **CPU always allocated:** Remove for lower cost if cold starts are acceptable
- **Concurrency:** Higher concurrency = fewer instances = lower cost

## Troubleshooting

### Container fails to start
```bash
gcloud run services logs read panelin-api --region us-central1
```

### Health check failures
```bash
curl https://your-service-url/ready
```

### Permission issues
```bash
gcloud run services add-iam-policy-binding panelin-api \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Security Considerations

1. **Public access:** `--allow-unauthenticated` makes the API public. For private access, use IAM authentication.
2. **Secrets:** Never commit API keys. Use Secret Manager.
3. **Service account:** Create a dedicated service account with minimal permissions.

## Next Steps

1. Set up custom domain
2. Configure SSL certificate
3. Set up monitoring dashboards
4. Implement rate limiting
5. Add authentication (if needed)
