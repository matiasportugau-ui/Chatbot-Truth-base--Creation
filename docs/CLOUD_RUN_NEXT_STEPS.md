# Cloud Run — Next steps (step-by-step)

Follow these in order. Use **PowerShell** or **Command Prompt** from the repo root.

---

## Step 0: Prerequisites

- **Google Cloud project** with billing enabled.
- **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install

Check:

```powershell
gcloud --version
gcloud config get-value project
```

If no project is set:

```powershell
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 1: Enable required APIs

Run once per project:

```powershell
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

Wait until it finishes. If it asks to enable billing, do it for the project.

---

## Step 2: Create Artifact Registry repo

Run once per project:

```powershell
gcloud artifacts repositories create panelin --repository-format=docker --location=us-central1
```

If you get "already exists", you can skip this step.

---

## Step 3: Create the WOLF_API_KEY secret

**What is this?**  
The Panelin API only accepts requests that send a password in the header `X-API-Key`. That password is called **WOLF_API_KEY**. You store it once in Google Secret Manager; Cloud Run then injects it into your app so the API can check incoming keys.

**What value do I use?**  
- If you already have a `WOLF_API_KEY` in your project’s `.env` file, use that same value.  
- If not, use any long random string you make up (e.g. `MySecretKey123XYZ` or a 32-character random string). You’ll use this same value later when configuring your GPT Action.

---

### Automated (recommended)

From the **repo root**, with **WOLF_API_KEY** set in your `.env`:

```cmd
cd c:\Users\usuario\Panelin\Chatbot-Truth-base--Creation
python scripts\create_wolf_secret_gcp.py
```

The script reads `WOLF_API_KEY` from `.env`, creates the secret in Google (or adds a new version if it already exists), and exits. No manual file or copy-paste needed.

---

### Manual: Easiest way (Command Prompt) — use a file

**3a. Create a file with your key**

1. Open **Notepad**.
2. Type **only** your key (no spaces, no extra lines). Examples:
   - `MySecretKey123XYZ`
   - Or copy the value of `WOLF_API_KEY` from your `.env` file.
3. Save the file:
   - **File → Save As**
   - Go to: `c:\Users\usuario\Panelin\Chatbot-Truth-base--Creation`
   - **File name:** `wolf_key.txt`
   - **Save as type:** All Files (*.*)
   - Click **Save**.
4. Close Notepad.

**3b. Tell Google to create the secret from that file**

In **Command Prompt** (or Google Cloud SDK shell), run:

```cmd
cd c:\Users\usuario\Panelin\Chatbot-Truth-base--Creation
gcloud secrets create WOLF_API_KEY --data-file=wolf_key.txt
```

If you see **"already exists"**, add a new version instead:

```cmd
gcloud secrets versions add WOLF_API_KEY --data-file=wolf_key.txt
```

**3c. Delete the file (so the key isn’t left on disk)**

```cmd
del wolf_key.txt
```

Step 3 is done when `gcloud secrets create` (or `versions add`) succeeds.

---

### Alternative: PowerShell (if you use PowerShell)

Replace `YOUR_ACTUAL_KEY` with your real key:

```powershell
$key = "YOUR_ACTUAL_KEY"
$key | gcloud secrets create WOLF_API_KEY --data-file=-
```

If the secret already exists:

```powershell
$key = "YOUR_ACTUAL_KEY"
$key | gcloud secrets versions add WOLF_API_KEY --data-file=-
```

---

## Step 4: Create service account and grant access to the secret

Run (replace `YOUR_PROJECT_ID` if you don’t use `gcloud config`):

```powershell
$PROJECT_ID = gcloud config get-value project
gcloud iam service-accounts create panelin-runner --display-name "Panelin Cloud Run"
```

Then grant the service account access to **WOLF_API_KEY**:

```powershell
$SA_EMAIL = "panelin-runner@$PROJECT_ID.iam.gserviceaccount.com"
gcloud secrets add-iam-policy-binding WOLF_API_KEY --member="serviceAccount:$SA_EMAIL" --role="roles/secretmanager.secretAccessor"
```

If the service account already exists (e.g. "already exists" error), skip the create and only run the `add-iam-policy-binding` line.

---

## Step 5: First deploy (with secrets)

From the **repo root** (where `Dockerfile` and `cloudbuild.yaml` are):

```powershell
cd c:\Users\usuario\Panelin\Chatbot-Truth-base--Creation

$PROJECT_ID = gcloud config get-value project
$SA_EMAIL = "panelin-runner@$PROJECT_ID.iam.gserviceaccount.com"

gcloud run deploy panelin-api `
  --source . `
  --region us-central1 `
  --service-account $SA_EMAIL `
  --memory 512Mi --cpu 1 --timeout 300 --concurrency 80 `
  --min-instances 0 --max-instances 10 `
  --set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest" `
  --no-allow-unauthenticated
```

- **--source .** builds the image from the current directory (uses the Dockerfile) and deploys it.
- The first run can take several minutes (build + deploy).

When it finishes, it will print the **service URL**, e.g. `https://panelin-api-xxxxx-uc.a.run.app`.

---

## Step 6: Check that it works

**Health (no auth):**

```powershell
# Replace with your actual URL from Step 5
curl https://panelin-api-XXXXX-uc.a.run.app/health
```

You should get something like: `{"status":"ok"}`.

**Ready (no auth):**

```powershell
curl https://panelin-api-XXXXX-uc.a.run.app/ready
```

You should get: `{"status":"ready"}` if WOLF_API_KEY is set correctly.

**Authenticated root (use your WOLF_API_KEY):**

```powershell
curl -H "X-API-Key: YOUR_WOLF_API_KEY" https://panelin-api-XXXXX-uc.a.run.app/
```

---

## Step 7: Use this URL in your GPT / OpenAPI

1. Copy the Cloud Run URL (e.g. `https://panelin-api-xxxxx-uc.a.run.app`).
2. Open `deployment_bundle/openapi.json`.
3. Set **servers** to that URL, e.g.:

   `"servers": [ { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" } ]`

4. In your GPT Action, use the same **X-API-Key** value as the one you stored in Secret Manager (WOLF_API_KEY).

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| `gcloud: command not found` | Install Cloud SDK and restart the terminal. |
| `Permission denied` / 403 | Check that the APIs are enabled and your user has roles like "Cloud Run Admin", "Secret Manager Admin", "Service Account User". |
| Build fails | Ensure you run from the repo root (where `Dockerfile` is). Check that `config/` and `panelin_agent_v2/` exist. |
| 503 on `/ready` | WOLF_API_KEY is not reaching the service. Check Secret Manager and `--set-secrets` in the deploy command. |
| 403 on `/` with correct key | Confirm the key in the request matches the value in Secret Manager (WOLF_API_KEY). |

---

## Later: Deploy updates with Cloud Build

After the first deploy, you can use Cloud Build to build and deploy on push (or manually):

```powershell
gcloud builds submit --config=cloudbuild.yaml .
```

To have Cloud Build also inject secrets, add to the deploy step in `cloudbuild.yaml` (see comments there):

- `--service-account panelin-runner@PROJECT_ID.iam.gserviceaccount.com`
- `--set-secrets "WOLF_API_KEY=WOLF_API_KEY:latest"`

---

## Next steps after deploy (Cloud Run live)

| Step | Action |
|------|--------|
| **1. GPT Action** | In your GPT (e.g. Panelin – BMC Assistant), add an Action. Use **OpenAPI URL** or paste the schema from `deployment_bundle/openapi.json` (servers URL is already set to your Cloud Run URL). Set **Authentication** to API Key, **Header name** `X-API-Key`, **Value** = same as `WOLF_API_KEY` in Secret Manager (and `.env`). |
| **2. Test the GPT** | In the GPT, trigger a quote or product search and confirm the Action calls your Cloud Run API and returns data. |
| **3. Privacy / terms** | If required, set the GPT’s **Privacy policy URL** (e.g. `https://bmcuruguay.com.uy/privacy`) in the GPT configuration. |
| **4. Future deploys** | From repo root: `gcloud run deploy panelin-api --source . --region us-central1 ...` (same command as Step 5), or set up **Cloud Build** with `gcloud builds submit --config=cloudbuild.yaml .` and add `--set-secrets` in `cloudbuild.yaml` so CI/CD injects the key. |
| **5. Monitoring (optional)** | In [Cloud Console → Cloud Run → panelin-api → Metrics](https://console.cloud.google.com/run/detail/us-central1/panelin-api/metrics?project=chatbot-bmc-live), watch requests, latency, and errors. Optionally add alerts for error rate or latency. |
| **6. OpenAPI schema** | `deployment_bundle/openapi.json` already has `servers[].url` = your Cloud Run URL. If you use a different schema for the GPT (e.g. from `scripts/deploy_thewolf.py` output), ensure its **servers** URL and **X-API-Key** match. |
