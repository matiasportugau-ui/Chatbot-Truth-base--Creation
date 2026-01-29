"""
Panelin Tests - Test suite para el sistema de cotización.

Incluye:
- Golden dataset tests (50+ casos reales)
- Unit tests para funciones de cálculo
- Integration tests para el agente
- Validation tests
"""

from panelin.tests.test_quotation_calculations import (
    TestQuotationCalculations,
    TestValidation,
    TestKnowledgeBase,
    GoldenDatasetTests,
)

__all__ = [
    "TestQuotationCalculations",
    "TestValidation",
    "TestKnowledgeBase",
    "GoldenDatasetTests",
]
