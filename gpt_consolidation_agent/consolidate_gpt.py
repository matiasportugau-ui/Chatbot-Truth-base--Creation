import os
import shutil
import json
import sys
from pathlib import Path
import datetime

# Add root directory to sys.path to allow importing verify_gpt_configuration if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from verify_gpt_configuration import GPTConfigurationVerifier
except ImportError:
    print("Warning: verify_gpt_configuration.py not found in root. Verification step will be skipped.")
    GPTConfigurationVerifier = None

class GPTConsolidator:
    def __init__(self, output_dir="gpt_consolidation_agent/deployment"):
        self.root_dir = Path(".").resolve()
        self.output_dir = Path(output_dir).resolve()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define sources
        self.sources = {
            "instructions": "docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md",
            "kb_master": "BMC_Base_Conocimiento_GPT-2.json",
            "kb_validation": "BMC_Base_Unificada_v4.json", 
            "kb_dynamic": "panelin_truth_bmcuruguay_web_only_v2.json",
            "kb_guide": "PANELIN_KNOWLEDGE_BASE_GUIDE.md",
            "kb_quotation": "PANELIN_QUOTATION_PROCESS.md",
            "kb_training": "PANELIN_TRAINING_GUIDE.md",
            "sop_context": "panelin_context_consolidacion_sin_backend.md",
            "aleros": "Files /Aleros -2.rtf",
            "config_json": "gpt_configs/Panelin_Asistente_Integral_BMC_config.json"
        }
        
    def setup_deployment_dir(self):
        """Creates the deployment directory structure."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "knowledge_base").mkdir()
        (self.output_dir / "config").mkdir()
        (self.output_dir / "actions").mkdir()
        
        print(f"📁 Created deployment directory at {self.output_dir}")

    def run_verification(self):
        """Runs the verification script."""
        if not GPTConfigurationVerifier:
            return "SKIPPED"
        
        print("\n🔍 Running pre-consolidation verification...")
        verifier = GPTConfigurationVerifier(base_path=str(self.root_dir))
        results = verifier.verify_all()
        
        # Save verification report
        report_path = self.output_dir / "verification_report.txt"
        with open(report_path, "w") as f:
            for res in results:
                f.write(f"[{res.status}] {res.message}\n")
                if res.details:
                    for det in res.details:
                        f.write(f"  - {det}\n")
        
        fail_count = sum(1 for r in results if r.status == "FAIL")
        if fail_count > 0:
            print(f"⚠️  Verification failed with {fail_count} errors. See {report_path}")
            return "FAILED"
        else:
            print(f"✅ Verification passed.")
            return "PASSED"

    def consolidate_files(self):
        """Copies and organizes files."""
        print("\n📦 Consolidating files...")
        
        manifest = {
            "timestamp": self.timestamp,
            "files": []
        }

        # 1. Instructions
        src_instr = self.root_dir / self.sources["instructions"]
        if src_instr.exists():
            dst_instr = self.output_dir / "instructions.md"
            shutil.copy2(src_instr, dst_instr)
            manifest["files"].append({"type": "instructions", "path": "instructions.md", "source": str(src_instr)})
            print(f"  ✓ Copied instructions from {src_instr.name}")
        else:
            print(f"  ❌ Instructions file missing: {src_instr}")

        # 2. Knowledge Base
        kb_keys = ["kb_master", "kb_validation", "kb_dynamic", "kb_guide", "kb_quotation", "kb_training", "sop_context", "aleros"]
        for key in kb_keys:
            filename = self.sources.get(key)
            # Search for file in root or subdirs (simple search)
            src_path = self.root_dir / filename
            if not src_path.exists():
                # Try finding it if it's not in root
                matches = list(self.root_dir.glob(f"**/{filename}"))
                if matches:
                    src_path = matches[0]
            
            if src_path.exists():
                dst_path = self.output_dir / "knowledge_base" / src_path.name
                shutil.copy2(src_path, dst_path)
                manifest["files"].append({"type": "knowledge_base", "path": f"knowledge_base/{src_path.name}", "source": str(src_path)})
                print(f"  ✓ Copied KB file: {src_path.name}")
            else:
                print(f"  ⚠️  KB file missing: {filename}")

        # 3. Configuration
        src_conf = self.root_dir / self.sources["config_json"]
        if src_conf.exists():
            dst_conf = self.output_dir / "config" / "gpt_config.json"
            shutil.copy2(src_conf, dst_conf)
            manifest["files"].append({"type": "config", "path": "config/gpt_config.json", "source": str(src_conf)})
            print(f"  ✓ Copied config from {src_conf.name}")
        else:
             print(f"  ⚠️  Config file missing: {src_conf}")

        # 4. Actions (Code Interpreter Scripts)
        # Assuming we want to bundle some utility scripts for the agent to use in code interpreter
        # For now, let's just create a placeholder or copy relevant .py files if identified
        actions_to_copy = ["verify_gpt_configuration.py"]
        for action in actions_to_copy:
            src_action = self.root_dir / action
            if src_action.exists():
                dst_action = self.output_dir / "actions" / action
                shutil.copy2(src_action, dst_action)
                manifest["files"].append({"type": "action", "path": f"actions/{action}", "source": str(src_action)})
                print(f"  ✓ Copied action script: {action}")

        # Save manifest
        with open(self.output_dir / "consolidation_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        print(f"\n✅ Consolidation complete. Output in {self.output_dir}")

    def generate_readme(self):
        """Generates a README for the deployment package."""
        readme_content = f"""# Panelin GPT Deployment Package
Generated: {self.timestamp}

## Contents

### 1. Instructions
- `instructions.md`: The canonical system prompt for the GPT. Copy this into the "Instructions" field of the GPT Builder.

### 2. Knowledge Base (`knowledge_base/`)
Upload these files to the "Knowledge" section of the GPT Builder.
- **Level 1 (Master)**: `BMC_Base_Conocimiento_GPT-2.json`
- **Level 2 (Validation)**: `BMC_Base_Unificada_v4.json`
- **Level 3 (Dynamic)**: `panelin_truth_bmcuruguay_web_only_v2.json`
- **Support Files**: Guides, contexts, and indexes.

### 3. Configuration (`config/`)
- `gpt_config.json`: The JSON representation of the GPT's settings, capabilities, and actions.

### 4. Actions (`actions/`)
- Scripts that define logic or can be uploaded for Code Interpreter use.

## Deployment Steps
1. Go to GPT Builder.
2. Name: **Panelin - BMC Assistant Pro**
3. Copy content from `instructions.md`.
4. Upload all files from `knowledge_base/`.
5. Enable "Code Interpreter" and "Canvas".
6. Disable "Web Browsing" (unless strictly necessary, per instructions).
"""
        with open(self.output_dir / "README.md", "w") as f:
            f.write(readme_content)
        print("  ✓ Generated README.md")

if __name__ == "__main__":
    consolidator = GPTConsolidator()
    consolidator.setup_deployment_dir()
    verification_status = consolidator.run_verification()
    
    if verification_status != "FAILED":
        consolidator.consolidate_files()
        consolidator.generate_readme()
    else:
        print("❌ Aborting consolidation due to verification failure.")
