# Production Cloud Deployment Plan: Panelin Agent V2

## Overview
This document outlines the production-grade deployment strategy for the Panelin Agent V2 on Google Cloud Run. It incorporates improvements for security, observability, and resilience, addressing the "production-readiness" gaps identified in previous plans.

## Architecture
*   **Compute**: Google Cloud Run (Serverless, Container-native).
*   **Registry**: Artifact Registry (Docker images).
*   **CI/CD**: Cloud Build (Automated build & deploy).
*   **Security**: 
    *   **IAM**: Strictly controlled access (no public `--allow-unauthenticated` by default).
    *   **Secret Manager**: Sensitive configuration injection.
*   **Observability**: Cloud Logging, Cloud Monitoring, and Tracing.

## 1. Codebase Preparation (Completed)

### Dockerfile
A production-ready `Dockerfile` has been created in the root.
*   **Base Image**: `python:3.11-slim` (lightweight, secure).
*   **Port Handling**: Correctly expands `${PORT}` using `sh -c`.
*   **Structure**: Copies specific application folders and `requirements.txt`.

### Dependencies
`requirements.txt` has been updated with **pinned versions** to ensure deterministic builds.

### Health Checks
The API (`api.py`) now includes:
*   `/health`: Liveness probe (returns 200 OK if process is up).
*   `/ready`: Readiness probe (returns 200 OK if dependencies are ready).

## 2. Deployment Implementation

### Step 1: Infrastructure Setup
Run these commands once to set up the environment.

```bash
# 1. Create Artifact Registry Repository
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin Agent Docker Repository"

# 2. Enable APIs
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com
```

### Step 2: Secret Management (Critical Security)
Do not store secrets in environment variables or code.

```bash
# 1. Create a secret (Example: API Key)
printf "my-secret-value" | gcloud secrets create panelin-api-key --data-file=-

# 2. Grant access to the Cloud Run Service Account
# (Replace PROJECT_NUMBER with your actual project number)
gcloud secrets add-iam-policy-binding panelin-api-key \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 3: Deployment via Cloud Build
Use the provided `cloudbuild.yaml` for consistent deployments.

```bash
gcloud builds submit --config cloudbuild.yaml .
```

The `cloudbuild.yaml` is configured with:
*   **Resources**: 512Mi Memory, 1 CPU.
*   **Scaling**: 0-10 instances (Cost efficient, capped risk).
*   **Concurrency**: 80.
*   **Security**: `--no-allow-unauthenticated` (Private service).

## 3. Observability & Monitoring Strategy

### Logging
Cloud Run captures stdout/stderr automatically. The application uses `uvicorn` which logs access requests.

### Alerts (Recommended Setup in Cloud Monitoring)
1.  **Availability**: Alert if `5xx` error rate > 1% for 5 minutes.
2.  **Latency**: Alert if p95 latency > 2000ms.
3.  **Container**: Alert on "Container started" count (high churn/crashing).

## 4. Operational Runbook

### updating the Application
1.  Commit changes to the repository.
2.  Run `gcloud builds submit` (or push to the branch if a trigger is set up).
3.  Cloud Run automatically migrates traffic to the new revision.

### Rollback
If a deployment fails:
```bash
gcloud run services update-traffic panelin-api --to-revisions LATEST_WORKING_REVISION=100
```

### Accessing the Private Service
Since `--no-allow-unauthenticated` is set, you need a token to invoke the service:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://panelin-api-xxxxx-uc.a.run.app/health
```
For public access (if required), deploy with `--allow-unauthenticated` or set up an **API Gateway** / **Cloud Load Balancer** with IAP in front.
