# GPT Action for Cloud Run API

Use this when your API is deployed on **Cloud Run** (`https://panelin-api-q74zutv7dq-uc.a.run.app`).

## 1. Fix 403 Forbidden from Cloud Run

Cloud Run was deployed with **no public access** (`--no-allow-unauthenticated`), so Google blocks requests before they reach your app. The GPT only sends **X-API-Key**; it does not use Google IAM.

**Redeploy allowing unauthenticated traffic** (the app still enforces X-API-Key):

```cmd
cd c:\Users\usuario\Panelin\Chatbot-Truth-base--Creation
gcloud run deploy panelin-api --source . --region us-central1 --service-account panelin-runner@chatbot-bmc-live.iam.gserviceaccount.com --memory 512Mi --cpu 1 --timeout 300 --concurrency 80 --min-instances 0 --max-instances 10 --set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest" --allow-unauthenticated
```

Only change: **`--allow-unauthenticated`** instead of `--no-allow-unauthenticated`. After this, anyone can *reach* the URL; the FastAPI app still returns 403 for requests without a valid **X-API-Key**.

---

## 2. Use the correct OpenAPI schema

The live API uses **different paths and methods** than the old bundle:

| Old (wrong)              | Actual API              |
|--------------------------|--------------------------|
| GET `/` (health)         | GET `/health` (no auth) |
| GET `/products/search`   | **POST** `/find_products` (body: `{"query":"...","max_results":5}) |
| GET `/products/{id}/price` | **POST** `/product_price` (body: `{"product_id":"..."}`) |
| POST `/quotes`           | **POST** `/calculate_quote` (body: QuoteRequest) |

**In your GPT Action:**

1. Remove the current schema or replace it.
2. Import **`openapi_cloudrun.json`** from this folder (or paste its contents). It matches the real Cloud Run API.
3. Set **Authentication** to **API Key**:
   - **Auth type:** API Key  
   - **Header name:** `X-API-Key`  
   - **Value:** your WOLF_API_KEY (same as in Secret Manager / `.env`).

---

## 3. Summary

- Redeploy once with **`--allow-unauthenticated`** so the GPT can reach the service.
- Use **`openapi_cloudrun.json`** in the GPT Action so it calls `/health`, `/find_products`, `/calculate_quote`, etc., with the right methods and bodies.
- Keep **X-API-Key** set in the Action so the app accepts the requests.
