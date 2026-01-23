# Security and Data Handling

## API keys and secrets
- Store API keys in `.env` or environment variables.
- Do not commit `.env` or secret files to version control.
- Rotate keys if accidental exposure occurs.

## Sensitive files
Some KB assets contain internal cost or margin data. These must not be uploaded
to public GPTs or shared externally.

Examples:
- `BROMYROS_Base_Costos_Precios_2026.json`

## Data sources and privacy
- Social media ingestion may include sensitive user data.
- Review and anonymize data where required.
- Use PII masking guardrails when running agents.

## Operational safeguards
- Keep Level 1 KB files restricted to trusted operators.
- Maintain backups before running evolution or bulk updates.
- Review conflict reports before applying changes.

## References
- GUIA_BASE_CONOCIMIENTO_COSTOS.md
- PANELIN_FULL_CONFIGURATION.md
