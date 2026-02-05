# Cloud Run Deployment

Panelin Wolf API runs on **Google Cloud Run** using the Dockerfile and Cloud Build config in this repo.

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and logged in (`gcloud auth login`, `gcloud config set project PROJECT_ID`)
- Docker (for local build/test)

## One-time setup

### 1. Enable APIs

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

### 2. Create Artifact Registry repo

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 3. Create secrets (Secret Manager)

The API requires `WOLF_API_KEY` (and optionally `OPENAI_API_KEY` for future features). Create them:

```bash
# WOLF_API_KEY is required for API authentication
echo -n "YOUR_WOLF_API_KEY" | gcloud secrets create WOLF_API_KEY --data-file=-

# Optional: for assistant/LLM features
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### 4. Service account (recommended)

Create a dedicated service account for Cloud Run and grant it access to secrets:

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud iam service-accounts create panelin-runner --display-name "Panelin Cloud Run"
SA_EMAIL="panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com"

# Allow Cloud Run to read the secrets
gcloud secrets add-iam-policy-binding WOLF_API_KEY \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/secretmanager.secretAccessor"
# Repeat for OPENAI_API_KEY if created
```

## Deploy

### Option A: Cloud Build (CI/CD)

From repo root:

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

This builds the image, runs tests, pushes to Artifact Registry, and deploys to Cloud Run.  
**Note:** The default `cloudbuild.yaml` does not inject secrets. Add to the deploy step for first run:

- `--service-account panelin-runner@PROJECT_ID.iam.gserviceaccount.com`
- `--set-secrets "WOLF_API_KEY=projects/PROJECT_ID/secrets/WOLF_API_KEY:latest"`

Edit `cloudbuild.yaml` and add those args to the `gcloud run deploy` step, or use Option B for the first deploy.

### Option B: Manual first deploy (with secrets)

From repo root:

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
SA_EMAIL="panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run deploy panelin-api \
  --source . \
  --region $REGION \
  --service-account $SA_EMAIL \
  --memory 512Mi --cpu 1 --timeout 300 --concurrency 80 \
  --min-instances 0 --max-instances 10 \
  --set-secrets "WOLF_API_KEY=projects/${PROJECT_ID}/secrets/WOLF_API_KEY:latest" \
  --no-allow-unauthenticated
```

For public access (e.g. health only), use `--allow-unauthenticated` instead of `--no-allow-unauthenticated`.

### Option C: Deploy from existing image

If you already built and pushed the image:

```bash
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/PROJECT_ID/panelin/panelin-api:SHA \
  --region us-central1 \
  --set-secrets "WOLF_API_KEY=projects/PROJECT_ID/secrets/WOLF_API_KEY:latest" \
  --no-allow-unauthenticated
```

## After deploy

- **URL:** `https://panelin-api-XXXXX-uc.a.run.app` (from Cloud Run console or `gcloud run services describe panelin-api --region us-central1 --format='value(status.url)'`).
- **Health:** `GET /health` (no auth). **Readiness:** `GET /ready` (returns 200 when `WOLF_API_KEY` is set).
- **OpenAPI:** Update `deployment_bundle/openapi.json` `servers[].url` to this URL and use the same `X-API-Key` value as `WOLF_API_KEY` for the GPT action.

## Local Docker run (test)

```bash
docker build -t panelin-api .
docker run --rm -p 8000:8000 -e WOLF_API_KEY=your-key -e PORT=8000 panelin-api
# GET http://localhost:8000/health
```
