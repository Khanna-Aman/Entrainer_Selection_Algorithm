**Research Proposal**.

# An Active Learning Framework for the Simultaneous Optimization of Thermodynamic Efficiency and Inherent Safety in Extractive Distillation Entrainers

---

## 1. Introduction & Problem Statement

In industrial separation processes, particularly extractive distillation (e.g., Ethanol-Water separation), the selection of entrainers has traditionally followed a sequential optimization approach: thermodynamic efficiency is maximized first, with safety considerations applied retroactively as constraints. This paradigm often leads to the selection of highly efficient but hazardous solvents, such as benzene (a known carcinogen), necessitating expensive containment and mitigation strategies.

Current methodologies often treat safety as a "check-box" compliance step rather than a primary design variable. Furthermore, traditional solvent selection based solely on infinite dilution coefficients fails to account for distillation boundaries and azeotropic behavior, as noted by Laroche & Morari. This research proposes a "Safety-by-Design" framework that treats safety and efficiency as simultaneous objectives within a Multi-Objective Bayesian Optimization (MOBO) loop.

---

## 2. Research Objectives

* To develop a **continuous Safety-Cost Penalty Function** that translates discrete GHS hazard categories into economic metrics, enabling smooth gradient-based optimization.
* To implement an **Active Learning Framework** utilizing MOBO and qEHVI to explore the chemical space efficiently, balancing computational fidelity with model uncertainty.
* To **validate thermodynamic feasibility** using the Infinitely Sharp Step (ISS) method to ensure realizable separation sequences.

### Research Hypotheses

* **H1:** The Pareto frontier between thermodynamic efficiency and inherent safety for ethanol-water entrainers exhibits a convex structure with identifiable knee points.
* **H2:** Active learning via qEHVI achieves equivalent Pareto hypervolume to exhaustive evaluation using ≤30% of total computational budget.
* **H3:** Consensus-based safety scoring reduces prediction uncertainty by ≥25% compared to single-source QSAR.

---

## 3. Methodology

### 3.1 Thermodynamic Fidelity & Feasibility

Standard infinite dilution screening is insufficient for complex azeotropic mixtures. This research will incorporate the **ISS (Infinitely Sharp Step) method** to analyze isovolatility curves. This ensures that the rectifying and stripping operating lines intersect within the feasible region, avoiding solvents that create impassable distillation boundaries.

### 3.2 Quantifying Safety for Gaussian Processes

A major challenge in optimizing for safety is the discrete nature of safety data (e.g., GHS Categories 1–5), which creates "cliffs" (zero gradients) that confuse Gaussian Process (GP) regressors.

**Innovation:** We will map discrete Inherent Safety Indices (ISI) to a continuous "Cost of Mitigation" function. This translates risk into the economic cost required to mitigate that risk (e.g., cost of specialized ventilation, containment, or PPE). The consensus safety score is subsequently passed through a barrier-shaped cost-of-mitigation function before entering the MOBO loop, ensuring that extreme or legally prohibited hazard classes are treated as effectively infeasible rather than merely costly.

### 3.3 Data Acquisition & Consensus Labeling

To address data sparsity in safety databases, a **Tri-Modular Consensus** approach will be employed:

1. **NLP-based Extraction:** Utilizing Large Language Models (e.g., Gemini/GPT) to mine textual safety data and reasoning from Safety Data Sheets (SDS).
2. **QSAR Modeling:** Deploying Quantitative Structure-Activity Relationship models for toxicity prediction where data is absent.
3. **Database Cross-Referencing:** Validation against ECHA and PubChem repositories.

**Uncertainty Quantification:** An uncertainty score will be generated. High-uncertainty molecules will be prioritized for physics-based validation to reduce noise.

### 3.4 The Active Learning Loop

The core engine will be a **Multi-Objective Bayesian Optimization (MOBO)** framework.

* **Surrogate Model:** Gaussian Processes trained on molecular descriptors (Morgan Fingerprints).
* **Acquisition Function:** q-Expected Hypervolume Improvement (qEHVI) will be used to select candidate molecules that push the Pareto frontier forward.
* **Oracle/Validation:** Selected candidates will be verified using **UNIFAC-based property estimation and Penalty Functions as the oracle**, allowing for a high-throughput active learning simulation. Safety: The consensus safety score, transformed via a barrier-shaped cost-of-mitigation function.

### Hypothesis Testing Approach


| Hypothesis | Test Phase | Validation Metric | Success Threshold |
| --- | --- | --- | --- |
| H1: Convex Pareto with knee points | Phase IV | Pareto curvature analysis | ≥1 identifiable knee |
| H2: qEHVI ≤30% budget efficiency | Phase IV | Cumulative Regret & Log-Hypervolume Difference | HV_30% ≥ 0.95 × HV_100% |
| H3: Consensus reduces uncertainty 25% | Phase II | σ_consensus vs σ_single | σ_reduction ≥ 25% |

---

## 4. Expected Outcomes & Impact

* **Pareto-Optimal Library:** A high-dimensional dataset (visualized via HiPlot) identifying the "Knee Point"—the optimal trade-off where marginal gains in safety do not disproportionately compromise energy efficiency.
* **Quantifiable Metrics:** The framework aims to demonstrate potential improvements, such as a reduction in inherent risk (ISI) by 20% with a minimal efficiency penalty (<8%).
* **Reproducibility:** The entire workflow will be encapsulated in a Dockerized Virtual Lab, allowing the methodology to be adapted for other chemical engineering challenges, such as carbon capture solvent selection.


---

## 5. Theoretical Frameworks of Chemistry & Research

To defend a PhD, we must situate this work within established scientific philosophies. This research sits at the convergence of three distinct frameworks:

### A. The Framework of "Green Chemistry" (Principles 4 & 5)

This work is a direct computational application of Paul Anastas and John Warner's 12 Principles of Green Chemistry.

* **Principle 4 (Designing Safer Chemicals):** The QSAR/GHS model directly addresses this.
* **Principle 5 (Safer Solvents and Auxiliaries):** Focus on entrainers is the practical application of this principle.

**How to use this:** In my thesis, frame "Cost of Mitigation" function not just as an economic tool, but as a quantification of Green Chemistry principles. We are converting qualitative principles into quantitative design variables.

### B. The Framework of "Computer-Aided Molecular Design" (CAMD)

We are moving from "Forward Problem" solving to "Inverse Problem" solving.

* **Forward Problem:** "Here is Benzene. Is it safe?" (Traditional).
* **Inverse Problem (My Research):** "I need a solvent with Safety > X and Efficiency > Y. What does the molecule look like?"

**The Shift:** I am hybridizing Group Contribution Methods (like UNIFAC) with Topology-Based Learning. While UNIFAC provides the thermodynamic baseline, the Topology-Based Learning (Morgan Fingerprints) captures the emergent safety and toxicity features that UNIFAC cannot predict..

### C. The Framework of "Process Systems Engineering" (PSE)

This is the engineering wrapper around the chemistry.

* **Superstructure Optimization:** We are not just picking a fluid; we are optimizing the interaction between the fluid and the process (the distillation column).
* **The "No-Free-Lunch" Theorem:** We are explicitly acknowledging that we cannot have perfect safety and perfect efficiency simultaneously. Use of Pareto Optimization is the mathematical acceptance of this trade-off.

---

## Critical Analysis, Precautions and Approach

### 1. Theoretical Frameworks & Context

This research sits at the intersection of three major frameworks. Citing these will ground the thesis in established literature:

#### The "Inverse Design" Framework (CAMD)

* **Traditional:** Pick a molecule → Test properties.
* **My Approach:** Define properties (Safety + Efficiency) → Find the molecule.
* **Context:** We are moving beyond "Group Contribution Methods" (like UNIFAC) to "Data-Driven CAMD."

#### Inherent Safety (The Kletz Paradigm)

* Trevor Kletz's principle of "Inherent Safety" argues that hazards should be eliminated, not controlled.
* **My Contribution:** Most Inherent Safety Indices (ISI) are static scores. Converting Kletz's static principles into a dynamic objective function for optimization.

#### The "No-Free-Lunch" Theorem in Optimization

* This theorem states that no optimization algorithm is best for all problems.
* **Context:** We are using MOBO because the search landscape is noisy (Safety Data) and we require multi-objective trade-offs. This justifies choice of algorithm over simple Genetic Algorithms.

### 2. Critical Analysis: The Pitfalls (and how to fix them)

#### Pitfall A: The "Smoothing" Fallacy (The biggest risk)

We propose converting discrete GHS categories (1-5) into a continuous "Cost of Mitigation" curve.

**The Risk:** A GHS Category 1 chemical (Fatal if swallowed) might not just be "expensive" to mitigate; it might be legally banned. If the model smooths this too much, the AI might suggest a deadly chemical because it is "super efficient," assuming we can just pay $1M to fix the safety issue.

**The Fix:** Use a "Barrier Function" or "Log-Barrier" approach.

Instead of a linear cost, make the cost exponential:

* Category 5: $10 cost.
* Category 3: $1,000 cost.
* Category 1: $1,000,000,000 cost (effectively infinity).

This forces the Gaussian Process to treat Category 1 regions as "cliffs" that are extremely undesirable, rather than just "expensive slopes."

#### Pitfall B: The "ISS" Implementation Trap

The Infinitely Sharp Step (ISS) method is elegant on paper but mathematically difficult to automate in Python. Detecting the intersection of operating lines for thousands of molecules without human visual inspection is prone to error.

**The Fix:** Start simpler. Use Azeotrope Existence as a binary filter first.

* If Solvent + Ethanol or Solvent + Water forms a new azeotrope → Discard immediately (or penalize heavily).
* Only run the full ISS geometric check on the top 5% of candidates.

#### Pitfall C: The "Empty Set" Problem

What if the "Knee Point" doesn't exist? What if every safe solvent is terrible at separation, and every good solvent is toxic?

**The Fix:** This is still a valid PhD result. It proves that for this specific separation (Ethanol-Water), no magic bullet exists. We then pivot discussion to "Quantifying the Trade-off."

### 3. Ideas to Improve Research Quality

#### 1. The "Baseline" Comparison

To prove AI works, we must compare it against the "Human Standard."

* **Control Group:** Run analysis on Benzene (the old standard) and Ethylene Glycol (a common modern entrainer).
* **Win Condition:** AI must find a molecule that has a better combined score (Safety + Efficiency) than these two.

#### 2. Sensitivity Analysis of the Cost Function

Since we are inventing the "Cost of Mitigation" function, reviewers will ask: "What if cost assumptions are wrong?"

**Improvement:** Run the optimization three times with different weights:

* **Scenario A:** "Profit First" (Low penalty for safety).
* **Scenario B:** "Balanced."
* **Scenario C:** "Safety First" (High penalty for safety).

Show how the Pareto front shifts. This adds depth to discussion.

#### 3. Molecular Fingerprinting

For the QSAR/GP model, the choice of molecular representation matters.

**Recommendation:** Do not just use basic properties (MW, Boiling Point). Use **Morgan Fingerprints (ECFP4)** via RDKit. These capture the substructures (e.g., "this molecule has a benzene ring") which correlates strongly with toxicity.