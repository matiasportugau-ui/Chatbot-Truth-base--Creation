"""
AI Architect Agent for Multi-Channel Chatbot Deployment

A functionalist, cost-effective architecture definition system for deploying
chatbots to WhatsApp, Facebook Messenger, Instagram, and Mercado Libre.

Optimized for Uruguay-based e-commerce with focus on:
- Minimal infrastructure costs ($25-75/month target)
- Maximum functionality per dollar spent
- Production reliability at scale (1,000-2,000 conversations/month)
"""

from .architect_agent import AIArchitectAgent
from .models.architecture import Architecture, ArchitectureConfig
from .engines.cost_optimizer import CostOptimizer
from .engines.architecture_generator import ArchitectureGenerator

__version__ = "1.0.0"
__author__ = "Panelin AI Team"

__all__ = [
    "AIArchitectAgent",
    "Architecture",
    "ArchitectureConfig",
    "CostOptimizer",
    "ArchitectureGenerator",
]
