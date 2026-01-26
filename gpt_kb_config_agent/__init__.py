"""
GPT Knowledge Base Configuration and Evolution Agent
====================================================

Specialized agent for configuring and evolving GPT knowledge bases.
Analyzes, validates, and evolves knowledge base files for optimal GPT performance.
"""

from .kb_config_agent import GPTKnowledgeBaseAgent
from .kb_analyzer import KnowledgeBaseAnalyzer
from .kb_evolver import KnowledgeBaseEvolver
from .gpt_config_generator import GPTConfigGenerator
from .correction_agent import GPTCorrectionAgent

__all__ = [
    "GPTKnowledgeBaseAgent",
    "KnowledgeBaseAnalyzer",
    "KnowledgeBaseEvolver",
    "GPTConfigGenerator",
    "GPTCorrectionAgent",
]

__version__ = "1.0.0"
