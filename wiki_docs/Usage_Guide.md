# Usage Guide

## Interacting with Panelin

Panelin is designed to guide the user through a consultation or quotation process.

### The Quotation Process
Panelin follows a 5-phase process:

1.  **Identification**: Determines product, thickness, and quantity.
    *   *Crucial*: It will ask for the "Luz" (span/distance between supports) if not provided.
2.  **Validation**: Checks if the chosen panel supports the span (Autoportancia).
3.  **Retrieval**: Fetches prices from the Knowledge Base.
4.  **Calculation**: Computes quantities of panels, screws, sealants, etc., using standard formulas.
    *   *Energy Savings*: It also calculates potential energy savings (USD/year) for thermal insulation.
5.  **Presentation**: Displays the detailed quote with IVA (22%) and technical recommendations.

### Special Commands (SOP)

The agent recognizes specific commands for advanced operations:

*   `/estado`: Returns a summary of the current context and risk assessment.
*   `/checkpoint`: Saves the current conversation state.
*   `/consolidar`: Exports the full context and knowledge gathered so far.
*   `/evaluar_ventas`: Starts a roleplay mode to evaluate sales staff.
*   `/entrenar`: Starts a training session based on best practices.

## Generating PDFs

Users can request a PDF version of the quote.
*   **Trigger**: "Generame un PDF de esta cotización".
*   **Mechanism**: The agent uses the **Code Interpreter** to run a Python script using `reportlab` to generate the file.

## Example Conversation

> **User**: Hola, necesito cotizar un techo de 50m2 con Isodec 100mm.
>
> **Panelin**: ¡Hola! Soy Panelin. Para darte la mejor opción, ¿qué distancia hay entre los apoyos (vigas) de tu techo?
>
> **User**: Son 4 metros.
>
> **Panelin**: Perfecto. Para 4m de luz, el Isodec de 100mm funciona bien (soporta hasta 5.5m).
> Aquí tienes la cotización detallada...
