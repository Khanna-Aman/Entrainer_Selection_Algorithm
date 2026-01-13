"""
Phase Modules
=============

Each phase is implemented as a separate subpackage with its own:
- Runner (main execution logic)
- Models (phase-specific data models)
- Utils (phase-specific utilities)

Phases:
- phase_1: Domain Mapping & Definition
- phase_2a: Graph-RAG Engine
- phase_2b: TRIZ Multi-Agent System
- phase_2c: Cheminformatics Clustering
- phase_3: Graph Traversal & Expansion
- phase_4: Bayesian Optimization
- phase_5: Process Simulation
"""

from typing import List

PHASE_ORDER: List[str] = [
    "phase_1",
    "phase_2a",
    "phase_2b", 
    "phase_2c",
    "phase_3",
    "phase_4",
    "phase_5",
]

__all__ = ["PHASE_ORDER"]

