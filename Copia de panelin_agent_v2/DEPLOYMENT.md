# Panelin API - Cloud Deployment Guide

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Project**
   - Create a project at [Google Cloud Console](https://console.cloud.google.com)
   - Enable billing for the project
   - Install [gcloud CLI](https://cloud.google.com/sdk/docs/install)

2. **Required APIs**
   ```bash
   gcloud services enable run.googleapis.com \
       cloudbuild.googleapis.com \
       artifactregistry.googleapis.com \
       --project YOUR_PROJECT_ID
   ```

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

---

## 📦 Deployment Methods

### Method 1: Automated Deployment (Recommended)

Use the deployment script for a fully automated deployment:

```bash
# From the repository root
python scripts/deploy_cloud_run.py --project YOUR_PROJECT_ID
```

**Options:**
- `--project PROJECT_ID` - Your GCP project ID
- `--region REGION` - GCP region (default: us-central1)
- `--service SERVICE_NAME` - Cloud Run service name (default: panelin-api)
- `--private` - Deploy as private service (requires IAM authentication)

**Example:**
```bash
python scripts/deploy_cloud_run.py \
    --project my-project-123 \
    --region us-central1 \
    --service panelin-api
```

---

### Method 2: Manual Deployment

#### Step 1: Build and Deploy with Source

```bash
cd "Copia de panelin_agent_v2"

gcloud run deploy panelin-api \
    --source . \
    --region us-central1 \
    --platform managed \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --allow-unauthenticated
```

#### Step 2: Get Service URL

```bash
gcloud run services describe panelin-api \
    --region us-central1 \
    --format 'value(status.url)'
```

---

### Method 3: CI/CD with Cloud Build

#### Step 1: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
    --repository-format=docker \
    --location=us-central1
```

#### Step 2: Set up Cloud Build Trigger

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Create Trigger"
3. Configure:
   - **Name**: `deploy-panelin-api`
   - **Event**: Push to branch
   - **Source**: Your repository
   - **Branch**: `^main$` or your preferred branch
   - **Configuration**: Cloud Build configuration file
   - **Location**: `Copia de panelin_agent_v2/cloudbuild.yaml`

#### Step 3: Push to trigger deployment

```bash
git add .
git commit -m "Deploy Panelin API"
git push origin main
```

---

## 🔧 Configuration

### Environment Variables

Set environment variables for your Cloud Run service:

```bash
gcloud run services update panelin-api \
    --update-env-vars KEY1=value1,KEY2=value2 \
    --region us-central1
```

### Secrets Management

For sensitive data like API keys, use Secret Manager:

```bash
# Create a secret
echo -n "your-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor

# Update Cloud Run service to use the secret
gcloud run services update panelin-api \
    --update-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --region us-central1
```

---

## 🏥 Health Checks

The API includes health check endpoints:

- **`GET /health`** - Liveness probe (is the service running?)
- **`GET /ready`** - Readiness probe (is the service ready to handle requests?)
- **`GET /`** - Basic health check

Test health checks:
```bash
SERVICE_URL=$(gcloud run services describe panelin-api --region us-central1 --format 'value(status.url)')
curl $SERVICE_URL/health
curl $SERVICE_URL/ready
```

---

## 📊 Monitoring & Logging

### View Logs

```bash
# Real-time logs
gcloud logging tail 'resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api' --project YOUR_PROJECT_ID

# Recent logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api' \
    --project YOUR_PROJECT_ID \
    --limit 50 \
    --format json
```

### Metrics

View metrics in [Cloud Console](https://console.cloud.google.com/run):
- Request count
- Request latency (P50, P95, P99)
- Container instance count
- CPU utilization
- Memory utilization

### Alerts

Set up alerting policies:

```bash
# Example: Alert on error rate > 5%
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate - Panelin API" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=300s
```

---

## 🔒 Security

### IAM Authentication

For private API (recommended for production):

```bash
# Deploy with IAM authentication
gcloud run deploy panelin-api \
    --source . \
    --region us-central1 \
    --no-allow-unauthenticated
```

### Service Account

Create a dedicated service account with minimal permissions:

```bash
# Create service account
gcloud iam service-accounts create panelin-runner \
    --display-name="Panelin API Runner"

# Deploy with service account
gcloud run deploy panelin-api \
    --source . \
    --region us-central1 \
    --service-account panelin-runner@PROJECT_ID.iam.gserviceaccount.com
```

---

## 🧪 Testing

### Local Testing with Docker

Build and test the container locally:

```bash
# Build
docker build -t panelin-api .

# Run locally
docker run -p 8000:8000 -e PORT=8000 panelin-api

# Test
curl http://localhost:8000/health
```

### Load Testing

Use tools like Apache Bench or k6:

```bash
# Apache Bench
ab -n 1000 -c 10 $SERVICE_URL/health

# k6
k6 run --vus 10 --duration 30s load-test.js
```

---

## 💰 Cost Optimization

### Scaling Configuration

```bash
# Optimize for cost
gcloud run services update panelin-api \
    --min-instances 0 \          # Scale to zero when idle
    --max-instances 10 \         # Cap maximum instances
    --concurrency 80 \           # Requests per instance
    --cpu 1 \                    # CPU allocation
    --memory 512Mi \             # Memory allocation
    --region us-central1
```

### Resource Recommendations

- **Development**: 512Mi memory, 1 CPU
- **Production**: 1Gi memory, 2 CPUs
- **High Traffic**: 2Gi memory, 4 CPUs

---

## 🔄 Updates & Rollbacks

### Deploy New Version

```bash
# Deploy new version
gcloud run deploy panelin-api --source . --region us-central1

# Traffic splitting (canary deployment)
gcloud run services update-traffic panelin-api \
    --to-revisions=REVISION_NEW=10,REVISION_OLD=90 \
    --region us-central1
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service panelin-api --region us-central1

# Rollback to previous revision
gcloud run services update-traffic panelin-api \
    --to-revisions=REVISION_OLD=100 \
    --region us-central1
```

---

## 📝 OpenAPI Schema Update

After deployment, update your OpenAPI schema with the production URL:

```python
# Run the deployment script to auto-update
python scripts/deploy_cloud_run.py --project YOUR_PROJECT_ID
```

Or manually update `deployment_bundle/openapi.json`:

```json
{
  "servers": [
    {
      "url": "https://panelin-api-xxxxx-uc.a.run.app",
      "description": "Cloud Run Production"
    }
  ]
}
```

---

## 🆘 Troubleshooting

### Common Issues

1. **Deployment fails with permission errors**
   ```bash
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member=user:YOUR_EMAIL \
       --role=roles/run.admin
   ```

2. **Service crashes on startup**
   ```bash
   # Check logs
   gcloud logging read 'resource.type=cloud_run_revision' --limit 50 --format json
   ```

3. **Port binding errors**
   - Ensure your app listens on `0.0.0.0:${PORT}`
   - Cloud Run injects `PORT` environment variable

4. **Container build fails**
   ```bash
   # Test locally
   docker build -t test-build .
   docker run -p 8000:8000 -e PORT=8000 test-build
   ```

### Support Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Troubleshooting Guide](https://cloud.google.com/run/docs/troubleshooting)
- [Best Practices](https://cloud.google.com/run/docs/tips)

---

## 📚 Additional Resources

- **API Documentation**: `{SERVICE_URL}/docs`
- **OpenAPI Spec**: `{SERVICE_URL}/openapi.json`
- **Health Check**: `{SERVICE_URL}/health`
- **Readiness**: `{SERVICE_URL}/ready`

---

## 🎯 Next Steps

1. ✅ Deploy the API to Cloud Run
2. ✅ Test all endpoints
3. ✅ Set up monitoring and alerts
4. ✅ Configure secrets for API keys
5. ✅ Set up CI/CD with Cloud Build triggers
6. ✅ Update OpenAPI schema with production URL
7. ✅ Configure custom domain (optional)
8. ✅ Set up Cloud CDN (optional)

---

**Need Help?** Open an issue or contact the development team.
