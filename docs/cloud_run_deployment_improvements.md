# Cloud Run Deployment Improvements

This document details the improvements made to the deployment configuration for production readiness.

## 1. Docker Configuration
- **Dockerfile**: Created in `Copia de panelin_agent_v2/Dockerfile`.
  - Uses `sh -c` in CMD to correctly expand `${PORT}`.
  - Base image: `python:3.11-slim`.
- **.dockerignore**: Created in `Copia de panelin_agent_v2/.dockerignore`.
  - Excludes `tests/`, `__pycache__`, and other non-essential files to reduce image size.

## 2. API Improvements
- **Health Checks**: Added `/health` and `/ready` endpoints to `api.py`.
  - `/health`: Returns 200 OK if service is running.
  - `/ready`: Returns 200 OK if service is ready to accept traffic.

## 3. Cloud Build Configuration
- **cloudbuild.yaml**: Created in the workspace root.
  - Builds from `Copia de panelin_agent_v2`.
  - Pushes to Artifact Registry.
  - Deploys to Cloud Run with:
    - Memory: 512Mi
    - CPU: 1
    - Timeout: 300s
    - Concurrency: 80
    - Autoscaling: 0-10 instances

## 4. Security & Identity Recommendations (Manual Steps)

The following steps should be performed via Google Cloud Console or CLI to fully secure the service.

### Secret Manager Integration
Instead of plain environment variables, use Secret Manager.

1. Create a secret:
   ```bash
   gcloud secrets create panelin-api-key --replication-policy="automatic"
   echo -n "your-super-secret-key" | gcloud secrets versions add panelin-api-key --data-file=-
   ```

2. Grant access to Cloud Run Service Account:
   ```bash
   # Get the default compute service account (or your custom one)
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

   gcloud secrets add-iam-policy-binding panelin-api-key \
       --member="serviceAccount:${SERVICE_ACCOUNT}" \
       --role="roles/secretmanager.secretAccessor"
   ```

3. Update Cloud Run to mount the secret:
   ```bash
   gcloud run services update panelin-api \
       --set-secrets="API_KEY=panelin-api-key:latest" \
       --region us-central1
   ```

### IAM Authentication
For internal services, remove `--allow-unauthenticated` and use IAM.

1. Remove public access:
   ```bash
   gcloud run services remove-iam-policy-binding panelin-api \
       --member="allUsers" \
       --role="roles/run.invoker" \
       --region us-central1
   ```

2. Grant invoker role to specific service accounts or users:
   ```bash
   gcloud run services add-iam-policy-binding panelin-api \
       --member="user:admin@example.com" \
       --role="roles/run.invoker" \
       --region us-central1
   ```

### Observability
- **Alerting**: Set up Cloud Monitoring alerts for:
  - Latency (p99 > 2s)
  - 5xx Error Rate > 1%
  - Container Startup Latency
