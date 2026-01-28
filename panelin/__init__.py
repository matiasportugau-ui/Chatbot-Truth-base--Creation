"""
Panelin package
===============

This package contains the deterministic building blocks for the quotation system.

Design principles:
- The LLM orchestrates (NLU + routing) but NEVER performs arithmetic.
- All financial math is executed deterministically in Python (Decimal).
"""

