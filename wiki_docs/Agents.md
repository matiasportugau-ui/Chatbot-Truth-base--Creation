# Agents

Panelin is not just a single bot; it's a suite of specialized agents working together.

## 1. Quotation Agent (`agente_cotizacion_panelin.py`)
The primary agent for interacting with customers.

*   **Role**: Sales Engineer.
*   **Capabilities**:
    *   Generates technical quotes.
    *   Answers technical questions about products.
    *   Calculates thermal insulation savings.
*   **Personality**: Professional, technical but accessible, uses Uruguayan Spanish.

## 2. Ingestion & Analysis Agent (`agente_ingestion_analisis.py`)
Responsible for keeping the Knowledge Base up to date.

*   **Role**: Data Analyst.
*   **Capabilities**:
    *   Reads raw data (CSV, PDF, scraped web data).
    *   Validates data integrity.
    *   Updates the JSON Knowledge Base files.
    *   Generates reports on data quality.

## 3. Build AI Apps Agent (`agente_build_ai_apps.py`)
A meta-agent capable of creating or configuring other AI applications.

*   **Role**: DevOps / AI Engineer.
*   **Capabilities**:
    *   Generates configuration files for new GPTs.
    *   Sets up system instructions.
    *   Manages deployment pipelines.

## 4. Training System (`kb_training_system/`)
Not a conversational agent, but a system agent that learns from past interactions.

*   **Role**: Trainer.
*   **Capabilities**:
    *   Analyzes chat logs (Instagram, WhatsApp).
    *   Identifies successful sales patterns.
    *   Updates the "Training Guide" for the Quotation Agent.

## Multi-Model Support

The agents are designed to be model-agnostic.

*   **OpenAI**: Uses the standard Assistants API or Chat Completion with Tools.
*   **Claude**: Uses the Anthropic API with Tool Use.
*   **Gemini**: Uses Google's Generative AI SDK with Function Calling.

You can switch between models by changing the configuration or using the `orquestador_multi_modelo.py`.
