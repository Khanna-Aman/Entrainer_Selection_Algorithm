Implementation_Plan_02_05_Phase 5 - Simulation & Validation.md

# High-Level Approach and Implementation Plan - Phase V

## Phase V: Simulation & Validation ("The Final Assay")

---

### 1. Executive Summary of Phase V

**Phase Name:** Simulation & Validation
**Primary Objective:** Subject the "Shortlist" (Top 10 Pareto-optimal candidates from Phase IV) to rigorous **Process Simulation** to validate their real-world performance against industrial Key Performance Indicators (KPIs).

While Phase IV used statistical surrogates to predict performance, Phase V uses **deterministic chemical engineering principles** to verify those predictions. This phase functions as the "Final Assay" in the exploration model. We utilize the **Fenske-Underwood-Gilliland (FUG)** shortcut method to model the extractive distillation process, calculating precise energy duties, purity levels, and entrainer circulation rates. The methodology explicitly compares all AI-generated candidates against the industry benchmark (**Ethylene Glycol**) to quantify improvements in efficiency and safety.

---

### 2. Alignment with Bedrock

This plan aligns with the **Research Proposal** and **Core Methodologies** as follows:

* **Process Systems Engineering (PSE):** We are implementing the "Superstructure Optimization" framework mentioned in the Bedrock (Section 5.C). We are not just analyzing the fluid properties; we are simulating the fluid's interaction with the column mechanics (stages, reflux, energy).
* **Validation of Hypothesis H1/H2:** By generating concrete simulation data, we provide the ground truth required to validate the Pareto frontier generated in Phase IV.
* **The "ISS" Method:** We implement the "Simplified Infinitely Sharp Step" method (as defined in the Phase File) by rigorously checking for new azeotrope formation before running the column simulation, ensuring no distillation boundaries are crossed.
* **Benchmarks:** We adhere to the "Critical Analysis" requirement to compare AI results against a **Control Group** (Ethylene Glycol), providing a "Human Standard" for the thesis defense.

---

### 3. High-Level Approach

The methodology shifts from *Data Science* (Phases I–IV) to *Chemical Engineering* (Phase V).

#### Process Flow & Logic

1. **Feed Specification:** Define a standardized industrial feed (Azeotropic Ethanol-Water at 1 atm) to ensure all candidates are tested under identical conditions.
2. **Thermodynamic Rigor:** Move beyond simple property prediction. We calculate **Activity Coefficients** (via UNIFAC) and perform a **Binary Azeotrope Check** to ensure the entrainer does not form new, inseparable mixtures with the feed components.
3. **Shortcut Simulation (FUG Method):** Since full rigorous simulation (Aspen Plus) is resource-constrained, we deploy the **Fenske-Underwood-Gilliland** shortcut sequence:
* *Fenske:* Calculates Minimum Stages ().
* *Underwood:* Calculates Minimum Reflux ().
* *Gilliland:* Estimates Actual Stages and Reflux Ratio for a given efficiency.


4. **KPI Evaluation:** Scoring based on the Research Proposal's criteria: Purity (99.5%), Energy (Reboiler Duty), and Safety (Phase IV score).
5. **Final Ranking:** A weighted hierarchy identifying the "Gold Standard" molecule.

#### Core Principles

* **Feasibility First:** Any molecule that forms a new azeotrope with Ethanol or Water is immediately disqualified (The "ISS" Filter), regardless of its efficiency score.
* **Relative Scoring:** All energy and circulation metrics are normalized against the Ethylene Glycol benchmark. A candidate is only "valid" if it outperforms the benchmark in at least one dimension (Safety or Efficiency).

---

### 4. Implementation Plan

#### Sub-Phase V.1: Feed & Process Specification

* **Objective:** Define the immutable boundary conditions for the simulation.
* **Action:** Implement `src/simulation/feed_specification.py`.
* **Definitions:**
* **Feed:** 85 mol% Ethanol / 15 mol% Water (Near-azeotrope from Beer Column).
* **Product Target:**  99.5 mol% Ethanol (Fuel Grade ASTM D4806).
* **Benchmark:** Ethylene Glycol (Entrainer-to-Feed Ratio = 2.5).


* **Output:** A `SimulationCase` object for every Phase IV candidate + the Benchmark.

#### Sub-Phase V.2: Thermodynamic Property Calculation

* **Objective:** Generate the VLE (Vapor-Liquid Equilibrium) data required for simulation.
* **Action:** Implement `src/simulation/thermodynamics.py`.
* **Method:**
* **UNIFAC Implementation:** Use `rdkit` descriptors to approximate UNIFAC groups or utilize the `thermo` library if available for rigorous activity coefficient () calculation.
* **Selectivity Calculation:** .
* **Azeotrope Checker:** A heuristic check for specific functional groups (e.g., primary alcohols) combined with volatility analysis to flag potential azeotrope formation (Simplified ISS).



#### Sub-Phase V.3: Shortcut Process Simulation (The Engine)

* **Objective:** Execute the column design calculations.
* **Action:** Implement `src/simulation/shortcut_simulation.py`.
* **Logic (FUG Sequence):**
1. **Relative Volatility ():** Derive effective  in the presence of the entrainer.
2. **Fenske Eq:** Calculate theoretical minimum stages ().
3. **Underwood Eq:** Calculate minimum reflux ratio ().
4. **Gilliland Correlation:** Derive actual stages () and Reflux () using a Molokanov approximation.
5. **Energy Estimate:** Calculate Reboiler Duty () based on Vapor Rate and Heat of Vaporization.


* **Output:** `ShortcutResults` object containing Duty (kW), Stage Count, and Purity estimates.

#### Sub-Phase V.4: KPI Evaluation & Ranking

* **Objective:** Score candidates against the project goals.
* **Action:** Implement `src/simulation/kpi_evaluation.py`.
* **Metrics:**
* **Purity:** Pass/Fail (Must meet 99.5%).
* **Energy Score:** Normalized inverse of Reboiler Duty.
* **Safety Score:** Carry-over from Phase IV (Cost of Mitigation).
* **Entrainer Metrics:** Circulation Rate and Loss Fraction.


* **Action:** Generate the `FinalRanking` comparing `Candidate_Score` vs `Benchmark_Score`.

#### Sub-Phase V.5: Phase V Orchestrator

* **Objective:** Integrate the pipeline and generate the final report.
* **Action:** Implement `src/simulation/phase5_orchestrator.py`.
* **Workflow:**
1. Load Phase IV Pareto Frontier.
2. Create Benchmark Case.
3. Run Thermodynamics -> Simulation -> KPI Evaluation for all cases.
4. Export `phase5_results.json` and human-readable `phase5_report.txt`.



### Key Deliverables

| Category | Deliverable Item | Description |
| --- | --- | --- |
| **Code** | `src/simulation/` | Full Python package (FUG method, UNIFAC logic, KPI scoring). |
| **Data** | `phase5_results.json` | Comprehensive simulation data for the Top 10 + Benchmark. |
| **Report** | `phase5_report.txt` | Final "Executive Report" ranking the molecules. |
| **Notebook** | `37_phase5_integration.ipynb` | End-to-end execution of the simulation pipeline. |
| **Vis** | **Final Hierarchy Plot** | Bar chart comparing Candidate Energy/Safety vs. Benchmark. |

---

### 5. Continuity Check

**How this builds upon the Previous Phase (Phase IV):**

* **Input Specificity:** Phase V strictly processes the **Pareto-Optimal Frontier** (Top 10 candidates) generated in Phase IV. It relies entirely on the efficiency and safety scores calculated by the Phase IV "Oracles" as starting priors.
* **Knee Point Prioritization:** The logic explicitly prioritizes molecules identified as "Knee Points" in Phase IV for detailed simulation, ensuring we validate the most critical trade-off opportunities.

**Conclusion of the Project:**

* **Deliverable Fulfillment:** This phase generates the final "Quantifiable Metrics" (e.g., "Reduction in ISI by 20% with <8% efficiency penalty") promised in the Research Proposal.
* **Portfolio Ready:** The output is a complete, validated database and a reproducible code artifact (The Dockerized Lab), fulfilling the objective of a reusable computational framework.