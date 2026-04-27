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

### Option A: GitHub Actions with OIDC (recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-gcp.yml`) that
uses **OpenID Connect (OIDC)** with Workload Identity Federation so no long-lived service
account keys need to be stored as GitHub secrets.

#### One-time GCP setup for OIDC

1. **Create a Workload Identity Pool:**

   ```bash
   gcloud iam workload-identity-pools create "github-pool" \
     --location="global" \
     --display-name="GitHub Actions Pool"
   ```

2. **Create a Workload Identity Provider:**

   ```bash
   gcloud iam workload-identity-pools providers create-oidc "github-provider" \
     --location="global" \
     --workload-identity-pool="github-pool" \
     --display-name="GitHub Provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
     --attribute-condition="assertion.repository == 'matiasportugau-ui/Chatbot-Truth-base--Creation'" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   ```

3. **Grant the service account access via Workload Identity:**

   ```bash
   PROJECT_ID=$(gcloud config get-value project)
   SA_EMAIL="panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com"
   PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')

   gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/matiasportugau-ui/Chatbot-Truth-base--Creation"
   ```

4. **Add two GitHub repository secrets:**
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full provider path, e.g.
     `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
   - `GCP_SERVICE_ACCOUNT`: The service account email, e.g.
     `panelin-runner@<PROJECT_ID>.iam.gserviceaccount.com`

After setup, every push to `main` triggers the workflow which authenticates via OIDC, builds the
Docker image, pushes it to Artifact Registry, and deploys to Cloud Run — all without long-lived keys.

### Option B: Cloud Build (CI/CD)

From repo root:

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

This builds the image, runs tests, pushes to Artifact Registry, and deploys to Cloud Run.  
**Note:** The default `cloudbuild.yaml` does not inject secrets. Add to the deploy step for first run:

- `--service-account panelin-runner@PROJECT_ID.iam.gserviceaccount.com`
- `--set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest"`

Edit `cloudbuild.yaml` and add those args to the `gcloud run deploy` step, or use Option C for the first deploy.

### Option C: Manual first deploy (with secrets)

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
  --set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest" \
  --no-allow-unauthenticated
```

For public access (e.g. health only), use `--allow-unauthenticated` instead of `--no-allow-unauthenticated`.

### Option D: Deploy from existing image

If you already built and pushed the image:

```bash
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/PROJECT_ID/panelin/panelin-api:SHA \
  --region us-central1 \
  --set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest" \
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
