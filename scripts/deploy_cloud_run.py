#!/usr/bin/env python3
"""
Cloud Run Deployment Script for Panelin API
============================================

This script automates the deployment of the Panelin Agent V2 API to Google Cloud Run.

Usage:
    python scripts/deploy_cloud_run.py [--project PROJECT_ID] [--region REGION] [--service SERVICE_NAME]

Prerequisites:
    - gcloud CLI installed and authenticated
    - Docker installed (optional, Cloud Build can build remotely)
    - Artifact Registry repository created
    - Service account with necessary permissions

Environment Variables:
    GCP_PROJECT_ID: Google Cloud Project ID
    GCP_REGION: Google Cloud Region (default: us-central1)
    GCP_SERVICE_NAME: Cloud Run service name (default: panelin-api)
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_V2_DIR = PROJECT_ROOT / "Copia de panelin_agent_v2"
OPENAPI_PATH = PROJECT_ROOT / "deployment_bundle" / "openapi.json"


def log(msg, level="INFO"):
    """Log a message with a prefix."""
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
    }.get(level, "ℹ️")
    print(f"[{prefix}] {msg}")
    sys.stdout.flush()


def run_command(cmd, cwd=None, capture_output=False):
    """Run a shell command and handle errors."""
    log(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=True,
        )
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e}", level="ERROR")
        if capture_output and e.stderr:
            log(f"Error output: {e.stderr}", level="ERROR")
        return None


def check_prerequisites():
    """Check if required tools are installed."""
    log("Checking prerequisites...")
    
    # Check gcloud
    if not run_command("gcloud --version", capture_output=True):
        log("gcloud CLI not found. Please install it first.", level="ERROR")
        return False
    
    # Check if authenticated
    if not run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'", capture_output=True):
        log("Not authenticated with gcloud. Please run: gcloud auth login", level="ERROR")
        return False
    
    log("Prerequisites check passed", level="SUCCESS")
    return True


def create_artifact_registry(project_id, region, repo_name="panelin"):
    """Create Artifact Registry repository if it doesn't exist."""
    log(f"Checking Artifact Registry repository '{repo_name}'...")
    
    # Check if repository exists
    check_cmd = f"gcloud artifacts repositories describe {repo_name} --location={region} --project={project_id} 2>/dev/null"
    if run_command(check_cmd, capture_output=True):
        log(f"Artifact Registry repository '{repo_name}' already exists", level="SUCCESS")
        return True
    
    # Create repository
    log(f"Creating Artifact Registry repository '{repo_name}'...")
    create_cmd = f"""gcloud artifacts repositories create {repo_name} \
        --repository-format=docker \
        --location={region} \
        --project={project_id}"""
    
    if run_command(create_cmd):
        log(f"Artifact Registry repository '{repo_name}' created", level="SUCCESS")
        return True
    else:
        log(f"Failed to create Artifact Registry repository", level="ERROR")
        return False


def deploy_to_cloud_run(project_id, region, service_name, allow_public=True):
    """Deploy the API to Cloud Run using Cloud Build."""
    log(f"Deploying '{service_name}' to Cloud Run...")
    
    # Build and deploy using gcloud run deploy with --source
    deploy_cmd = f"""gcloud run deploy {service_name} \
        --source {AGENT_V2_DIR} \
        --region {region} \
        --project {project_id} \
        --platform managed \
        --memory 512Mi \
        --cpu 1 \
        --timeout 300 \
        --concurrency 80 \
        --min-instances 0 \
        --max-instances 10"""
    
    if allow_public:
        deploy_cmd += " --allow-unauthenticated"
    else:
        deploy_cmd += " --no-allow-unauthenticated"
    
    if not run_command(deploy_cmd):
        log("Deployment failed", level="ERROR")
        return None
    
    # Get the service URL
    url_cmd = f"gcloud run services describe {service_name} --region {region} --project {project_id} --format 'value(status.url)'"
    service_url = run_command(url_cmd, capture_output=True)
    
    if service_url:
        log(f"Service deployed successfully: {service_url}", level="SUCCESS")
        return service_url
    else:
        log("Failed to get service URL", level="ERROR")
        return None


def update_openapi_schema(service_url):
    """Update the OpenAPI schema with the Cloud Run URL."""
    log("Updating OpenAPI schema...")
    
    if not OPENAPI_PATH.exists():
        log(f"OpenAPI schema not found at {OPENAPI_PATH}", level="WARNING")
        log("Skipping schema update", level="WARNING")
        return
    
    try:
        with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        schema["servers"] = [
            {"url": service_url, "description": "Cloud Run Production"}
        ]
        
        with open(OPENAPI_PATH, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        log("OpenAPI schema updated", level="SUCCESS")
        print("\n" + "=" * 60)
        print("📋 UPDATED OPENAPI SCHEMA")
        print("=" * 60)
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        print("=" * 60)
    except Exception as e:
        log(f"Failed to update OpenAPI schema: {e}", level="ERROR")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Panelin API to Cloud Run")
    parser.add_argument("--project", help="Google Cloud Project ID")
    parser.add_argument("--region", default="us-central1", help="Google Cloud Region")
    parser.add_argument("--service", default="panelin-api", help="Cloud Run service name")
    parser.add_argument("--private", action="store_true", help="Deploy as private (IAM authentication required)")
    args = parser.parse_args()
    
    # Get project ID
    project_id = args.project or os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        # Try to get from gcloud config
        project_id = run_command("gcloud config get-value project", capture_output=True)
    
    if not project_id:
        log("Project ID not specified. Use --project or set GCP_PROJECT_ID", level="ERROR")
        sys.exit(1)
    
    region = args.region or os.environ.get("GCP_REGION", "us-central1")
    service_name = args.service or os.environ.get("GCP_SERVICE_NAME", "panelin-api")
    allow_public = not args.private
    
    print("\n" + "=" * 60)
    print("🚀 CLOUD RUN DEPLOYMENT - PANELIN API")
    print("=" * 60)
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print(f"Service Name: {service_name}")
    print(f"Access: {'Public (unauthenticated)' if allow_public else 'Private (IAM authenticated)'}")
    print("=" * 60 + "\n")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Create Artifact Registry if needed
    if not create_artifact_registry(project_id, region):
        log("Failed to set up Artifact Registry", level="ERROR")
        sys.exit(1)
    
    # Deploy to Cloud Run
    service_url = deploy_to_cloud_run(project_id, region, service_name, allow_public)
    if not service_url:
        sys.exit(1)
    
    # Update OpenAPI schema
    update_openapi_schema(service_url)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 60)
    print(f"🔗 Service URL: {service_url}")
    print(f"🏥 Health Check: {service_url}/health")
    print(f"📖 API Docs: {service_url}/docs")
    print(f"📊 OpenAPI Spec: {service_url}/openapi.json")
    print("\n🔍 Monitor the service:")
    print(f"   gcloud run services describe {service_name} --region {region} --project {project_id}")
    print("\n📝 View logs:")
    print(f"   gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name={service_name}' --project {project_id} --limit 50")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
