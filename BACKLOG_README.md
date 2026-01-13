# 📋 Entrainer Selection Framework - Development Backlog

## Overview

This document provides a comprehensive overview of the development backlog for the Safety-by-Design Framework for Ethanol-Water Separation Entrainer Selection.

---

## 🎯 RECOMMENDED EXECUTION SEQUENCE

### Primary Path (Follow Phase Order):

```
1. INF-001 to INF-008  (Environment Setup + Data Schemas)
        ↓
2. P1-xxx: Phase I (Domain Mapping)
        ↓
3. P2A-xxx: Phase II-A (Graph-RAG)
        ↓
4. P2B-xxx: Phase II-B (TRIZ Agents)
        ↓
5. P2C-xxx: Phase II-C (Cheminformatics)
        ↓
6. P3-xxx: Phase III (Graph Traversal)
        ↓
7. P4-xxx: Phase IV (Bayesian Optimization)
        ↓
8. P5-xxx: Phase V (DWSIM Simulation)  ←── DWSIM risk contained here
```

### Risk Clarification (Updated from Consultation #8)

| Risk | Scope | Impact on Phases 1-4 | Mitigation |
|------|-------|----------------------|------------|
| DWSIM COM fails | Phase 5 ONLY | ❌ None | Plan-B fallbacks |
| Oracle slow (>1s) | Phase 4 | ❌ None on 1-3 | Caching strategy |
| LLM hallucinations | Phase 2A/2B | ❌ Contained | API verification |

**Key Insight:** DWSIM is for VALIDATION only. Phases 1-4 produce a ranked candidate list independently. If DWSIM automation fails, manual validation or alternative simulators can be used.

### Optional Risk Spikes (Can Be Deferred)

These were recommended by Consultation #8 but can be deferred to Phase 5:

| Task | Original Priority | Updated Priority | Rationale |
|------|-------------------|------------------|-----------|
| INF-009: DWSIM Spike | 🔴 CRITICAL | 🟢 Deferred to P5 | Risk contained to Phase 5 |
| INF-010: Oracle Benchmark | 🔴 Critical | 🟡 Before Phase 4 | Only needed before MOBO |
| INF-012: Simulation Watchdog | 🟡 High | 🟢 Deferred to P5 | Only needed for DWSIM |

---

## 🚨 Critical Fixes (Must Implement)

Based on the technical review in `Implementation Plan/Feedback to Improve.md` AND **Consultations #7 and #8**, the following critical fixes **MUST** be implemented:

### 1. Phase V Simulation Engine (CRITICAL)
- **Issue**: FUG shortcut method assumes constant relative volatility
- **Impact**: Invalid for extractive distillation where entrainer changes α along column
- **Fix**: Implement DWSIM COM automation to solve full MESH equations
- **Status**: ⬜ Not Started
- **Backlog**: `backlog/BACKLOG_05_Phase_5_Simulation.md`

### 2. Tanimoto Threshold (HIGH)
- **Issue**: 0.5 threshold returns functionally distinct molecules
- **Impact**: Graph traversal returns noise instead of similar candidates
- **Fix**: Tighten to 0.75-0.85 for similarity, keep 0.5 for scaffold hopping only
- **Status**: ⬜ Not Started
- **Backlog**: `backlog/BACKLOG_02C_Phase_2C_Cheminformatics.md`

### 3. Safety Data Verification (HIGH)
- **Issue**: LLMs can hallucinate GHS categories
- **Impact**: Safety barrier function fails if data is wrong
- **Fix**: Query PubChem PUG REST API first, LLM as fallback only
- **Status**: ⬜ Not Started
- **Backlog**: `backlog/BACKLOG_02A_Phase_2A_GraphRAG.md`

### 4. Ternary Azeotrope Check (HIGH)
- **Issue**: Solvent may form ternary azeotrope at finite concentrations
- **Impact**: Good selectivity at infinite dilution but fails in practice
- **Fix**: Add ternary azeotrope check in Phase IV Oracle, not just Phase V
- **Status**: ⬜ Not Started
- **Backlog**: `backlog/BACKLOG_04_Phase_4_Optimization.md`

## 📁 Backlog Structure

```
backlog/
├── BACKLOG_00_Infrastructure.md      # Core setup, config, databases
├── BACKLOG_01_Phase_1_Domain.md      # Phase I: Domain Mapping
├── BACKLOG_02A_Phase_2A_GraphRAG.md  # Phase II-A: Graph-RAG Engine
├── BACKLOG_02B_Phase_2B_TRIZ.md      # Phase II-B: TRIZ Multi-Agent
├── BACKLOG_02C_Phase_2C_Cheminformatics.md  # Phase II-C: Clustering
├── BACKLOG_03_Phase_3_Traversal.md   # Phase III: Graph Traversal
├── BACKLOG_04_Phase_4_Optimization.md # Phase IV: Bayesian Optimization
└── BACKLOG_05_Phase_5_Simulation.md  # Phase V: Process Simulation
```

## 🎯 Phase Summary

| Phase | Description | Key Deliverables | Critical Fixes |
|-------|-------------|------------------|----------------|
| **Infrastructure** | Core setup | Config, DB connections, models | - |
| **Phase I** | Domain Mapping | PubChem queries, SMARTS patterns | - |
| **Phase II-A** | Graph-RAG | Neo4j graph, ChromaDB embeddings | Safety verification |
| **Phase II-B** | TRIZ Agents | 6 specialized LLM agents | - |
| **Phase II-C** | Clustering | RDKit fingerprints, diversity | Tanimoto threshold |
| **Phase III** | Traversal | Graph expansion, similarity network | Tanimoto threshold |
| **Phase IV** | Optimization | BoTorch MOBO, Pareto frontier | Ternary azeotrope |
| **Phase V** | Simulation | DWSIM automation, validation | DWSIM (not FUG) |

## 🔄 Development Workflow

1. **Pick a task** from the relevant backlog file
2. **Update status** to "🔄 In Progress"
3. **Implement** following the implementation notes
4. **Test** using the specified test approach
5. **Update status** to "✅ Complete" with date

## 📊 Progress Tracking

### Overall Progress
- Infrastructure: ⬜ 0%
- Phase I: ⬜ 0%
- Phase II-A: ⬜ 0%
- Phase II-B: ⬜ 0%
- Phase II-C: ⬜ 0%
- Phase III: ⬜ 0%
- Phase IV: ⬜ 0%
- Phase V: ⬜ 0%

### Sprint Goals
- **Sprint 1**: Infrastructure + Phase I
- **Sprint 2**: Phase II (A, B, C)
- **Sprint 3**: Phase III + Phase IV
- **Sprint 4**: Phase V + Integration Testing

## 🔗 Related Documentation

- [Project Documentation](./Project%20Documentation/) *(Sacred - DO NOT MODIFY)*
- [Implementation Plans](./Implementation%20Plan/) *(Sacred - DO NOT MODIFY)*
- [Technical Feedback](./Implementation%20Plan/Feedback%20to%20Improve.md)
- [Infrastructure Config](./config/infra_config.yaml)
- [Science Config](./config/science_config.yaml)
- [Consultation Tools](./.tools/advanced_consultation_mcp_server/)

## 📝 Task Status Legend

- ⬜ Not Started
- 🔄 In Progress
- ⏸️ Blocked
- ✅ Complete
- ❌ Cancelled

---

## 📋 Consultation #8 Recommendations Summary

**Date:** 2026-01-11 | **Scorecard:** Docs 9/10, Plan 6/10, Backlog 9/10

### High Priority Items (Incorporated)

| # | Recommendation | Location | Status |
|---|----------------|----------|--------|
| 1 | DWSIM Feasibility Spike | INF-009 | ⬜ Added |
| 2 | Oracle Latency Benchmark | INF-010 | ⬜ Added |
| 3 | Data Contracts (Pydantic Schemas) | INF-008 | ⬜ Added |
| 4 | Name-to-SMILES Resolver | INF-011, P2B-009 | ⬜ Added |
| 5 | Simulation Watchdog | INF-012 | ⬜ Added |
| 6 | Solver Strategy Pattern | P5-007 | ⬜ Added |
| 7 | Reorder Execution Sequence | This README | ✅ Done |

### Medium Priority Items (Incorporated)

| # | Recommendation | Location | Status |
|---|----------------|----------|--------|
| 1 | Split settings.yaml | config/infra_config.yaml, config/science_config.yaml | ✅ Done |
| 2 | Configurable Safety Mode | science_config.yaml → strict_safety_mode | ✅ Done |
| 3 | SMILES Validation Gateway | P2B-009 | ⬜ Added |
| 4 | Move MCP Server | .tools/advanced_consultation_mcp_server | ✅ Done |

### Deferred Items

| # | Recommendation | Reason |
|---|----------------|--------|
| 1 | API Rate Limit Orchestrator | Deferred per user request |
| 2 | Delete/simplify TRIZ agents | Retained - user expertise |

### Key Insights from Consultation

1. **"Windows Trap"**: Docker + DWSIM COM = incompatible. Decision required.
2. **Pre-Mortem Warning**: Likely failure modes are "Empty Set Optimization" (aggressive safety) or deployment failure.
3. **Backlog > Plan**: The Backlog is more technically mature than the Implementation Plan.

---

## ⚠️ PENDING DECISIONS

The following decisions are required before significant coding begins:

### 1. Docker vs. Windows Deployment
- **Issue**: DWSIM COM requires Windows, but proposal promises "Dockerized Virtual Lab"
- **Options**: Abandon Docker / Use DWSIM CLI / REST Service / Windows Container
- **Status**: ⏳ PENDING

### 2. Safety Mode Configuration
- **Issue**: Strict safety may filter out global optimums early
- **Current**: Configurable via `strict_safety_mode` in science_config.yaml
- **Status**: ✅ RESOLVED (configurable)

---

## 📊 Updated Task Counts

| Backlog | Original | Added | Total |
|---------|----------|-------|-------|
| Infrastructure | 7 | 5 | 12 |
| Phase I | - | - | - |
| Phase II-A | - | - | - |
| Phase II-B | 8 | 1 | 9 |
| Phase II-C | - | - | - |
| Phase III | - | - | - |
| Phase IV | - | - | - |
| Phase V | 6 | 1 | 7 |

