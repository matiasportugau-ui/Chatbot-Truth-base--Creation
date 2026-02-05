#!/usr/bin/env python3
"""
Create or update WOLF_API_KEY in Google Secret Manager (Step 3 of Cloud Run deploy).

Reads WOLF_API_KEY from the project's .env file, then runs:
  gcloud secrets create WOLF_API_KEY --data-file=...
  or
  gcloud secrets versions add WOLF_API_KEY --data-file=...
if the secret already exists.

Usage (from repo root or scripts/):
  python scripts/create_wolf_secret_gcp.py

Requires: gcloud CLI installed and logged in, python-dotenv.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def find_gcloud():
    """Return path to gcloud (for Windows when not in PATH)."""
    import shutil
    exe = shutil.which("gcloud")
    if exe:
        return exe
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        for name in ("gcloud.cmd", "gcloud.bat"):
            p = Path(local) / "Google" / "Cloud SDK" / "google-cloud-sdk" / "bin" / name
            if p.exists():
                return str(p)
    return "gcloud"

# Project root = parent of scripts/ or cwd
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else Path.cwd()
ENV_FILE = PROJECT_ROOT / ".env"


def load_wolf_key():
    """Load WOLF_API_KEY from .env (simple parse, no extra deps if dotenv missing)."""
    if not ENV_FILE.exists():
        print(f"[ERROR] .env not found at {ENV_FILE}")
        print("Create .env with WOLF_API_KEY=your_key or run from repo root.")
        sys.exit(1)
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "WOLF_API_KEY":
            val = value.strip().strip('"').strip("'")
            if val:
                return val
            break
    print("[ERROR] WOLF_API_KEY is empty or missing in .env")
    print("Add a line: WOLF_API_KEY=your_secret_key")
    sys.exit(1)


def main():
    print("[1/3] Reading WOLF_API_KEY from .env ...")
    key = load_wolf_key()
    print("[2/3] Creating/updating secret in Google Secret Manager ...")

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(key)
            tmp = f.name
    except Exception as e:
        print(f"[ERROR] Failed to write temp file: {e}")
        sys.exit(1)

    gcloud = find_gcloud()
    try:
        # Try create first; if exists, add version
        r = subprocess.run(
            [
                gcloud,
                "secrets",
                "create",
                "WOLF_API_KEY",
                "--data-file=" + tmp,
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            if "already exists" in (r.stderr or "").lower() or "already exists" in (r.stdout or "").lower():
                r2 = subprocess.run(
                    [
                        gcloud,
                        "secrets",
                        "versions",
                        "add",
                        "WOLF_API_KEY",
                        "--data-file=" + tmp,
                    ],
                    capture_output=True,
                    text=True,
                )
                if r2.returncode != 0:
                    print("[ERROR] gcloud secrets versions add failed:")
                    print(r2.stderr or r2.stdout)
                    sys.exit(1)
                print("Secret WOLF_API_KEY already existed; added new version.")
            else:
                print("[ERROR] gcloud secrets create failed:")
                print(r.stderr or r.stdout)
                sys.exit(1)
        else:
            print("Secret WOLF_API_KEY created.")
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass

    print("[3/3] Done. You can continue with Step 4 (service account + deploy).")


if __name__ == "__main__":
    main()
