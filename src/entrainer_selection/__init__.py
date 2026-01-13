"""
Entrainer Selection Framework
=============================

A Safety-by-Design Framework for Ethanol-Water Separation Entrainer Selection.

This package implements a multi-phase computational chemistry research pipeline:
- Phase I: Domain Mapping & Definition (PubChem, SMARTS patterns)
- Phase II-A: Graph-RAG Engine (Neo4j, ChromaDB, Gemini)
- Phase II-B: TRIZ Multi-Agent System
- Phase II-C: Cheminformatics Clustering (RDKit)
- Phase III: Graph Traversal & Expansion
- Phase IV: Multi-Objective Bayesian Optimization (BoTorch)
- Phase V: Process Simulation Validation (DWSIM)

Usage:
    from entrainer_selection import Settings, get_settings
    from entrainer_selection.core import Neo4jConnection, ChromaDBConnection
"""

__version__ = "0.1.0"
__author__ = "Research Team"

from entrainer_selection.core.config import Settings, get_settings

__all__ = [
    "__version__",
    "Settings",
    "get_settings",
]

