Implementation_Plan_02_02_B_Phase 2-B_Multi-Vector Initial Selection - Engine B - TRIZ-Powered Consultation Module.md

# High-Level Approach and Implementation Plan - Phase II-B

## Multi-Vector Initial Selection - Engine B (TRIZ-Powered Consultation)

---

### 1. Executive Summary of Phase II-B

**Phase Name:** Engine B – TRIZ-Powered Consultation Module
**Primary Objective:** Deploy a **Multi-Agent System** grounded in the Theory of Inventive Problem Solving (TRIZ) to generate 25–50 high-potential molecular candidates based on **functional innovation** and **first principles**, rather than purely data-driven literature search.

While Phase II-A ("Deep Research") focused on what *exists* in the literature, Phase II-B focuses on what *should* exist based on engineering logic. This phase utilizes a "structured formalization of expert intuition." By deploying six specialized AI agents—ranging from Contradiction Analysis to Bio-isosterism—this engine treats the Ethanol-Water separation challenge as an inventive problem. It aims to identify novel candidates and safer analogs that traditional keyword searches might miss, specifically looking for "Hot Lead" overlaps with Engine A.

---

### 2. Alignment with Bedrock

This phase executes the "Creative/Lateral" vector of the research methodology, ensuring the pipeline is not limited by existing biases in published data.

* **Designing Safer Chemicals (Green Chemistry Principle 4):** Agent 6 (Bio-isosterism) and Agent 2 (Ideality) directly address the "Inverse Design" framework. Instead of asking "Is Benzene safe?", they ask "What structural analog provides Benzene's separation performance without its toxicity?"
* **The "No-Free-Lunch" Theorem:** This engine explicitly operationalizes the trade-offs mentioned in the proposal. Agent 1 (Contradiction Analysis) formally maps the "Efficiency vs. Safety" trade-off (Technical Contradiction) and proposes resolution strategies (e.g., Separation Principles) before the mathematical optimization in Phase IV.
* **Computer-Aided Molecular Design (CAMD):** Agent 5 (Inverse Design) implements the "Inverse Problem" approach defined in the proposal: defining properties (Safety > X, Efficiency > Y) first, then seeking the molecular structure.

---

### 3. High-Level Approach

The methodology uses a **Modular Multi-Agent Architecture** where Large Language Models (LLMs) act as reasoning engines constrained by specific heuristic frameworks.

#### The "Structured Intuition" Logic

1. **Domain Mapping:** First, we translate abstract TRIZ concepts (e.g., "segmentation," "separation in time") into concrete chemical domains (e.g., "functional group modularity," "temperature-switchable solvents").
2. **Parallel Agent Execution:** Six agents run simultaneously, each viewing the problem through a different lens:
* *The Conflict Solver (Agent 1):* Resolves contradictions.
* *The Futurist (Agent 2):* Looks at system evolution and sustainability trends.
* *The Modeler (Agent 3):* Analyzes substance-field interactions (Su-Field).
* *The Physicist (Agent 4):* Derives requirements from thermodynamic laws.
* *The Architect (Agent 5):* Searches based on target property profiles.
* *The Chemist (Agent 6):* Finds safer structural analogs (Bio-isosterism).


3. **Synthesis & Overlap:** An Orchestrator Agent consolidates results, ranks confidence, and—crucially—flags any molecules that were *also* found by Engine A (Phase II-A). These overlaps represent the highest-probability candidates.

---

### 4. Implementation Plan

#### Step-by-Step Execution

**Step 1: TRIZ Domain Translation (The Intellectual Core)**

* **Action:** Implement `src/triz/domain_mapping.py`.
* **Detail:** Define the specific "Technical Contradictions" for Ethanol-Water separation (e.g., Selectivity vs. Energy, Polarity vs. Separation). Map the "40 Inventive Principles" to molecular equivalents (e.g., *Principle 1: Segmentation*  Modular functional groups).
* **Output:** Validated mapping dictionaries required for Agent logic.

**Step 2: Agent Development & Testing (The Specialists)**

* **Action:** Develop the six agent classes in `src/triz/agents/`.
* **Agent 1 (Contradiction):** Implement logic to map separation issues to the Contradiction Matrix and query the LLM for molecular features that resolve them.
* **Agent 2 (Evolution):** Implement "9 Windows" and "Ideality" prompts to identify future-proof, sustainable solvent classes (e.g., bio-derived esters).
* **Agent 3 (Su-Field):** code the "Smart Little People" and "Standard Solutions" heuristics to model molecular interactions anthropomorphically.
* **Agent 4 (First Principles):** Implement derivation logic based on Activity Coefficients (UNIFAC/NRTL) to define "must-have" structural features.
* **Agent 5 (Inverse Design):** Set up property targeting (BP > 78°C, H-Bond Acceptors > 2) and enable the LLM to propose structures meeting these criteria.
* **Agent 6 (Bio-isosterism):** Implement "Scaffold Hopping" logic to find safer replacements for effective but toxic templates (e.g., replacing Benzene rings with Pyridine or bio-isosteres).



**Step 3: Orchestration & Synthesis**

* **Action:** Develop `src/triz/engine_b_orchestrator.py`.
* **Logic:**
1. Load `engine_a_results.json` (from Phase II-A).
2. Trigger all 6 agents.
3. Aggregating outputs via a "Synthesis Agent" that ranks molecules based on multi-agent consensus.
4. **Crucial Step:** Check for `engine_a_overlap`. If a molecule appears in both the Literature Search (Engine A) and the Innovation Search (Engine B), mark it as **Priority 1**.



**Step 4: Validation & Export**

* **Action:** Validate all LLM-proposed SMILES strings using RDKit to ensure chemical validity.
* **Action:** Filter out "Hallucinations" (invalid SMILES).
* **Action:** Export final list to `data/engine_b_results.json`.

#### Key Deliverables

| Category | Deliverable Item | Description |
| --- | --- | --- |
| **Code** | `domain_mapping.py` | Translation of TRIZ concepts to Chemistry. |
| **Code** | `agents/` Package | The 6 specialized Python Agent modules. |
| **Code** | `engine_b_orchestrator.py` | Main execution pipeline. |
| **Notebooks** | `10_triz_domain_mapping.ipynb` | Interactive exploration of TRIZ mappings. |
| **Notebooks** | `17_engine_b_integration.ipynb` | Full pipeline execution and testing. |
| **Data** | `engine_b_results.json` | Final list of 25-50 synthesized molecules + Insights. |

---

### 5. Continuity Check

**How this builds upon the Previous Phase (Phase II-A):**

* **Input Integration:** The orchestrator explicitly loads `engine_a_results.json`.
* **Overlap Detection:** The primary validation metric for Engine B is its ability to independently corroborate findings from Engine A (Literature) or finding "Blue Ocean" candidates that Engine A missed.
* **Constraint Checking:** The safety baselines established in Phase I (Benzene) are used as "Templates for Improvement" in Agent 6 (Bio-isosterism), ensuring we are actively designing *away* from known hazards.

**How this prepares for the Next Phase (Phase II-C & III):**

* **Input for Cheminformatics:** The molecules generated here (specifically the potentially novel "Inverse Design" candidates) will be passed to **Engine C** for rigorous descriptor calculation and diversity clustering to ensure the final seed list is mathematically diverse.
* **Seeds for Deep Traversal:** The "Scaffold Hops" identified here become excellent starting nodes for the Graph Traversal in Phase III, allowing the system to explore the "neighborhood" of these novel structures.