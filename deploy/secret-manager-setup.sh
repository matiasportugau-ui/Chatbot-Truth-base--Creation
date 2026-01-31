#!/bin/bash
# ============================================
# SECRET MANAGER SETUP SCRIPT
# Panelin API - Production Deployment
# ============================================
#
# This script sets up Google Cloud Secret Manager
# for secure secret storage and rotation.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Secret Manager API enabled
#   - Appropriate IAM permissions
#
# Usage:
#   ./deploy/secret-manager-setup.sh <PROJECT_ID>
# ============================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <PROJECT_ID> [REGION]${NC}"
    echo "Example: $0 my-gcp-project us-central1"
    exit 1
fi

PROJECT_ID=$1
REGION=${2:-us-central1}
SERVICE_ACCOUNT="panelin-api@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Secret Manager Setup for Panelin API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Account: ${SERVICE_ACCOUNT}"
echo ""

# ========================================
# Step 1: Enable required APIs
# ========================================
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"

gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"
gcloud services enable run.googleapis.com --project="${PROJECT_ID}"
gcloud services enable artifactregistry.googleapis.com --project="${PROJECT_ID}"
gcloud services enable cloudbuild.googleapis.com --project="${PROJECT_ID}"

echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# ========================================
# Step 2: Create service account
# ========================================
echo -e "${YELLOW}Step 2: Creating service account...${NC}"

# Check if service account exists
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud iam service-accounts create panelin-api \
        --display-name="Panelin API Service Account" \
        --description="Service account for Panelin API Cloud Run service" \
        --project="${PROJECT_ID}"
    echo -e "${GREEN}✓ Service account created${NC}"
else
    echo -e "${GREEN}✓ Service account already exists${NC}"
fi
echo ""

# ========================================
# Step 3: Grant IAM roles to service account
# ========================================
echo -e "${YELLOW}Step 3: Granting IAM roles...${NC}"

# Secret Manager Secret Accessor - to read secrets
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

# Cloud Trace Agent - for distributed tracing
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudtrace.agent" \
    --condition=None

# Cloud Monitoring Metric Writer - for custom metrics
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/monitoring.metricWriter" \
    --condition=None

# Logging Log Writer - for structured logging
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter" \
    --condition=None

echo -e "${GREEN}✓ IAM roles granted${NC}"
echo ""

# ========================================
# Step 4: Create secrets
# ========================================
echo -e "${YELLOW}Step 4: Creating secrets...${NC}"

# List of secrets to create
declare -A SECRETS=(
    ["openai-api-key"]="OpenAI API Key for LLM integration"
    ["mongodb-uri"]="MongoDB connection URI"
    ["google-sheets-credentials"]="Google Sheets API credentials JSON"
)

for SECRET_NAME in "${!SECRETS[@]}"; do
    DESCRIPTION="${SECRETS[$SECRET_NAME]}"
    
    # Check if secret exists
    if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
        echo "Creating secret: ${SECRET_NAME}"
        gcloud secrets create "${SECRET_NAME}" \
            --replication-policy="user-managed" \
            --locations="${REGION}" \
            --labels="app=panelin,env=production" \
            --project="${PROJECT_ID}"
        echo -e "${GREEN}✓ Secret '${SECRET_NAME}' created${NC}"
    else
        echo -e "${GREEN}✓ Secret '${SECRET_NAME}' already exists${NC}"
    fi
done
echo ""

# ========================================
# Step 5: Create Artifact Registry repository
# ========================================
echo -e "${YELLOW}Step 5: Creating Artifact Registry repository...${NC}"

if ! gcloud artifacts repositories describe panelin --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud artifacts repositories create panelin \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Docker repository for Panelin API" \
        --labels="app=panelin" \
        --project="${PROJECT_ID}"
    echo -e "${GREEN}✓ Artifact Registry repository created${NC}"
else
    echo -e "${GREEN}✓ Artifact Registry repository already exists${NC}"
fi
echo ""

# ========================================
# Summary and next steps
# ========================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Add secret values:"
echo "   echo -n 'your-openai-api-key' | gcloud secrets versions add openai-api-key --data-file=- --project=${PROJECT_ID}"
echo "   echo -n 'mongodb+srv://user:pass@cluster.mongodb.net/db' | gcloud secrets versions add mongodb-uri --data-file=- --project=${PROJECT_ID}"
echo ""
echo "2. Build and push Docker image:"
echo "   gcloud builds submit --config=deploy/cloudbuild.yaml --project=${PROJECT_ID}"
echo ""
echo "3. Deploy Cloud Run service:"
echo "   Replace PROJECT_ID in deploy/cloudrun-service.yaml, then run:"
echo "   gcloud run services replace deploy/cloudrun-service.yaml --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo "4. Configure access (if needed):"
echo "   # For public access:"
echo "   gcloud run services add-iam-policy-binding panelin-api --member='allUsers' --role='roles/run.invoker' --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo "   # For authenticated access only (recommended):"
echo "   gcloud run services add-iam-policy-binding panelin-api --member='serviceAccount:client@other-project.iam.gserviceaccount.com' --role='roles/run.invoker' --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}Important: Never commit secrets to version control!${NC}"
