import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    api_dir = repo_root / "Copia de panelin_agent_v2"
    out_path = repo_root / "deployment_bundle" / "openapi.json"

    # Ensure we import the API from the runtime folder (contains `api.py`)
    sys.path.insert(0, str(api_dir))

    from api import app  # noqa: E402

    schema = app.openapi()
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote OpenAPI schema to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

