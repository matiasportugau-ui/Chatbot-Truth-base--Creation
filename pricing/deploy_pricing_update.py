#!/usr/bin/env python3
"""
Deploy Pricing Update
Orchestrates the full pricing update cycle.
"""
import os
import sys
import shutil

# Hardcode paths relative to where script is run (workspace root)
PRICING_DIR = "pricing"
TOOLS_DIR = "pricing/tools"
KB_DIR = "gpt_consolidation_agent/deployment/knowledge_base"
MASTER_FILE = f"{KB_DIR}/bromyros_pricing_master.json"

def run_step(script_path, description):
    print(f"\n>>> {description}...")
    # Escape spaces for shell execution if needed, but since we are in root and paths are relative without spaces, it should be fine.
    # Wait, the CWD has spaces! "Chatbot Truth base Creation"
    # When python runs `os.system("python3 relative/path.py")`, it should work regardless of CWD name.
    # The issue was likely how I constructed the absolute path in previous attempts.
    
    cmd = f'python3 "{script_path}"'
    ret = os.system(cmd)
    if ret != 0:
        print(f"❌ Error during: {description}")
        sys.exit(1)
    print("✅ Done.")

def deploy():
    # 1. Generate Base
    run_step(f"{PRICING_DIR}/generate_gpt_reference.py", "Generating Base Reference from CSV")
    
    # 2. Enrich
    run_step(f"{TOOLS_DIR}/enrich_product_data.py", "Enriching with Rules & Manual Data")
    
    # 3. Validate
    run_step(f"{PRICING_DIR}/validate_product_data.py", "Validating Data Integrity")
    
    # 4. Deploy
    print(f"\n>>> Deploying to Knowledge Base: {MASTER_FILE}...")
    source = f"{PRICING_DIR}/out/bromyros_pricing_reference.json"
    if not os.path.exists(source):
        print(f"❌ Error: Source file {source} not found.")
        sys.exit(1)
        
    os.makedirs(KB_DIR, exist_ok=True)
    shutil.copy(source, MASTER_FILE)
    print(f"✅ Successfully deployed to {MASTER_FILE}")
    
    print("\n🎉 Deployment Complete! The GPT now has access to the latest pricing & production rules.")

if __name__ == "__main__":
    deploy()
