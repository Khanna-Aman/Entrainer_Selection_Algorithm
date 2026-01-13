Implementation_Plan_02_02_A_Phase 2-A_Multi-Vector Initial Selection - Engine A Deep Research via Graph-RAG.md

# 1. Executive Summary of Phase II-A

**Phase Name:** Multi-Vector Initial Selection - Engine A (Graph-RAG System)
**Primary Objective:** Deploy a "Deep Research" AI architecture to autonomously identify **25–50 high-probability entrainer molecules** by synthesizing academic literature and patent data.

This phase activates "Engine A" of the Tri-Modular selection strategy. Unlike traditional keyword searches, this system utilizes a **Graph-RAG (Retrieval-Augmented Generation)** architecture. It combines the semantic flexibility of Vector Stores (ChromaDB) with the structured relationship mapping of Graph Databases (Neo4j). The system leverages **Gemini 1.5 Pro** as a reasoning engine to iteratively traverse the literature, moving from the broad "Cluster Definitions" established in Phase I to specific, chemically validated molecular candidates, ensuring every selection is backed by citational provenance.

---

# 2. Alignment with Bedrock

This implementation plan strictly adheres to the core methodologies defined in the **Research Proposal**:

* **The "Oil Exploration" Model:** Following Phase I's "Geological Survey," this phase executes the **"Seismic Analysis."** We are now targeting specific "coordinates" (molecules) within the high-probability zones (clusters) identified previously.
* **Tri-Modular Consensus (NLP Vector):** This phase constitutes the **"NLP-based Extraction"** module explicitly called for in the proposal's Data Acquisition section (Section 3.3). It automates the mining of textual safety data and reasoning from papers.
* **Green Chemistry (Safety-by-Design):** The Gemini System Prompt is engineered to flag safety concerns immediately upon selection, adhering to the "Inverse Design" framework where safety is a primary selection variable, not an afterthought.
* **Computer-Aided Molecular Design (CAMD):** We are implementing the "Data-Driven CAMD" framework by using Morgan Fingerprints (via RDKit properties in the graph) and literature sentiment to bridge the gap between chemical structure and separation performance.

---

# 3. High-Level Approach

The strategic methodology for Phase II-A relies on a **Hybrid Memory Architecture** to overcome the limitations of standard LLM contexts.

### Process Flow & Logic

1. **Corpus Aggregation:** We do not rely on the LLM's training data cut-off. We dynamically build a fresh corpus using the **Semantic Scholar API**, targeting the "hot spots" identified in Phase I.
2. **Dual-Knowledge Storage:**
* **Unstructured Data (ChromaDB):** Stores "Chunks" of text (Abstracts, Methods) for semantic similarity retrieval (e.g., "Find papers discussing hydrolysis of amides").
* **Structured Data (Neo4j):** Stores "Nodes" (Molecules, Papers) and "Edges" (MENTIONED_IN, SIMILAR_TO) to understand relationships and chemical properties.


3. **Iterative Reasoning Loop:** The `GeminiResearchEngine` does not perform a single-shot query. It executes a multi-step "Deep Research" cycle:
* *Retrieve Context* -> *Reason on Suitability* -> *Select Candidates* -> *Update Global State* -> *Refine Next Query*.



### Core Principles

* **Provenance is Mandatory:** No molecule is selected without a direct link to a source document (Paper ID or Patent). Hallucinations are strictly filtered.
* **Constraint-Aware Selection:** The system operates within the hardware constraints (32GB RAM) by using a lightweight Graph-RAG stack (Neo4j Community + Local ChromaDB + API-based Inference).
* **Semantic Chunking:** Scientific text is processed via semantic units (concepts/sentences) rather than arbitrary token counts to preserve technical meaning.

---

# 4. Implementation Plan

This section details the execution of the four sub-phases defined in the Phase File.

### Step-by-Step Execution

#### Sub-Phase II-A.1: Document Corpus Preparation

* **Action:** Implement `SemanticScholarClient` to fetch metadata and abstracts.
* **Input:** Search queries derived from Phase I Clusters (e.g., "glycol entrainer distillation", "ionic liquid ethanol separation").
* **Constraint:** Respect API rate limits (1 request/sec).
* **Filter:** Prioritize papers from 2020–2024 to capture recent Green Chemistry advancements, while retaining seminal works.
* **Output:** A raw JSON corpus of approx. 500 relevant papers.

#### Sub-Phase II-A.2: Chunking & Embedding Pipeline

* **Action:** Deploy **Semantic Chunking** logic (`chunk_abstract`) to split text based on sentence boundaries and concept integrity.
* **Action:** Generate "Molecule Cards"—specialized text chunks combining SMILES, physical properties (from RDKit), and literature contexts.
* **Action:** Initialize **ChromaDB** with two collections: `paper_chunks` and `molecule_cards`.
* **Action:** Embed text using `all-MiniLM-L6-v2` (or ChemBERTa if available) for semantic indexing.

#### Sub-Phase II-A.3: Neo4j Graph Schema Design

* **Action:** Configure **Neo4j Community Edition** with the defined schema.
* **Node Definition:** `Molecule` (SMILES key), `Paper`, `Author`, `Cluster` (linked to Phase I), `Property`.
* **Edge Definition:** `[:MENTIONED_IN]`, `[:SIMILAR_TO]` (Tanimoto > 0.85), `[:BELONGS_TO]` (Cluster).
* **Action:** Implement `MoleculeGraphDB` client to populate the graph, linking molecules found in the text to their respective clusters and papers.

#### Sub-Phase II-A.4: Gemini-Powered Iterative Selection

* **Action:** Instantiate the `GeminiResearchEngine`.
* **Logic:** Run the **Iterative Research Workflow** (5 iterations, ~10 molecules per batch):
1. **Context Construction:** Fetch relevant vector chunks + Graph neighbors.
2. **Prompt Engineering:** Inject strict rules (No hallucination, cite sources, flag safety).
3. **Parsing:** Extract SMILES, Name, Rationale, and Confidence from Gemini output.
4. **State Update:** Add to `ResearchSession` to prevent duplicate selections in subsequent loops.


* **Validation:** Ensure every selected molecule has a valid SMILES string and a traceable source.

### Key Deliverables

| Category | Deliverable Item | Format |
| --- | --- | --- |
| **Code** | `05_corpus_acquisition.ipynb` (Semantic Scholar Pipeline) | Jupyter Notebook |
| **Code** | `06_chunking_embedding.ipynb` (ChromaDB Setup) | Jupyter Notebook |
| **Code** | `07_neo4j_population.ipynb` (Graph Schema & Load) | Jupyter Notebook |
| **Code** | `08_gemini_research.ipynb` (The Reasoning Loop) | Jupyter Notebook |
| **Code** | `src/` Module Library (GraphDB, VectorStore, LLM Clients) | Python Package |
| **Data** | **Vector Store** (Populated ChromaDB instance) | Directory |
| **Data** | **Knowledge Graph** (Neo4j Database Dump) | .dump file |
| **Result** | `engine_a_results.json` (25-50 Selected Molecules) | JSON |

---

# 5. Continuity Check

**How this builds upon the Previous Phase (Phase I):**

* **Cluster Usage:** The *inputs* for the literature search queries are the **"Molecular Hot Spots"** (Cluster definitions) identified in Phase I.
* **Scoping:** The graph schema includes a `[:BELONGS_TO]` relationship specifically to link new candidates back to the Phase I mechanism ontology.
* **Exclusion:** The Phase I **Benchmark Compounds** (Benzene, Ethylene Glycol) are used as reference points in the prompt context to ground the LLM's comparative reasoning.

**How this prepares for the Next Phase (Phase II-B/C & Phase III):**

* **Overlap Check:** The list of 25-50 molecules produced here will be cross-referenced against the outputs of Engine B (TRIZ) and Engine C (Cheminformatics) to identify "High Confidence Intersections."
* **Deep Traversal:** The **Neo4j Graph** built here is not a throwaway artifact; it is the *foundation* for the **Phase III Deep Traversal**, where we will algorithmically expand the search from these initial "Seed Nodes."

