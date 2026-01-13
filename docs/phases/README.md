# Phase Documentation

This directory contains detailed documentation for each phase of the Safety-by-Design Entrainer Selection Framework.

## Overview

The framework implements a five-phase pipeline for identifying optimal entrainers that balance thermodynamic efficiency with inherent safety.

## Phase Documents

| Phase | Document | Description |
|-------|----------|-------------|
| I | [PHASE1_DOMAIN_MAPPING.md](PHASE1_DOMAIN_MAPPING.md) | Chemical space mapping and cluster definition |
| II | [PHASE2_MULTI_VECTOR_SELECTION.md](PHASE2_MULTI_VECTOR_SELECTION.md) | Three-engine candidate selection with consensus |
| III | [PHASE3_GRAPH_TRAVERSAL.md](PHASE3_GRAPH_TRAVERSAL.md) | Similarity-based molecular expansion |
| IV | [PHASE4_BAYESIAN_OPTIMIZATION.md](PHASE4_BAYESIAN_OPTIMIZATION.md) | Multi-objective optimization with qEHVI |
| V | [PHASE5_SIMULATION_VALIDATION.md](PHASE5_SIMULATION_VALIDATION.md) | DWSIM process simulation and final ranking |

## Pipeline Flow

```
Phase I          Phase II         Phase III        Phase IV         Phase V
┌─────────┐     ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ Domain  │────▶│ Multi-  │─────▶│ Graph   │─────▶│  MOBO   │─────▶│ DWSIM   │
│ Mapping │     │ Vector  │      │Traversal│      │         │      │Simulation│
│100K→500 │     │ 500→150 │      │150→300  │      │300→25   │      │ 25→10   │
└─────────┘     └─────────┘      └─────────┘      └─────────┘      └─────────┘
```

## Key Outputs by Phase

| Phase | Primary Output | Format |
|-------|----------------|--------|
| I | Cluster centroids | Parquet + Neo4j |
| II | Scored candidates | JSON |
| III | Expanded candidate set | JSON + Neo4j edges |
| IV | Pareto frontier | JSON + PyTorch model |
| V | Final rankings | JSON + CSV reports |

## Research Hypotheses

| ID | Hypothesis | Validation Phase |
|----|------------|------------------|
| H1 | Pareto frontier has convex structure with knee points | Phase IV |
| H2 | qEHVI achieves 95% hypervolume with 30% budget | Phase IV |
| H3 | Consensus scoring reduces uncertainty by ≥25% | Phase II |

## Getting Started

1. Start with Phase I to understand the domain mapping approach
2. Review Phase II for the multi-engine selection strategy
3. Phase III explains the graph-based expansion
4. Phase IV covers the core optimization methodology
5. Phase V details the final validation process

## Related Documentation

- [TECH_STACK.md](../TECH_STACK.md) - Technology dependencies
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [Backlog Files](../../backlog/) - Implementation task tracking

