This structure is designed to position your Master’s research as a rigorous contribution to **Computer-Aided Molecular Design (CAMD)** and **Process Systems Engineering (PSE)**. It targets high-impact journals found on ScienceDirect (e.g., *Computers & Chemical Engineering*, *AIChE Journal*, *Chemical Engineering Science*) and fits the preprint standards of arXiv.

The structure translates your project-management terminology ("Phases") into standard academic nomenclature ("Methodology," "Framework," "Evaluation").

---

### **Proposed Title Options**

* **Option A (Technical):** *An Active Learning Framework for the Simultaneous Optimization of Thermodynamic Efficiency and Inherent Safety in Extractive Distillation Entrainers.*
* **Option B (Impact-Focused):** *Beyond Sequential Design: A Multi-Vector AI Approach to Safety-by-Design in Solvent Selection.*
* **Option C (Methodological):** *Hybridizing Graph-RAG, TRIZ, and Bayesian Optimization for Inverse Molecular Design: A Case Study in Ethanol-Water Separation.*

---

### **Structured Table of Contents**

#### **Abstract**

* **Context:** The conflict between thermodynamic efficiency and safety in industrial separations.
* **Gap:** Limitations of sequential optimization and discrete safety data cliffs.
* **Method:** A hierarchical "Geological Survey" framework combining Graph-RAG, TRIZ-based heuristics, and Multi-Objective Bayesian Optimization (MOBO).
* **Results:** Identification of Pareto-optimal knee points for ethanol-water separation using a continuous Safety-Cost Barrier Function.
* **Conclusion:** Demonstration of a reproducible, safety-first computational pipeline.

---

#### **1. Introduction**

* **1.1 The Industrial Challenge:**
* Energy intensity of azeotropic separations (Ethanol-Water context).
* Historical reliance on high-efficiency but hazardous solvents (e.g., Benzene).


* **1.2 The Paradigm Shift:**
* Moving from "Forward Simulation" (testing known molecules) to "Inverse Design" (generating molecules from constraints).
* The transition from sequential optimization (Efficiency  Check Safety) to simultaneous optimization.


* **1.3 Problem Statement:**
* The "No-Free-Lunch" theorem in separation processes.
* Difficulty in modeling discrete safety regulations (GHS categories) in continuous optimization landscapes.


* **1.4 Research Objectives & Contributions:**
* Development of a continuous Safety-Cost Penalty Function.
* Integration of heuristic (TRIZ) and semantic (Graph-RAG) reasoning in candidate generation.
* Validation via the Infinitely Sharp Step (ISS) method and shortcut process simulation.



#### **2. Theoretical Background**

* **2.1 Computer-Aided Molecular Design (CAMD):**
* Overview of Group Contribution Methods (UNIFAC) vs. Topology-Based Learning (Morgan Fingerprints).


* **2.2 Inherent Safety in Process Design:**
* The Kletz Paradigm: Elimination/Substitution vs. Control.
* Existing safety indices (ISI) and their limitations in optimization loops.


* **2.3 Artificial Intelligence in Chemical Engineering:**
* Retrieval-Augmented Generation (RAG) in scientific literature mining.
* Multi-Objective Bayesian Optimization (MOBO) for experimental design.



#### **3. Methodology: The Hierarchical Search Framework**

*(Note: This section consolidates your "Phases I-III" into a coherent scientific narrative)*

* **3.1 Overview of the Architecture:**
* The "Oil Exploration" metaphor: Global Survey  Seismic Analysis  Drilling.


* **3.2 Domain Definition and Clustering (Global Survey):**
* Mechanism-informed clustering (Hydrogen Bonding, Polarity Shift, Salting Out).
* Use of SMARTS patterns for chemical ontology definition.


* **3.3 Multi-Vector Candidate Generation:**
* *Vector A: Semantic Literature Mining (Graph-RAG):* Utilizing Neo4j and Gemini to ground selection in peer-reviewed provenance.
* *Vector B: Heuristic Innovation (TRIZ):* Application of Contradiction Analysis and Su-Field modeling to resolve the Efficiency-Safety paradox.
* *Vector C: Cheminformatic Diversity:* Ensuring coverage of the chemical space via RDKit descriptors.


* **3.4 Knowledge Graph Traversal:**
* Seed consolidation and expansion strategies.
* Traversal algorithms: Structural similarity vs. Co-citation networks.



#### **4. Intelligent Optimization (The Active Learning Loop)**

*(Note: This section covers "Phase IV" and is the mathematical core of the paper)*

* **4.1 Problem Formulation:**
* Definition of the bi-objective optimization problem (Maximize Efficiency, Minimize Safety Cost).


* **4.2 The Safety-Cost Barrier Function:**
* **Innovation:** Mathematical transformation of discrete GHS categories into a continuous, differentiable cost surface.
* Handling "Legally Infeasible" regions via barrier penalties.


* **4.3 Gaussian Process Surrogate Modeling:**
* Feature encoding (Morgan Fingerprints).
* Kernel selection and hyperparameter tuning.


* **4.4 Acquisition Strategy:**
* Utilization of q-Expected Hypervolume Improvement (qEHVI) for batch candidate selection.
* Hypothesis H1 & H2: Testing Pareto convexity and budget efficiency.



#### **5. Simulation and Validation**

*(Note: This covers "Phase V")*

* **5.1 Thermodynamic Modeling:**
* UNIFAC-based estimation of Infinite Dilution Activity Coefficients ().
* Azeotrope detection and distillation boundary analysis.


* **5.2 Process Simulation:**
* Feed specifications and rigorous KPI definitions.
* Application of Fenske-Underwood-Gilliland (FUG) shortcut methods for energy and stage estimation.


* **5.3 Benchmark Comparison:**
* Defining the control group: Ethylene Glycol (Industry Standard) vs. Benzene (Historical Standard).



#### **6. Results and Discussion**

* **6.1 Candidate Generation Analysis:**
* Venn diagram analysis of molecules proposed by Graph-RAG vs. TRIZ.
* Evaluation of "Novelty" vs. "Provenance."


* **6.2 Optimization Trajectories:**
* Pareto frontier visualization (Efficiency vs. Safety).
* Identification and analysis of "Knee Points" (Optimal trade-off candidates).
* Convergence plots demonstrating active learning efficiency.


* **6.3 Case Study Validation:**
* Detailed profile of the top 3 recommended entrainers.
* Comparison of reboiler duty and toxicity profiles against Ethylene Glycol.


* **6.4 Sensitivity Analysis:**
* Impact of varying the Safety-Cost penalty weights on candidate selection.



#### **7. Conclusion**

* **7.1 Summary of Findings:** Successful identification of safer, efficient alternatives.
* **7.2 Methodological Contributions:** Validation of the Multi-Vector + MOBO approach.
* **7.3 Future Directions:** Experimental validation and extension to other azeotropic systems.

#### **8. References**

#### **9. Supplementary Materials**

* **S1:** Detailed TRIZ Contradiction Matrix for Molecular Design.
* **S2:** Mathematical derivation of the Safety Barrier Function.
* **S3:** GitHub Repository link (Dockerized Virtual Lab).

---

### **Advice for "Selling" this to Journals**

1. **Frame TRIZ Carefully:** In pure engineering journals, TRIZ can sometimes be viewed as "soft" science. Frame Section 3.3 (Vector B) as **"Heuristic-Driven Hypothesis Generation"** or **"Expert System Integration"** rather than just "TRIZ consultation." Emphasize that it formalizes expert intuition into a reproducible algorithm.
2. **Highlight the Barrier Function:** The conversion of discrete GHS safety categories into a continuous function usable by Gaussian Processes (Section 4.2) is a significant mathematical contribution. Highlight this in the abstract.
3. **The "Why" Matters:** Ensure the Introduction explicitly states *why* previous attempts failed (usually because they optimized efficiency first and safety second). Your "Simultaneous Optimization" is the key selling point.