# System Architecture

Panelin is designed as a modular system where the core logic (Pricing Engine, Knowledge Base) is decoupled from the AI model interface. This allows it to run on multiple platforms (OpenAI, Claude, Gemini).

## High-Level Overview

```mermaid
graph TD
    User[User / Client] -->|Query| AI[AI Agent (OpenAI/Claude/Gemini)]
    AI -->|Function Call| Engine[Quotation Engine]
    Engine -->|Read| KB[Knowledge Base (JSON Files)]
    Engine -->|Return Data| AI
    AI -->|Natural Language Response| User
```

## Core Components

### 1. AI Layer (The Interface)
The AI model acts as the natural language interface. It understands the user's intent (e.g., "I need a quote for a 50m2 roof") and translates it into structured data calls to the Quotation Engine.

*   **Supported Models**: GPT-4 Turbo, Claude 3 Opus/Sonnet, Gemini 1.5 Pro.
*   **Mechanism**: Uses **Function Calling** (or Tool Use) to interact with the backend.

### 2. Quotation Engine (`motor_cotizacion_panelin.py`)
This is the "brain" of the logic. It does not guess; it calculates based on strict rules.

*   **Responsibilities**:
    *   Validating technical feasibility (e.g., span vs. panel thickness).
    *   Calculating quantities of panels and accessories.
    *   Retrieving prices from the Knowledge Base.
    *   Applying business rules (IVA, delivery zones).

### 3. Knowledge Base (The "Source of Truth")
A hierarchical set of JSON files that store all product data, prices, and formulas.

*   **Level 1 (Master)**: `BMC_Base_Conocimiento_GPT-2.json` (Primary source).
*   **Level 2 (Validation)**: `BMC_Base_Unificada_v4.json`.
*   **Level 3 (Dynamic)**: `panelin_truth_bmcuruguay_web_only_v2.json` (Real-time updates).

### 4. Orchestrator (`orquestador_multi_modelo.py`)
Routes requests to the appropriate model or agent based on the complexity and type of task.

## Key Files

| File | Description |
|------|-------------|
| `motor_cotizacion_panelin.py` | Core calculation logic. |
| `agente_cotizacion_panelin.py` | Wrapper for the quotation engine compatible with AI function calling. |
| `orquestador_multi_modelo.py` | Manages model selection and task routing. |
| `agente_ingestion_analisis.py` | Handles data ingestion and KB updates. |
