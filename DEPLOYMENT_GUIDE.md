# Panelin API - Cloud Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Panelin Agent V2 API to Google Cloud Run. The deployment uses Cloud Build for CI/CD, Artifact Registry for container storage, and Secret Manager for secure credential management.

## Architecture

- **Platform**: Google Cloud Run (serverless containers)
- **Container Registry**: Artifact Registry
- **CI/CD**: Cloud Build (automated GitHub integration)
- **Secrets Management**: Secret Manager
- **Monitoring**: Cloud Monitoring & Cloud Logging
- **Auto-scaling**: 0 to 10 instances based on traffic

## Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP project with billing enabled
   - Project ID noted (you'll need this)

2. **Required Tools** (install locally if deploying manually)
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Initialize gcloud
   gcloud init
   
   # Login
   gcloud auth login
   
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     artifactregistry.googleapis.com \
     secretmanager.googleapis.com \
     cloudresourcemanager.googleapis.com
   ```

## Step-by-Step Deployment

### 1. Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"

# Verify creation
gcloud artifacts repositories list --location=us-central1
```

### 2. Create Service Account (Recommended for Production)

```bash
# Create a dedicated service account for Cloud Run
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin API Cloud Run Service Account"

# Grant necessary permissions (adjust as needed)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:panelin-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Store Secrets in Secret Manager (if using external APIs)

```bash
# Example: Store OpenAI API key
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY \
  --data-file=- \
  --replication-policy="automatic"

# Example: Store Shopify credentials
echo -n "your-shopify-api-key" | gcloud secrets create SHOPIFY_API_KEY \
  --data-file=- \
  --replication-policy="automatic"

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:panelin-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Manual Deployment (First Time)

For the first deployment, use `gcloud run deploy` from source:

```bash
cd "Copia de panelin_agent_v2"

gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account panelin-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10
  # Add secrets if needed:
  # --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

**Note**: Replace `--allow-unauthenticated` with `--no-allow-unauthenticated` if you want IAM-based authentication.

The deployment will:
- Build the Docker container from the Dockerfile
- Push it to Artifact Registry
- Deploy to Cloud Run
- Provide you with a public URL like: `https://panelin-api-xxxxx-uc.a.run.app`

### 5. Set Up Automated CI/CD with Cloud Build

#### a. Connect GitHub Repository

```bash
# Open Cloud Build triggers page
gcloud alpha builds triggers list

# Or use the console:
# https://console.cloud.google.com/cloud-build/triggers
```

In the GCP Console:
1. Go to **Cloud Build > Triggers**
2. Click **Connect Repository**
3. Select **GitHub** and authenticate
4. Select your repository
5. Click **Connect**

#### b. Create Build Trigger

```bash
# Create trigger for main branch deployments
gcloud builds triggers create github \
  --name="panelin-api-deploy-main" \
  --repo-name="YOUR_REPO_NAME" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$|^cursor/.*$" \
  --build-config="cloudbuild.yaml" \
  --substitutions="_REGION=us-central1,_REPO=panelin,_SERVICE=panelin-api"
```

Or create manually in the console:
1. **Name**: `panelin-api-deploy`
2. **Event**: Push to branch
3. **Source**: Your connected repository
4. **Branch**: `^main$` (or your deployment branch pattern)
5. **Build Configuration**: Cloud Build configuration file
6. **Location**: `/cloudbuild.yaml`
7. **Substitution variables**: Add `_REGION`, `_REPO`, `_SERVICE` as needed

### 6. Grant Cloud Build Permissions

Cloud Build needs permissions to deploy to Cloud Run:

```bash
# Get your project number
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")

# Grant Cloud Build the Cloud Run Admin role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Cloud Build the Service Account User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 7. Update OpenAPI Schema with Cloud Run URL

After deployment, get your Cloud Run URL:

```bash
gcloud run services describe panelin-api \
  --region us-central1 \
  --format="value(status.url)"
```

Update the `servers` section in your API schema (or environment configuration):

```json
{
  "servers": [
    {
      "url": "https://panelin-api-xxxxx-uc.a.run.app",
      "description": "Production - Google Cloud Run"
    }
  ]
}
```

### 8. Set Up Monitoring & Alerts

```bash
# View logs
gcloud run services logs read panelin-api --region us-central1

# Create uptime check (optional)
# Visit: https://console.cloud.google.com/monitoring/uptime
```

In the GCP Console, set up **Cloud Monitoring** alerts for:
- Error rate > 5%
- P95 latency > 2000ms
- Container restart frequency
- Cold start duration

## Configuration Options

### Environment Variables

To add environment variables to your Cloud Run service:

```bash
gcloud run services update panelin-api \
  --region us-central1 \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=info"
```

### Resource Limits

Adjust memory, CPU, and scaling:

```bash
gcloud run services update panelin-api \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 20
```

### Custom Domain

To use a custom domain:

```bash
# Map a domain
gcloud run domain-mappings create \
  --service panelin-api \
  --domain api.your-domain.com \
  --region us-central1
```

## Testing the Deployment

### Health Checks

```bash
CLOUD_RUN_URL=$(gcloud run services describe panelin-api --region us-central1 --format="value(status.url)")

# Test liveness
curl $CLOUD_RUN_URL/health

# Test readiness
curl $CLOUD_RUN_URL/ready

# Test API functionality
curl "$CLOUD_RUN_URL/products/search?q=isopanel&max_results=3"
```

### OpenAPI Documentation

Visit your Cloud Run URL + `/docs` to see the interactive API documentation:
```
https://panelin-api-xxxxx-uc.a.run.app/docs
```

## Troubleshooting

### Container Fails to Start

```bash
# Check logs
gcloud run services logs read panelin-api --region us-central1 --limit 50

# Check service details
gcloud run services describe panelin-api --region us-central1
```

### Build Failures

```bash
# List builds
gcloud builds list --limit 10

# Get build details
gcloud builds describe BUILD_ID

# View build logs
gcloud builds log BUILD_ID
```

### Permission Errors

Ensure Cloud Build has the necessary IAM roles (see Step 6).

### Cold Start Issues

If cold starts are slow, consider:
- Increasing `--min-instances` to 1 or more
- Optimizing Docker image size
- Using `--cpu-boost` flag for faster cold starts

## Cost Optimization

Cloud Run pricing is based on:
- **CPU and Memory**: Only charged when processing requests
- **Requests**: First 2 million requests/month are free
- **Networking**: Egress charges apply

**Tips**:
- Use `--min-instances 0` to scale to zero when idle
- Optimize container image size to reduce cold start time
- Set appropriate `--cpu` and `--memory` limits (don't over-provision)
- Use request timeout (`--timeout`) to prevent runaway costs

## Security Best Practices

1. **Authentication**: Use `--no-allow-unauthenticated` for production and require IAM or API keys
2. **Secrets**: Never commit secrets; use Secret Manager
3. **Service Account**: Use least-privilege IAM roles
4. **HTTPS Only**: Cloud Run enforces HTTPS by default
5. **VPC**: Consider VPC Connector for private network access
6. **Audit Logs**: Enable Cloud Audit Logs for compliance

## Rollback

To rollback to a previous revision:

```bash
# List revisions
gcloud run revisions list --service panelin-api --region us-central1

# Rollback to a specific revision
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

## Support

For issues or questions:
1. Check Cloud Run logs: `gcloud run services logs read panelin-api --region us-central1`
2. Review Cloud Build history: https://console.cloud.google.com/cloud-build/builds
3. Check service health: Visit `/health` and `/ready` endpoints

---

**Deployment Status Checklist**:
- [ ] Artifact Registry repository created
- [ ] Service account created with appropriate permissions
- [ ] Secrets stored in Secret Manager (if needed)
- [ ] First manual deployment successful
- [ ] Cloud Run URL obtained and tested
- [ ] Cloud Build trigger configured
- [ ] Cloud Build permissions granted
- [ ] OpenAPI schema updated with production URL
- [ ] Monitoring and alerts configured
- [ ] Documentation updated with actual URLs
- [ ] Team notified of deployment

---

**Last Updated**: 2026-02-04
**Maintained By**: Cloud Infrastructure Team
