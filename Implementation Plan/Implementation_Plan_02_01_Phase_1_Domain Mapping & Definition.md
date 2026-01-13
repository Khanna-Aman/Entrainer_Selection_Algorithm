Implementation_Plan_02_01_Phase_1_Domain Mapping & Definition.md


# 1. Executive Summary of Phase I

**Phase Name:** Domain Mapping & Definition ("The Geological Survey")
**Primary Objective:** Reduce the potential molecular search space from >100,000 compounds to approximately **500 mechanism-informed clusters** without engaging in computationally expensive brute-force simulation.

This phase functions as the foundational "Geological Survey" within the "Oil Exploration" metaphor. By leveraging established separation science literature (e.g., *Perry's Handbook*, *Seader et al.*) and utilizing the PubChem PUG REST API, we will construct a "prior knowledge map." This map identifies "molecular hot spots"—families of chemicals (Glycols, Amides, Sulfoxides) known to break the Ethanol-Water azeotrope via specific mechanisms (Hydrogen Bonding, Polarity Shift, Salting Out). The phase concludes with the establishment of a verified GitHub repository, benchmark control compounds, and a validated chemical ontology.

---

# 2. Alignment with Bedrock

This implementation plan strictly adheres to the principles outlined in the **Research Proposal**:

* **The "Oil Exploration" Model:** This phase executes the **"Geological Survey"** step defined in the proposal's overall approach, prioritizing directional accuracy over precision drilling at this stage.
* **Computer-Aided Molecular Design (CAMD):** We are initiating the "Inverse Design" framework by defining the *properties* (mechanisms) of desired solvents first, rather than screening random molecules.
* **Green Chemistry & Safety:** By explicitly including **Benzene** as a "Negative Control (Safety Failure)" and integrating safety concerns (e.g., reproductive toxicity of glycol ethers) into the cluster definitions, we establish the "Safety-by-Design" constraints immediately.
* **Efficiency:** The use of **SMARTS patterns** and **API metadata scoping** (instead of bulk downloads) aligns with the requirement to be computationally efficient before deploying the expensive MOBO/qEHVI loops in later phases.

---

# 3. High-Level Approach

The strategic methodology for Phase I follows a **Mechanism-Informed Clustering** logic. We do not group molecules simply by visual similarity; we group them by their *functional capacity* to perform the separation.

### Process Logic

1. **Literature Grounding:** Extract proven separation mechanisms (H-Bonding, Polarity Shift, Salting Out) from authoritative texts.
2. **Ontology Construction:** Define clusters using a structured nomenclature: `[Mechanism]_[Functional Class]_[Size Range]`.
3. **Digital Scoping:** Translate chemical families into machine-readable **SMARTS patterns** and query the PubChem API to quantify the available search space.
4. **Baseline Establishment:** Define positive and negative control compounds to validate future AI predictions.

### Core Principles

* **No "Empty Sets":** Verify that theoretical clusters actually contain purchasable molecules using API scoping.
* **Benchmark-Driven:** Every future algorithm will be measured against the specific "Control Group" established here (Ethylene Glycol vs. Benzene).
* **Reproducibility:** All scoping is code-based (Python/RDKit), ensuring the "Geological Survey" can be re-run if database contents change.

---

# 4. Implementation Plan

This section details the execution of the four sub-phases defined in the Phase File.

### Step-by-Step Execution

#### Sub-Phase I.1: Literature-Based Hot Spot Identification

* **Action:** Synthesize separation mechanisms from *Perry's Chemical Engineers' Handbook* (Section 13) and *Seader, Henley, Roper*.
* **Action:** Create the "Entrainer Family Matrix" categorizing known agents (Glycols, Glycol Ethers, Amides, Ionic Liquids).
* **Constraint:** Mark active research areas (Deep Eutectic Solvents, Ionic Liquids) as `[NEEDS VERIFICATION]` regarding data availability (2020–2024 literature).

#### Sub-Phase I.2: Database Scoping & Initial Filtering

* **Action:** Develop `pubchem_scoping.py` to interface with the PubChem PUG REST API.
* **Action:** Translate Entrainer Families into **SMARTS patterns** (e.g., Glycols: `[OX2H][CX4][CX4][OX2H]`).
* **Action:** Execute scoping queries to estimate compound counts per family without performing bulk downloads.
* **Risk Management:** Adhere to API rate limits (approx. 5 requests/second) and implement caching.

#### Sub-Phase I.3: Cluster Definition via Chemical Ontology

* **Action:** Develop `cluster_definition.py` to generate the target list of ~500 clusters.
* **Action:** Apply the clustering nomenclature:
* **Mechanism:** HB (Hydrogen Bonding), SO (Salting Out), PS (Polarity Shift).
* **Size:** S (MW 50-150), M (MW 150-300), L (MW 300-500).


* **Action:** Assign "Priority Scores" to clusters based on literature support (e.g., `HB_GLYCOL_S` = 1.5 priority; `EXP_IL_IMIDAZOLIUM` = 0.8 priority).

#### Sub-Phase I.4: Documentation & Baseline Establishment

* **Action:** Initialize the GitHub repository structure (`ethanol-water-separation/`).
* **Action:** Implement `benchmark_compounds.py` to fetch and store properties for the Control Group:
* **Positive Benchmark:** Ethylene Glycol (CAS: 107-21-1).
* **Negative Safety Control:** Benzene (CAS: 71-43-2).
* **Alternative Benchmarks:** NMP, DMSO.


* **Action:** Validate SMARTS patterns using RDKit (`03_cluster_validation.ipynb`) against known molecules to ensure query accuracy.

### Key Deliverables

| Category | Deliverable Item | Format/Location |
| --- | --- | --- |
| **Code** | `pubchem_scoping.py` | Python Script |
| **Code** | `cluster_definition.py` | Python Script |
| **Code** | `benchmark_compounds.py` | Python Script |
| **Data** | **Cluster Definitions** (~500 defined hot spots) | JSON / Markdown |
| **Data** | **Benchmark Compounds Dataset** (Properties of controls) | JSON |
| **Docs** | Literature Review & Entrainer Family Matrix | Markdown |
| **Docs** | Verification Report (SMARTS validation & RDKit tests) | Jupyter Notebook |

---

# 5. Continuity Check

**How this builds upon the Previous Phase:**

* *N/A - This is the initial phase.*

**How this prepares for the Next Phase (Phase II):**

* **Input for Phase II:** The ~500 **"Cluster Definitions"** produced here become the direct inputs for the "Multi-Vector Initial Selection" in Phase II.
* **Targeting:** The "Molecular Hot Spots" identified prevent the Phase II "Deep Research" (Graph-RAG) and "Cheminformatics" engines from scanning the entire chemical universe, focusing them instead on high-probability vectors.
* **Validation Standards:** The **Benchmark Compounds** established here (Ethylene Glycol, Benzene) provide the comparative baseline required for the "TRIZ-Powered Consultation Module" in Phase II to assess novelty and utility.

---
