import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Add project root to sys.path to allow importing from config
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config.settings import settings

# Setup paths
AGENT_V2_DIR = PROJECT_ROOT / "panelin_agent_v2"
OPENAPI_PATH = PROJECT_ROOT / "deployment_bundle" / "openapi.json"


def log(msg):
    print(f"[WOLF-DEPLOY] {msg}")
    sys.stdout.flush()


def kill_port(port):
    log(f"Cleaning port {port}...")
    try:
        # Use a more cross-platform way if possible, but keeping this for now
        # Replacing shell=True with list for safety
        if sys.platform != "win32":
            subprocess.run(
                ["pkill", "-f", f":{port}"], stderr=subprocess.DEVNULL
            )
    except Exception:
        pass


def main():
    log("🐺 INITIALIZING DEPLOY THE WOLF 🐺")

    # 1. Kill old processes
    kill_port(8000)

    # 2. Start API
    log("Starting API Server...")
    api_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=AGENT_V2_DIR,
    )
    time.sleep(3)

    # 3. Start Tunnel
    log("Starting Localtunnel...")
    url_file = PROJECT_ROOT / "tunnel_url.txt"
    if url_file.exists():
        url_file.unlink()

    # Fixed security risk: shell=True removed
    tunnel_proc = subprocess.Popen(
        ["npx", "localtunnel", "--port", "8000"],
        stdout=open(url_file, "w"),
        stderr=subprocess.STDOUT
    )

    url = None
    start_time = time.time()
    while time.time() - start_time < 20:
        if url_file.exists():
            content = url_file.read_text()
            if "your url is:" in content:
                url = content.split("your url is:")[1].strip()
                break
        time.sleep(1)

    if not url:
        log("CRITICAL ERROR: Could not get Localtunnel URL.")
        api_proc.terminate()
        tunnel_proc.terminate()
        sys.exit(1)

    # 4. Update Schema
    log(f"Updating Schema with URL: {url}")
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    schema["servers"] = [{"url": url, "description": "Localtunnel Development Server"}]
    
    # Add Security Scheme (API Key)
    if "components" not in schema:
        schema["components"] = {}
    
    schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    schema["security"] = [{"ApiKeyAuth": []}]

    wolf_key = settings.WOLF_API_KEY

    print("\n" + "=" * 50)
    print("🚀 DEPLOYMENT DATA READY 🚀")
    print("=" * 50)
    print("\n1. ACTION SCHEMA (Copy/Paste this entirely):")
    print("-" * 30)
    print(json.dumps(schema, indent=2))
    print("-" * 30)
    print("\n2. AUTHENTICATION SETUP:")
    print("Type: API Key")
    print("Parameter Name: X-API-Key")
    
    if not wolf_key:
        masked_key = "NOT_SET (Check your keyring or .env file)"
    else:
        masked_key = f"{wolf_key[:4]}...{wolf_key[-4:]}" if len(wolf_key) > 8 else "****"
    
    print(f"API Key: {masked_key}")
    print("\n3. PRIVACY POLICY URL:")
    print("https://bmcuruguay.com.uy/privacy")
    print("\n" + "=" * 50)
    print(f"🔗 LIVE URL: {url}")
    print("⚠️  KEEP THIS TERMINAL RUNNING!")
    print("=" * 50)
    sys.stdout.flush()

    # Keep script alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        api_proc.terminate()
        tunnel_proc.terminate()


if __name__ == "__main__":
    main()
