# Panelin API - Quick Deployment Reference

## 🚀 Quick Start (5 Minutes)

### Prerequisites
```bash
# Set your GCP project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable APIs (one-time setup)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### 1. Create Artifact Registry (one-time)
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 2. Deploy to Cloud Run
```bash
cd "Copia de panelin_agent_v2"

gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### 3. Get Your URL
```bash
gcloud run services describe panelin-api \
  --region us-central1 \
  --format="value(status.url)"
```

### 4. Test It
```bash
CLOUD_RUN_URL=$(gcloud run services describe panelin-api --region us-central1 --format="value(status.url)")
curl $CLOUD_RUN_URL/health
curl $CLOUD_RUN_URL/docs
```

## 🔄 Set Up Auto-Deploy from GitHub

### 1. Grant Cloud Build Permissions
```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 2. Connect GitHub & Create Trigger
1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click **"Connect Repository"** → Select GitHub → Authenticate
3. Create trigger:
   - **Name**: `panelin-api-deploy`
   - **Event**: Push to branch
   - **Branch**: `^main$|^cursor/.*$`
   - **Configuration**: Cloud Build configuration file
   - **Location**: `/cloudbuild.yaml`

### 3. Push to GitHub
Every push to `main` or `cursor/*` branches will now auto-deploy! ✨

## 📝 Update API URL

After deployment, set the actual Cloud Run URL:

```bash
# Get the URL
CLOUD_RUN_URL=$(gcloud run services describe panelin-api --region us-central1 --format="value(status.url)")

# Update as environment variable in Cloud Run
gcloud run services update panelin-api \
  --region us-central1 \
  --set-env-vars "API_BASE_URL=$CLOUD_RUN_URL"
```

## 🔐 Add Secrets (Optional)

If your API needs external API keys:

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Update Cloud Run to use it
gcloud run services update panelin-api \
  --region us-central1 \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

## 📊 Monitor & Debug

```bash
# View logs
gcloud run services logs read panelin-api --region us-central1 --limit 50

# Check service status
gcloud run services describe panelin-api --region us-central1

# List deployments
gcloud run revisions list --service panelin-api --region us-central1
```

## 🎯 Common Commands

```bash
# Redeploy current code
gcloud run deploy panelin-api --source . --region us-central1

# Scale up minimum instances (faster response, higher cost)
gcloud run services update panelin-api --region us-central1 --min-instances 1

# Scale down (cost optimization)
gcloud run services update panelin-api --region us-central1 --min-instances 0

# Rollback to previous version
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for detailed instructions, security setup, monitoring, and troubleshooting.

---

**Need Help?**
- Cloud Run Logs: `gcloud run services logs read panelin-api --region us-central1`
- Cloud Build History: https://console.cloud.google.com/cloud-build/builds
- API Health Check: `https://YOUR-CLOUD-RUN-URL/health`
