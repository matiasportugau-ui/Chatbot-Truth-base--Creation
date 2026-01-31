import os
import sys
import json
import signal
import subprocess
import time
import platform
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_V2_DIR = PROJECT_ROOT / "Copia de panelin_agent_v2"
OPENAPI_PATH = PROJECT_ROOT / "deployment_bundle" / "openapi.json"

IS_WINDOWS = platform.system() == "Windows"


def log(msg):
    print(f"[WOLF-DEPLOY] {msg}")
    sys.stdout.flush()


def kill_port(port):
    """Kill any process listening on the given port (cross-platform)."""
    log(f"Cleaning port {port}...")
    try:
        if IS_WINDOWS:
            # Find PIDs using netstat, then kill them
            result = subprocess.run(
                f'netstat -ano | findstr :{port} | findstr LISTENING',
                shell=True, capture_output=True, text=True
            )
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    subprocess.run(
                        f"taskkill /F /PID {pid}",
                        shell=True, stderr=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                    )
        else:
            subprocess.run(
                f"lsof -ti:{port} | xargs kill -9",
                shell=True, stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass


def start_tunnel(url_file: Path):
    """
    Start localtunnel and capture the public URL.

    Returns (subprocess.Popen, str | None) -- the tunnel process and the
    extracted URL (or None on failure).
    """
    if url_file.exists():
        url_file.unlink()

    # Use subprocess.PIPE so we can read stdout directly instead of relying
    # on shell redirects (which behave differently on Windows/PowerShell).
    tunnel_proc = subprocess.Popen(
        ["npx", "localtunnel", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    url = None
    start_time = time.time()
    timeout_seconds = 30

    while time.time() - start_time < timeout_seconds:
        line = tunnel_proc.stdout.readline()
        if not line:
            # Process may have exited
            if tunnel_proc.poll() is not None:
                log("Localtunnel process exited unexpectedly.")
                break
            time.sleep(0.5)
            continue

        line = line.strip()
        if line:
            log(f"  tunnel> {line}")

        if "your url is:" in line.lower():
            url = line.split("is:")[-1].strip()
            break

    return tunnel_proc, url


def main():
    log("\U0001f43a INITIALIZING DEPLOY THE WOLF \U0001f43a")

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

    # Check the API process is still alive
    if api_proc.poll() is not None:
        log("CRITICAL ERROR: API server failed to start.")
        sys.exit(1)

    # 3. Start Tunnel
    log("Starting Localtunnel...")
    url_file = PROJECT_ROOT / "tunnel_url.txt"
    tunnel_proc, url = start_tunnel(url_file)

    if not url:
        log("CRITICAL ERROR: Could not get Localtunnel URL.")
        log("Make sure Node.js / npx is installed and you have internet access.")
        log("You can test manually: npx localtunnel --port 8000")
        api_proc.terminate()
        if tunnel_proc.poll() is None:
            tunnel_proc.terminate()
        sys.exit(1)

    # Save URL for reference
    url_file.write_text(url)

    # 4. Update Schema
    log(f"Updating Schema with URL: {url}")
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    schema["servers"] = [{"url": url, "description": "Localtunnel Development Server"}]

    print("\n" + "=" * 50)
    print("\U0001f680 DEPLOYMENT DATA READY \U0001f680")
    print("=" * 50)
    print("\n1. ACTION SCHEMA (Copy/Paste this entirely):")
    print("-" * 30)
    print(json.dumps(schema, indent=2))
    print("-" * 30)
    print("\n2. AUTHENTICATION SETUP:")
    print("Type: None (Ninguno)")
    print("\n3. PRIVACY POLICY URL:")
    print("https://bmcuruguay.com.uy/privacy")
    print("\n" + "=" * 50)
    print(f"\U0001f517 LIVE URL: {url}")
    print("\u26a0\ufe0f  KEEP THIS TERMINAL RUNNING!")
    print("=" * 50)
    sys.stdout.flush()

    # Keep script alive
    try:
        while True:
            # Periodically check that subprocesses are still running
            if api_proc.poll() is not None:
                log("WARNING: API server process has exited.")
                break
            if tunnel_proc.poll() is not None:
                log("WARNING: Tunnel process has exited.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        api_proc.terminate()
        if tunnel_proc.poll() is None:
            tunnel_proc.terminate()


if __name__ == "__main__":
    main()
