"""
Knowledge Base Training System
==============================

Multi-level training system for chatbot knowledge base evolution using:
- Quote analysis and review
- Customer interactions
- Social media consultations and interactions

Architecture:
- Level 1: Static Grounding (Documentation & Quotes)
- Level 2: Interaction-Driven Evolution (Customer Support)
- Level 3: Proactive Social & Synthetic Ingestion
- Level 4: Autonomous Agent Feedback Loop
"""

from .kb_evaluator import KnowledgeBaseEvaluator
from .kb_leak_detector import KnowledgeBaseLeakDetector
from .training_levels import (
    Level1StaticGrounding,
    Level2InteractionEvolution,
    Level3SocialIngestion,
    Level4AutonomousFeedback
)
from .training_orchestrator import TrainingOrchestrator
from .evaluation_metrics import EvaluationMetrics

__all__ = [
    "KnowledgeBaseEvaluator",
    "KnowledgeBaseLeakDetector",
    "Level1StaticGrounding",
    "Level2InteractionEvolution",
    "Level3SocialIngestion",
    "Level4AutonomousFeedback",
    "TrainingOrchestrator",
    "EvaluationMetrics",
]

__version__ = "1.0.0"
