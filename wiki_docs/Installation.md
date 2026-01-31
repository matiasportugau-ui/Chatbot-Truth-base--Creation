# Installation and Setup

## Prerequisites

*   **Python 3.10+**
*   **API Keys**:
    *   `OPENAI_API_KEY` (Required for main features)
    *   `ANTHROPIC_API_KEY` (Optional, for Claude)
    *   `GOOGLE_API_KEY` (Optional, for Gemini)

## Step-by-Step Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-org/panelin-project.git
    cd panelin-project
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...
    GOOGLE_API_KEY=AIza...
    ```

## Verifying Installation

To check if everything is set up correctly, run the verification script:

```bash
python verificar_configuracion.py
```

## Running the Agents

### OpenAI Agent
To run the standard OpenAI-based agent:
```bash
python ejercicio_cotizacion_panelin.py
```

### Claude Agent
To run the Claude-based agent:
```bash
python setup_claude_agent.py
```

### Gemini Agent
To run the Gemini-based agent:
```bash
python setup_gemini_agent.py
```
