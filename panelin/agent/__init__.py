"""
Panelin Agent - Agente híbrido con LangGraph 1.0.

Este módulo implementa el agente principal que:
- Usa LLM para comprensión de lenguaje natural
- Usa herramientas deterministas para cálculos
- Garantiza precisión 100% en cotizaciones
"""

from panelin.agent.hybrid_agent import (
    PanelinHybridAgent,
    create_panelin_agent,
    run_quotation_workflow,
)

__all__ = [
    "PanelinHybridAgent",
    "create_panelin_agent",
    "run_quotation_workflow",
]
