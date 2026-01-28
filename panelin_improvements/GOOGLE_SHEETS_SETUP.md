# Google Sheets Setup (Cost Matrix)

This guide sets up the Service Account credentials required by
`panelin_improvements/cost_matrix_tools/gsheets_manager.py`.

## 1) Create a Google Cloud Project

1. Go to the Google Cloud Console.
2. Create a new project (or select an existing one).

## 2) Enable the Google Sheets API

1. In the project, open **APIs & Services** → **Library**.
2. Enable **Google Sheets API**.
3. Also enable **Google Drive API** (required by gspread).

## 3) Create a Service Account

1. Go to **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **Service Account**.
3. Assign a name and finish creation.

## 4) Generate a JSON key

1. In the Service Account page, go to **Keys**.
2. Click **Add Key** → **Create new key** → JSON.
3. Download the file and rename it to `credentials.json`.

## 5) Place the credentials file locally

Copy the file to:

```
panelin_improvements/credentials.json
```

This file is ignored by git. Do not commit it.

## 6) Share the Google Sheet

1. Open the Google Sheet used for the cost matrix.
2. Share it with the Service Account email (found in the JSON file).
3. Give it **Editor** access.

## 7) Verify dependencies

Install dependencies:

```
pip install -r panelin_improvements/requirements.txt
```

## 8) Quick validation

Run a sync up:

```
python3 -m panelin_improvements.cost_matrix_tools.gsheets_manager sync_up \
  "wiki/matriz de costos adaptacion /redesigned/BROMYROS_Costos_Ventas_2026_OPTIMIZED.json" \
  "panelin_improvements/credentials.json" \
  "BROMYROS_Costos_Ventas_2026"
```

If this succeeds, the connection is working.

## Troubleshooting

- **SpreadsheetNotFound**: Ensure the Service Account has access to the sheet.
- **Invalid credentials**: Re-download the JSON key.
- **API not enabled**: Enable Google Sheets + Drive APIs in the project.
