# Panelin Chatbot Truth Base

Repositorio central para el sistema de cotización y soporte técnico de Panelin (BMC Uruguay). Aquí se alojan la base de conocimiento principal, los calculadores deterministas, los agentes multi‑modelo y las guías operativas para desplegar y mantener el asistente.

## Visión general
- **Base de conocimiento** estructurada por niveles con precios, fórmulas y reglas de negocio.
- **Calculadores deterministas** para cotizaciones y validaciones de autoportancia.
- **Agentes y flujos** de ingestión, orquestación y entrenamiento.
- **Herramientas de backend** y utilidades para persistencia, reporting y despliegue.

## Estructura principal
- `panelin/` y `panelin_core/`: calculadores de cotización y utilidades comunes.
- `panelin_backend/`: servicios backend y persistencia.
- `GPT_Panelin_copilotedit/` y `panelin_hybrid_agent/`: herramientas y agentes GPT.
- `kb_training_system/` y `training_data/`: entrenamiento y optimización de la KB.
- `docs/`: guías de configuración, seguridad y despliegue.
- Archivos `.json` en la raíz: catálogos y reglas de la base de conocimiento (protegidos por CODEOWNERS).

## Inicio rápido
1. **Requisitos**: Python 3.10+, `pip`, y (opcional) Node.js para utilidades complementarias.
2. **Instalación**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Recomendado para entorno de desarrollo
   ```
3. **Configurar entorno**:
   - Copia `.env.example` a `.env`.
   - Completa las credenciales necesarias (OpenAI, MongoDB, Google Sheets, etc.). Consulta `docs/CONFIGURATION.md` para detalles.
4. **Pruebas**:
   ```bash
   python3 -m pytest tests/ -v
   ```

## Jerarquía de la base de conocimiento
Nivel 1 es la fuente maestra y siempre tiene prioridad:
1. **Level 1 - Master**: `BMC_Base_Conocimiento_GPT-2.json`, `accessories_catalog.json`, `bom_rules.json`
2. **Level 2 - Validación**: archivo unificado de referencia (`BMC_Base_Unificada_v4.json` o `BMC_Base_Conocimiento_Unified_v6.json`)
3. **Level 3 - Dinámico**: `panelin_truth_bmcuruguay_web_only_v2.json`
4. **Level 4 - Soporte**: documentación de referencia y archivos auxiliares

## Documentación clave
- [`PANELIN_MASTER_INDEX.md`](PANELIN_MASTER_INDEX.md) — índice maestro con las guías críticas.
- [`PANELIN_KNOWLEDGE_BASE_GUIDE.md`](PANELIN_KNOWLEDGE_BASE_GUIDE.md) — estructura y reglas de la KB.
- [`PANELIN_SETUP_COMPLETE.md`](PANELIN_SETUP_COMPLETE.md) — pasos completos de configuración del asistente.
- [`QUICK_START_CONFIG.md`](QUICK_START_CONFIG.md) — configuración rápida de entorno y datos.
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) — detalle de variables de entorno.
- [`SECURITY.md`](SECURITY.md) — políticas de seguridad y manejo de credenciales.

## GitHub Copilot Setup

This repository is configured for [GitHub Copilot coding agent](https://docs.github.com/en/copilot/tutorials/coding-agent):
- **Repository instructions**: `.github/copilot-instructions.md` - Comprehensive coding guidelines
- **Path-specific instructions**: `.github/instructions/` - Language and file-type specific guidance
  - `python.instructions.md` - Python coding standards (Decimal for financials, type hints, testing)
  - `json.instructions.md` - JSON file guidelines (knowledge base hierarchy, pricing data)
  - `test.instructions.md` - Testing patterns and pytest conventions
- **Custom agents**: `.github/agents/` - Specialized agents for specific tasks
  - `readme-specialist.md` - Documentation and README improvements

See [`.github/COPILOT_SETUP.md`](.github/COPILOT_SETUP.md) for details on the Copilot configuration.

## Contribuciones
- Los cambios en archivos protegidos (por ejemplo, `*.json`, `/config/`, `/panelin_core/`, `/gpt_configs/`, `.github/`) requieren revisión según `CODEOWNERS`.
- Mantén el uso de `Decimal` para cálculos financieros y respeta la jerarquía de la KB en toda la documentación.
- Preferir PRs pequeños y bien descritos; incluye enlaces a las guías relevantes cuando añadas nueva documentación.
- **GitHub Copilot**: Si usas Copilot, las instrucciones en `.github/` te ayudarán a seguir los estándares del repositorio automáticamente.
