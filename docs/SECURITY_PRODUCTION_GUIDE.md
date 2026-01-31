# Security & Production Guide for Panelin API

This guide covers security best practices, Secret Manager integration, IAM configuration, and access control for the Panelin API deployed on Google Cloud Run.

## Table of Contents

1. [Secret Manager Integration](#secret-manager-integration)
2. [IAM & Service Accounts](#iam--service-accounts)
3. [Access Control Options](#access-control-options)
4. [Cloud Armor & Rate Limiting](#cloud-armor--rate-limiting)
5. [Security Checklist](#security-checklist)

---

## Secret Manager Integration

### Why Secret Manager?

- **Centralized secret storage**: Single source of truth for all secrets
- **Automatic rotation**: Support for secret versioning and rotation
- **Audit logging**: Track who accessed secrets and when
- **IAM integration**: Fine-grained access control per secret
- **No secrets in code**: Eliminates hardcoded credentials

### Step 1: Create Secrets

```bash
# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Create secrets
gcloud secrets create openai-api-key \
  --replication-policy="automatic" \
  --labels="app=panelin-api,env=production"

gcloud secrets create mongodb-uri \
  --replication-policy="automatic" \
  --labels="app=panelin-api,env=production"

gcloud secrets create shopify-api-key \
  --replication-policy="automatic" \
  --labels="app=panelin-api,env=production"
```

### Step 2: Add Secret Values

```bash
# Add secret values (use --data-file for complex values)
echo -n "sk-your-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-

echo -n "mongodb+srv://user:pass@cluster.mongodb.net/db" | gcloud secrets versions add mongodb-uri --data-file=-

# Or from a file
gcloud secrets versions add shopify-api-key --data-file=./secret-shopify.txt
```

### Step 3: Grant Access to Service Account

```bash
# Grant the Cloud Run service account access to secrets
export SA_EMAIL="panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding mongodb-uri \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding shopify-api-key \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Reference Secrets in Cloud Run

**Option A: Via gcloud CLI**

```bash
gcloud run deploy panelin-api \
  --image=us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:latest \
  --region=us-central1 \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,MONGODB_URI=mongodb-uri:latest" \
  --service-account="${SA_EMAIL}"
```

**Option B: Via YAML (cloudrun-service.yaml)**

```yaml
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: openai-api-key
        key: latest
  - name: MONGODB_URI
    valueFrom:
      secretKeyRef:
        name: mongodb-uri
        key: latest
```

### Secret Rotation

```bash
# Add a new version (previous version still accessible)
echo -n "sk-new-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-

# Disable old version after confirming new version works
gcloud secrets versions disable 1 --secret=openai-api-key

# Destroy old version (irreversible)
gcloud secrets versions destroy 1 --secret=openai-api-key
```

---

## IAM & Service Accounts

### Principle of Least Privilege

Create a dedicated service account for the Panelin API with only the permissions it needs.

### Step 1: Create Service Account

```bash
export PROJECT_ID="your-project-id"
export SA_NAME="panelin-api-sa"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create the service account
gcloud iam service-accounts create ${SA_NAME} \
  --display-name="Panelin API Service Account" \
  --description="Dedicated SA for Panelin API Cloud Run service"
```

### Step 2: Assign Minimal Roles

```bash
# Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Cloud Logging (write logs)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"

# Cloud Trace (if using tracing)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtrace.agent"

# Cloud Monitoring (custom metrics)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.metricWriter"

# If accessing Cloud Storage
# gcloud projects add-iam-policy-binding ${PROJECT_ID} \
#   --member="serviceAccount:${SA_EMAIL}" \
#   --role="roles/storage.objectViewer"

# If accessing Firestore
# gcloud projects add-iam-policy-binding ${PROJECT_ID} \
#   --member="serviceAccount:${SA_EMAIL}" \
#   --role="roles/datastore.user"
```

### Step 3: Deploy with Service Account

```bash
gcloud run deploy panelin-api \
  --service-account="${SA_EMAIL}" \
  --region=us-central1 \
  --image=...
```

---

## Access Control Options

Choose the appropriate access control based on your use case:

### Option 1: Public API (--allow-unauthenticated)

**Use when:** API is meant for public consumption (e.g., customer-facing app)

```bash
gcloud run deploy panelin-api \
  --allow-unauthenticated
```

**Considerations:**
- Implement rate limiting (Cloud Armor)
- Add API key validation in application
- Monitor for abuse

### Option 2: IAM Authentication (Recommended for Internal Services)

**Use when:** API is consumed by other services or internal applications

```bash
# Deploy without --allow-unauthenticated (default is authenticated)
gcloud run deploy panelin-api \
  --no-allow-unauthenticated
```

**Grant access to specific users/services:**

```bash
# Allow a service account to invoke
gcloud run services add-iam-policy-binding panelin-api \
  --region=us-central1 \
  --member="serviceAccount:client-sa@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Allow a specific user
gcloud run services add-iam-policy-binding panelin-api \
  --region=us-central1 \
  --member="user:developer@company.com" \
  --role="roles/run.invoker"

# Allow all authenticated users in organization
gcloud run services add-iam-policy-binding panelin-api \
  --region=us-central1 \
  --member="domain:company.com" \
  --role="roles/run.invoker"
```

**Client authentication:**

```bash
# Get ID token for calling the service
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer ${TOKEN}" https://panelin-api-xxx.run.app/health
```

### Option 3: Identity-Aware Proxy (IAP)

**Use when:** You need user-level authentication with Google accounts

```bash
# Enable IAP for Cloud Run
gcloud run services update panelin-api \
  --region=us-central1 \
  --ingress=internal-and-cloud-load-balancing

# Then configure IAP through the console or Terraform
```

### Option 4: API Gateway

**Use when:** You need rate limiting, API keys, quotas, or complex routing

```bash
# Create API Gateway config (openapi.yaml with x-google-backend)
gcloud api-gateway api-configs create panelin-config \
  --api=panelin-api \
  --openapi-spec=openapi-gateway.yaml

gcloud api-gateway gateways create panelin-gateway \
  --api=panelin-api \
  --api-config=panelin-config \
  --location=us-central1
```

---

## Cloud Armor & Rate Limiting

### Enable Cloud Armor for DDoS Protection

```bash
# Create a security policy
gcloud compute security-policies create panelin-security-policy \
  --description="Security policy for Panelin API"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=panelin-security-policy \
  --action=throttle \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP

# Add geo-blocking rule (optional)
gcloud compute security-policies rules create 2000 \
  --security-policy=panelin-security-policy \
  --action=deny-403 \
  --expression="origin.region_code == 'RU' || origin.region_code == 'CN'"

# Apply to backend service (requires Load Balancer setup)
gcloud compute backend-services update panelin-backend \
  --security-policy=panelin-security-policy \
  --global
```

### Application-Level Rate Limiting

Add to your FastAPI application:

```python
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.get("/quotes")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def create_quote(request: Request):
    ...
```

---

## Security Checklist

### Before Production Deployment

- [ ] **Secrets**: All secrets stored in Secret Manager (no hardcoded values)
- [ ] **Service Account**: Dedicated SA with minimal permissions
- [ ] **Access Control**: Appropriate authentication configured
- [ ] **HTTPS**: Cloud Run provides HTTPS by default
- [ ] **Dependencies**: All dependencies scanned for vulnerabilities
- [ ] **Docker Image**: Using minimal base image (python:slim)
- [ ] **Non-root User**: Container runs as non-root user

### Ongoing Security

- [ ] **Secret Rotation**: Schedule regular secret rotation
- [ ] **Dependency Updates**: Use Dependabot for automatic updates
- [ ] **Vulnerability Scanning**: Enable Container Analysis
- [ ] **Audit Logs**: Review Cloud Audit Logs regularly
- [ ] **Alerts**: Set up alerts for security-related events
- [ ] **Penetration Testing**: Schedule regular security assessments

### Environment Variables to NEVER Expose

```bash
# These should ALWAYS come from Secret Manager:
OPENAI_API_KEY
MONGODB_URI
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
DATABASE_PASSWORD
JWT_SECRET
ENCRYPTION_KEY
```

---

## Quick Reference Commands

```bash
# List all secrets
gcloud secrets list --filter="labels.app=panelin-api"

# View secret versions
gcloud secrets versions list openai-api-key

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --filter="bindings.members:panelin-api-sa"

# View Cloud Run service IAM policy
gcloud run services get-iam-policy panelin-api --region=us-central1

# Check if service is public or authenticated
gcloud run services describe panelin-api --region=us-central1 \
  --format="value(spec.template.metadata.annotations)"
```
