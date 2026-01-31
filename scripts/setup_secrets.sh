#!/bin/bash
# ============================================================================
# Secret Manager Setup Script
# ============================================================================
# This script sets up Secret Manager secrets for the Panelin API service
# and configures proper IAM permissions for Cloud Run access.
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - PROJECT_ID set as environment variable
# - User has Secret Manager Admin role
#
# Usage:
#   export PROJECT_ID=your-project-id
#   ./setup_secrets.sh
# ============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
SERVICE_ACCOUNT_NAME="panelin-api-sa"
SERVICE_NAME="panelin-api"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
if [ -z "$PROJECT_ID" ]; then
    log_error "PROJECT_ID environment variable is required"
    echo "Usage: PROJECT_ID=your-project-id ./setup_secrets.sh"
    exit 1
fi

log_info "Setting up secrets for project: $PROJECT_ID"

# Set project
gcloud config set project "$PROJECT_ID"

# -----------------------------------------------------------------------------
# Enable required APIs
# -----------------------------------------------------------------------------
log_info "Enabling required APIs..."
gcloud services enable \
    secretmanager.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com

# -----------------------------------------------------------------------------
# Create Service Account (if not exists)
# -----------------------------------------------------------------------------
log_info "Setting up service account..."

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &>/dev/null; then
    log_info "Creating service account: $SERVICE_ACCOUNT_NAME"
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --description="Panelin API Cloud Run service account" \
        --display-name="Panelin API Service Account"
else
    log_info "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
fi

# -----------------------------------------------------------------------------
# Grant minimum required roles to service account
# -----------------------------------------------------------------------------
log_info "Configuring IAM roles..."

# Cloud Run invoker (if service calls other Cloud Run services)
# gcloud projects add-iam-policy-binding "$PROJECT_ID" \
#     --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
#     --role="roles/run.invoker"

# Secret Manager accessor (read secrets at runtime)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

# Cloud Trace agent (for distributed tracing)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudtrace.agent" \
    --condition=None

# Cloud Logging writer
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/logging.logWriter" \
    --condition=None

log_info "IAM roles configured"

# -----------------------------------------------------------------------------
# Create Secrets
# -----------------------------------------------------------------------------
log_info "Creating secrets..."

# Function to create or update a secret
create_secret() {
    local secret_name="$1"
    local description="$2"
    
    if ! gcloud secrets describe "$secret_name" &>/dev/null; then
        log_info "Creating secret: $secret_name"
        gcloud secrets create "$secret_name" \
            --replication-policy="automatic" \
            --labels="app=panelin-api,environment=production"
        
        # Add description via labels
        echo "Secret created. Add value with:"
        echo "  echo -n 'YOUR_SECRET_VALUE' | gcloud secrets versions add $secret_name --data-file=-"
    else
        log_info "Secret already exists: $secret_name"
    fi
}

# Create required secrets
create_secret "openai-api-key" "OpenAI API key for Panelin agent"
create_secret "mongodb-uri" "MongoDB connection string"

# Optional secrets (uncomment as needed)
# create_secret "shopify-api-key" "Shopify API key for sync service"
# create_secret "google-sheets-credentials" "Google Sheets service account JSON"

# -----------------------------------------------------------------------------
# Grant service account access to specific secrets
# -----------------------------------------------------------------------------
log_info "Granting secret access to service account..."

grant_secret_access() {
    local secret_name="$1"
    
    gcloud secrets add-iam-policy-binding "$secret_name" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/secretmanager.secretAccessor"
}

grant_secret_access "openai-api-key"
grant_secret_access "mongodb-uri"

# -----------------------------------------------------------------------------
# Verify Setup
# -----------------------------------------------------------------------------
log_info "Verifying setup..."

echo ""
echo "============================================================================"
echo "Secret Manager Setup Complete"
echo "============================================================================"
echo ""
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "Secrets created:"
gcloud secrets list --filter="labels.app=panelin-api" --format="table(name,createTime)"
echo ""
echo "Next steps:"
echo "1. Add secret values:"
echo "   echo -n 'sk-your-openai-key' | gcloud secrets versions add openai-api-key --data-file=-"
echo ""
echo "2. Deploy Cloud Run with secrets:"
echo "   gcloud run deploy $SERVICE_NAME \\"
echo "     --service-account=$SERVICE_ACCOUNT_EMAIL \\"
echo "     --set-secrets='OPENAI_API_KEY=openai-api-key:latest,MONGODB_URI=mongodb-uri:latest'"
echo ""
echo "3. Or use the cloudrun-service.yaml:"
echo "   gcloud run services replace cloudrun-service.yaml"
echo ""
echo "============================================================================"
