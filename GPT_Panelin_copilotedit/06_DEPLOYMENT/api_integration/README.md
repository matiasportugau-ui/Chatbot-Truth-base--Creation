# Panelin V3 API Deployment

This directory contains the deployment configuration for the Panelin V3 Quotation Calculator API.

## Architecture

- **Service**: FastAPI REST API
- **Platform**: Google Cloud Run
- **Container Registry**: Google Container Registry (GCR)
- **Deployment**: Automated via GitHub Actions

## Files

### `main.py`
FastAPI application that wraps the `quotation_calculator_v3.py` module with a REST API.

**Endpoints**:
- `POST /v3/quote` - Calculate panel quotation
- `GET /health` - Health check for Cloud Run
- `GET /` - API info payload (interactive API docs at `/docs` and `/redoc`)

### `Dockerfile`
Container image definition for Google Cloud Run.

**Build Context**: `GPT_Panelin_copilotedit/` (parent directory)

**Image Contents**:
- Python 3.11 slim base
- Calculator module (`03_PYTHON_TOOLS/quotation_calculator_v3.py`)
- Knowledge base files (`01_KNOWLEDGE_BASE/`)
- FastAPI application

### `requirements.txt`
Python dependencies for the API service:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

## Deployment

### Automated Deployment (GitHub Actions)

The workflow `.github/workflows/deploy-panelin-v3.yml` automatically deploys to Cloud Run when:
- Changes are pushed to the `main` branch
- Changes occur in the `GPT_Panelin_copilotedit/**` directory

**Required GitHub Secrets**:
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCP_SA_KEY` - Service account key JSON (with Cloud Run and GCR permissions)
- `WOLF_API_KEY` - API key for the WOLF service (passed as environment variable)

**Workflow Steps**:
1. Authenticate with Google Cloud
2. Build Docker image with tag `<commit-sha>` and `latest`
3. Push image to GCR
4. Deploy to Cloud Run service `panelin-v3-api`

### Manual Deployment

#### Prerequisites
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Build and Deploy
```bash
# From repository root
cd GPT_Panelin_copilotedit

# Build the Docker image
docker build \
  -t gcr.io/YOUR_PROJECT_ID/panelin-v3-api:latest \
  -f 06_DEPLOYMENT/api_integration/Dockerfile \
  .

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/panelin-v3-api:latest

# Deploy to Cloud Run
gcloud run deploy panelin-v3-api \
  --image gcr.io/YOUR_PROJECT_ID/panelin-v3-api:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars WOLF_API_KEY=your_key_here \
  --memory 512Mi \
  --cpu 1
```

## API Usage

### Example Request

```bash
curl -X POST "https://panelin-v3-api-xxxxx.run.app/v3/quote" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "ISOPANEL_EPS_50mm",
    "length_m": 6.0,
    "width_m": 10.0,
    "quantity": 1,
    "discount_percent": 0,
    "include_accessories": true,
    "include_tax": true,
    "installation_type": "techo",
    "validate_span": true
  }'
```

### Response Structure

```json
{
  "success": true,
  "data": {
    "quotation_id": "Q-20260208-xxxxx",
    "product_id": "ISOPANEL_EPS_50mm",
    "product_name": "Isopanel EPS 50mm",
    "length_m": 6.0,
    "width_m": 10.0,
    "area_m2": 60.0,
    "price_per_m2_usd": 41.88,
    "subtotal_usd": 2512.80,
    "total_usd": 3065.62,
    "calculation_verified": true,
    ...
  }
}
```

## Configuration

### Environment Variables

The API respects the following environment variables:

- `PORT` (default: 8080) - Server port (set by Cloud Run)
- `WOLF_API_KEY` - API key for WOLF service integration

### Cloud Run Configuration

Current settings:
- **Memory**: 512Mi
- **CPU**: 1
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero)
- **Timeout**: 60s
- **Authentication**: Allowed unauthenticated (public API)

To modify these settings, edit `.github/workflows/deploy-panelin-v3.yml` or use `gcloud run services update`.

## Monitoring

### Health Check
```bash
curl https://panelin-v3-api-xxxxx.run.app/health
```

### Cloud Run Logs
```bash
gcloud run services logs read panelin-v3-api --region us-central1
```

### API Documentation
Navigate to `https://panelin-v3-api-xxxxx.run.app/docs` for interactive Swagger UI.

## Troubleshooting

### Container Won't Start
- Check Cloud Run logs for startup errors
- Verify knowledge base files are present in the image
- Ensure PORT environment variable is set to 8080

### Calculator Errors
- Verify `panelin_truth_bmcuruguay.json` exists at `01_KNOWLEDGE_BASE/Level_1_Master/`
- Verify `accessories_catalog.json` exists at `01_KNOWLEDGE_BASE/Level_1_2_Accessories/`
- Verify `bom_rules.json` exists at `01_KNOWLEDGE_BASE/Level_1_3_BOM_Rules/`

### Authentication Issues
- Verify `GCP_SA_KEY` secret has correct permissions:
  - Cloud Run Admin
  - Storage Admin (for GCR)
  - Service Account User

## Development

### Local Testing

```bash
# Install dependencies
cd GPT_Panelin_copilotedit/06_DEPLOYMENT/api_integration
pip install -r requirements.txt

# Run locally (from GPT_Panelin_copilotedit directory)
cd ../..
python3 06_DEPLOYMENT/api_integration/main.py

# API will be available at http://localhost:8080
```

### Testing with Docker

```bash
# Build image locally
docker build -t panelin-v3-api:local \
  -f 06_DEPLOYMENT/api_integration/Dockerfile \
  GPT_Panelin_copilotedit/

# Run container
docker run -p 8080:8080 \
  -e WOLF_API_KEY=test_key \
  panelin-v3-api:local

# Test
curl http://localhost:8080/health
```
