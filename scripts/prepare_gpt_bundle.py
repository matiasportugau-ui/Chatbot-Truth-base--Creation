import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_V2_DIR = PROJECT_ROOT / "Copia de panelin_agent_v2"
BUNDLE_DIR = PROJECT_ROOT / "deployment_bundle"
KNOWLEDGE_DIR = BUNDLE_DIR / "knowledge"


def log(msg):
    print(f"[prepare_gpt_bundle] {msg}")


def run_tests():
    log("Running tests in Copia de panelin_agent_v2...")
    try:
        # Use python -m pytest to ensure path is correct
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/"],
            cwd=AGENT_V2_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        log("Tests passed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        log("CRITICAL: Tests failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def generate_openapi_spec():
    log("Generating OpenAPI schema...")

    # Add AGENT_V2_DIR to sys.path so we can import api
    sys.path.insert(0, str(AGENT_V2_DIR))

    try:
        from api import app

        schema = app.openapi()

        openapi_path = BUNDLE_DIR / "openapi.json"
        with open(openapi_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        log(f"OpenAPI spec generated at {openapi_path}")
        return True
    except Exception as e:
        log(f"CRITICAL: Failed to generate OpenAPI spec: {e}")
        import traceback

        traceback.print_exc()
        return False


def prepare_bundle():
    log("Preparing deployment bundle...")

    # 1. Copy Instructions
    source_instructions = (
        PROJECT_ROOT
        / "Panelin_GPT"
        / "02_INSTRUCTIONS"
        / "SYSTEM_INSTRUCTIONS_CANONICAL.md"
    )
    if source_instructions.exists():
        shutil.copy(source_instructions, BUNDLE_DIR / "instructions.md")
        log("Copied instructions.md")
    else:
        log("WARNING: SYSTEM_INSTRUCTIONS_CANONICAL.md not found!")

    # 2. Copy Knowledge Base files
    kb_files = [
        PROJECT_ROOT
        / "Panelin_GPT"
        / "03_KNOWLEDGE_BASE"
        / "panelin_truth_bmcuruguay.json",
        PROJECT_ROOT / "Panelin_GPT" / "03_KNOWLEDGE_BASE" / "product_catalog.json",
        PROJECT_ROOT / "Panelin_GPT" / "03_KNOWLEDGE_BASE" / "LEDGER_CHECKPOINT.md",
    ]

    for kb_file in kb_files:
        if kb_file.exists():
            shutil.copy(kb_file, KNOWLEDGE_DIR / kb_file.name)
            log(f"Copied {kb_file.name} to knowledge/")
        else:
            log(f"WARNING: Knowledge file {kb_file.name} not found!")

    # 3. Add a README with setup instructions
    readme_content = """# Panelin GPT Deployment Bundle

Este bundle contiene los archivos necesarios para configurar el Custom GPT en ChatGPT.

## Archivos:
- `openapi.json`: Pegar en la sección **Actions** del GPT Builder.
- `instructions.md`: Pegar en la sección **Instructions**.
- `knowledge/`: Subir estos archivos a la sección **Knowledge**.

## Configuración de Action:
1. Crear una nueva Action.
2. Importar el contenido de `openapi.json`.
3. Configurar la URL del servidor (donde despliegues `api.py`).
4. En **Authentication**, seleccionar 'API Key' si has configurado seguridad en tu servidor.

## Verificación:
Este bundle fue generado automáticamente después de pasar exitosamente todos los tests de cálculo.
"""
    with open(BUNDLE_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log("Generated bundle README.md")


def main():
    log("Starting GPT Setup Procedure...")

    # 1. Run tests
    if not run_tests():
        sys.exit(1)

    # 2. Clean and create bundle directory
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir()
    KNOWLEDGE_DIR.mkdir()

    # 3. Generate schema
    if not generate_openapi_spec():
        sys.exit(1)

    # 4. Finalize bundle
    prepare_bundle()

    log("SUCCESS: GPT Setup Bundle is ready in 'deployment_bundle/' directory.")


if __name__ == "__main__":
    main()
