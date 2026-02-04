# Panelin API - Cloud Deployment Guide

This guide walks you through deploying the Panelin API to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Required APIs enabled**:
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     secretmanager.googleapis.com
   ```

## Initial Setup (One-Time)

### 1. Set Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_NAME="panelin-api"
export REPO_NAME="panelin"
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create ${REPO_NAME} \
  --repository-format=docker \
  --location=${REGION} \
  --project=${PROJECT_ID}
```

### 3. Create Service Account

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin API Cloud Run Service Account" \
  --project=${PROJECT_ID}

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Store Secrets in Secret Manager

```bash
# Create secret for OpenAI API Key
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY \
  --data-file=- \
  --project=${PROJECT_ID}

# Grant the service account access to the secret
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=${PROJECT_ID}
```

## Deployment Options

### Option 1: Automated Deployment with Cloud Build

This is the recommended approach for CI/CD pipelines.

#### Manual Trigger

```bash
# From the workspace root
gcloud builds submit --config cloudbuild.yaml --project=${PROJECT_ID}
```

#### GitHub Trigger (Automated)

Set up a Cloud Build trigger to automatically deploy on push:

```bash
# Connect your GitHub repository first via Cloud Console
# Then create a trigger:
gcloud builds triggers create github \
  --repo-name=your-repo-name \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=${PROJECT_ID}
```

### Option 2: Direct Deployment with gcloud

For quick testing or initial deployment:

```bash
cd "Copia de panelin_agent_v2"

gcloud run deploy ${SERVICE_NAME} \
  --source . \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --service-account panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --allow-unauthenticated
```

## Post-Deployment Configuration

### 1. Get Your Service URL

```bash
gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --format="value(status.url)"
```

### 2. Update API_SERVER_URL Environment Variable

Once deployed, update the service with the actual URL:

```bash
export SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --format="value(status.url)")

gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --set-env-vars "API_SERVER_URL=${SERVICE_URL}"
```

### 3. Test the Deployment

```bash
# Health check
curl ${SERVICE_URL}/health

# Readiness check
curl ${SERVICE_URL}/ready

# API documentation
curl ${SERVICE_URL}/docs
```

## Monitoring and Observability

### View Logs

```bash
gcloud run services logs read ${SERVICE_NAME} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --limit 50
```

### Set Up Alerts (Recommended)

Create alerts for:
- **Error rate > 5%**
- **P95 latency > 2000ms**
- **Cold start frequency**

Use Cloud Monitoring console or:

```bash
# Example: Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Panelin API Error Rate Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

## Cost Optimization

Cloud Run charges based on:
- **CPU and memory allocation** (only while processing requests)
- **Number of requests**
- **Egress bandwidth**

**Cost-saving tips:**
- Use `--min-instances 0` to scale to zero when idle
- Monitor actual CPU/memory usage and adjust limits
- Consider using Cloud Run's committed use discounts for predictable workloads

## Security Best Practices

### 1. Authentication Options

**Public Access (Current):**
```bash
--allow-unauthenticated
```

**IAM Authentication (Recommended for production):**
```bash
--no-allow-unauthenticated

# Allow specific service accounts to invoke
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --region ${REGION} \
  --member="serviceAccount:caller@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

**Identity-Aware Proxy (IAP) for user authentication:**
Set up via Cloud Console for OAuth-based user authentication.

### 2. Rotate Secrets Regularly

```bash
# Update secret version
echo -n "new-api-key" | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# Cloud Run will automatically use the latest version
```

### 3. Enable VPC Connector (if needed)

For accessing private resources:

```bash
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --vpc-connector your-vpc-connector \
  --vpc-egress all-traffic
```

## Troubleshooting

### Common Issues

**1. "Permission denied" errors**
- Verify service account has correct IAM roles
- Check Secret Manager permissions

**2. Container fails to start**
- Check logs: `gcloud run services logs read ${SERVICE_NAME}`
- Verify Dockerfile builds locally: `docker build -f "Copia de panelin_agent_v2/Dockerfile" "Copia de panelin_agent_v2"`

**3. "Service Unavailable" (503)**
- Check `/ready` endpoint
- Verify dependencies are loading correctly
- Increase timeout if needed

**4. Cold start issues**
- Set `--min-instances 1` for always-warm instances
- Optimize Docker image size
- Use Cloud Run startup CPU boost

## Advanced Configuration

### Environment Variables

```bash
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --set-env-vars "KEY1=value1,KEY2=value2"
```

### Custom Domain

```bash
gcloud run domain-mappings create \
  --service ${SERVICE_NAME} \
  --domain api.yourdomain.com \
  --region ${REGION}
```

### Gradual Rollouts

```bash
# Deploy new revision with 10% traffic
gcloud run services update-traffic ${SERVICE_NAME} \
  --region ${REGION} \
  --to-revisions=REVISION_NEW=10,REVISION_OLD=90
```

## Rollback

```bash
# List revisions
gcloud run revisions list --service ${SERVICE_NAME} --region ${REGION}

# Rollback to previous revision
gcloud run services update-traffic ${SERVICE_NAME} \
  --region ${REGION} \
  --to-revisions=PREVIOUS_REVISION=100
```

## CI/CD Integration

The `cloudbuild.yaml` is configured to:
1. ✅ Build Docker image
2. ✅ Run tests
3. ✅ Push to Artifact Registry
4. ✅ Deploy to Cloud Run

**Environment-specific deployments:**

Modify `cloudbuild.yaml` substitutions:
- **Staging**: `_SERVICE=panelin-api-staging`
- **Production**: `_SERVICE=panelin-api-prod`

## Resource Limits

Current configuration in `cloudbuild.yaml`:
- **Memory**: 512Mi (adjust based on actual usage)
- **CPU**: 1 vCPU
- **Timeout**: 300s (5 minutes)
- **Concurrency**: 80 requests per instance
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10

Monitor and adjust these based on:
```bash
# View service metrics
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format=yaml
```

## Next Steps

1. ✅ Deploy to staging environment first
2. ✅ Run integration tests
3. ✅ Set up monitoring alerts
4. ✅ Configure custom domain (if needed)
5. ✅ Set up Cloud Armor for DDoS protection (if public)
6. ✅ Enable Cloud CDN for caching (if needed)
7. ✅ Deploy to production with gradual rollout

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Cloud Run Pricing Calculator](https://cloud.google.com/products/calculator)

---

**Deployment Checklist:**
- [x] Dockerfile created
- [x] .dockerignore configured
- [x] Dependencies pinned
- [x] Health endpoints added (/health, /ready)
- [x] cloudbuild.yaml configured
- [x] OpenAPI schema supports environment-based URL
- [ ] Artifact Registry repository created
- [ ] Service account created with permissions
- [ ] Secrets stored in Secret Manager
- [ ] Cloud Build triggered successfully
- [ ] Cloud Run service deployed
- [ ] API_SERVER_URL environment variable set
- [ ] Monitoring alerts configured
- [ ] Production deployment tested
