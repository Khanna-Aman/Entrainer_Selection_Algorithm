# 🎯 Phase II-B Implementation: Multi-Vector Initial Selection - Engine B

**Engine B** is a **TRIZ-Powered Consultation Module** that:

1. **Input:** Takes the Graph-RAG corpus (from Engine A) and Molecule Database
2. **Process:** Applies TRIZ (Theory of Inventive Problem Solving) as an analytical lens for hypothesis generation
3. **Output:** Yields 25-50 molecules and/or directional insights, flagging overlaps with Engine A

**Key Design Intent:** TRIZ serves as a "structured formalization of expert intuition" - a hypothesis-generation heuristic that approaches molecule selection from a **functional innovation perspective** rather than purely data-driven analysis.

**The TRIZ techniques to be evaluated:**
- Contradictions (Technical & Physical)
- Ideality & Ideal Final Result (IFR)
- Trends of Engineering System Evolution
- Psychological Inertia breaking
- 40 Inventive Principles
- Contradiction Matrix
- Separation Principles (Time, Space, Condition, Scale)
- Substance-Field (Su-Field) Analysis
- 76 Standard Solutions
- Function Analysis
- 9 Windows (System Operator)
- Smart Little People (SLP)
- Effects Database (Scientific Effects)
- Trimming
- ARIZ (full algorithm)

**Additional ideation frameworks:** First Principles Thinking, Inverse Design, Bio-isosterism & Scaffold Hopping

---

## Recommended Approach

### Why TRIZ for Molecule Selection?

TRIZ was developed for mechanical/engineering systems, but its core philosophy—**systematic innovation through contradiction resolution**—translates to molecular design:

| TRIZ Concept | Chemical Separation Application |
|--------------|--------------------------------|
| Technical Contradiction | "We need high selectivity (strong interaction with water) BUT low energy for regeneration" |
| Physical Contradiction | "The entrainer must be polar (to interact with water) AND non-polar (to separate easily)" |
| Ideality | "The ideal entrainer separates perfectly with zero energy input and zero toxicity" |
| Separation Principles | Resolve contradictions by separating in Time (temperature-dependent behavior), Space (structured materials), Condition (pH-dependent), Scale (nano-confinement) |

### Architecture Overview: Multi-Agent TRIZ System

We recommend a **modular multi-agent architecture** where each agent specializes in a subset of TRIZ techniques:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  ENGINE B: TRIZ-POWERED CONSULTATION                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    ORCHESTRATOR AGENT                             │  │
│  │  - Receives molecule database + problem definition                │  │
│  │  - Routes to specialist agents                                    │  │
│  │  - Aggregates and synthesizes results                             │  │
│  │  - Flags Engine A overlaps                                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                     │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│  ┌─────────────┐     ┌─────────────┐      ┌─────────────┐              │
│  │ AGENT 1:    │     │ AGENT 2:    │      │ AGENT 3:    │              │
│  │ Contradiction│     │ System      │      │ Su-Field &  │              │
│  │ Analysis    │     │ Evolution   │      │ Standard    │              │
│  │             │     │             │      │ Solutions   │              │
│  │ • Technical │     │ • 9 Windows │      │ • Su-Field  │              │
│  │ • Physical  │     │ • Trends    │      │ • 76 Stds   │              │
│  │ • Matrix    │     │ • Trimming  │      │ • Effects   │              │
│  │ • 40 Princ. │     │ • IFR       │      │ • SLP       │              │
│  │ • Separation│     │             │      │             │              │
│  └──────┬──────┘     └──────┬──────┘      └──────┬──────┘              │
│         │                   │                    │                      │
│         ▼                   ▼                    ▼                      │
│  ┌─────────────┐     ┌─────────────┐      ┌─────────────┐              │
│  │ AGENT 4:    │     │ AGENT 5:    │      │ AGENT 6:    │              │
│  │ First       │     │ Inverse     │      │ Bio-iso &   │              │
│  │ Principles  │     │ Design      │      │ Scaffold    │              │
│  │             │     │             │      │ Hopping     │              │
│  │ • Ab Initio │     │ • Target →  │      │ • Lateral   │              │
│  │ • Physics   │     │   Structure │      │   Thinking  │              │
│  │ • Thermo.   │     │ • Generative│      │ • Analogs   │              │
│  └──────┬──────┘     └──────┬──────┘      └──────┬──────┘              │
│         │                   │                    │                      │
│         └───────────────────┴────────────────────┘                      │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    SYNTHESIS AGENT                                │  │
│  │  - Consolidates all agent outputs                                 │  │
│  │  - Applies ARIZ for complex contradictions                        │  │
│  │  - Ranks by innovation potential + feasibility                    │  │
│  │  - Generates final 25-50 molecules + insights                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## TRIZ Framework Translation to Molecular Design

Before implementing agents, we need to establish **how each TRIZ tool translates to molecule selection**. This is the key intellectual contribution—without this mapping, the agents cannot function.

### Core TRIZ Concepts for Ethanol-Water Separation

```python
# src/triz/domain_mapping.py
"""
Phase II-B: TRIZ Domain Mapping for Ethanol-Water Separation

This module defines how TRIZ concepts translate to molecular/separation science.

References:
- Altshuller, G. (1999). "The Innovation Algorithm: TRIZ, Systematic Innovation 
  and Technical Creativity" - Primary TRIZ source
- Mann, D. (2002). "Hands-On Systematic Innovation" - TRIZ for chemistry applications
  [NEEDS VERIFICATION: Check if Mann's chemistry applications are still current]
- Terninko et al. (1998). "Systematic Innovation: An Introduction to TRIZ"

NOTE: The translation of TRIZ to molecular design is an active research area.
The mappings below are based on general principles and should be validated
with domain experts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ============================================================================
# CONTRADICTIONS FOR ETHANOL-WATER SEPARATION
# ============================================================================

@dataclass
class TechnicalContradiction:
    """
    A Technical Contradiction exists when improving one parameter 
    degrades another parameter.
    
    In TRIZ, these are resolved using the Contradiction Matrix + 40 Principles.
    """
    improving_parameter: str
    worsening_parameter: str
    description: str
    relevant_principles: List[int] = field(default_factory=list)  # From 40 Principles
    molecular_interpretation: str = ""

@dataclass
class PhysicalContradiction:
    """
    A Physical Contradiction exists when a parameter must simultaneously 
    have opposite values.
    
    Resolved using Separation Principles (Time, Space, Condition, Scale).
    """
    parameter: str
    required_state_a: str
    required_state_b: str
    description: str
    separation_strategy: str = ""
    molecular_interpretation: str = ""

# Define the core contradictions for ethanol-water separation
ETHANOL_WATER_TECHNICAL_CONTRADICTIONS = [
    TechnicalContradiction(
        improving_parameter="Selectivity (relative volatility enhancement)",
        worsening_parameter="Energy consumption (entrainer regeneration)",
        description="""
        Strong interactions with water increase selectivity but require 
        more energy to break for entrainer recovery.
        """,
        relevant_principles=[35, 28, 15, 10],  # See 40 Principles mapping below
        molecular_interpretation="""
        Need molecules with strong but reversible water interactions.
        Temperature-switchable hydrogen bonding, or molecules where 
        water affinity decreases significantly at elevated T.
        """
    ),
    TechnicalContradiction(
        improving_parameter="Selectivity",
        worsening_parameter="Safety (toxicity, flammability)",
        description="""
        Many highly selective entrainers (aromatics, halogenated compounds)
        have significant safety hazards.
        """,
        relevant_principles=[22, 35, 27, 3],
        molecular_interpretation="""
        Seek selectivity from structural features NOT associated with 
        toxicity: avoid benzene rings, prefer glycol-based or bio-derived.
        """
    ),
    TechnicalContradiction(
        improving_parameter="Low cost",
        worsening_parameter="Thermal stability",
        description="""
        Simple, cheap molecules often degrade at distillation temperatures.
        Complex, stable molecules are expensive to synthesize.
        """,
        relevant_principles=[1, 27, 35, 2],
        molecular_interpretation="""
        Look for naturally abundant molecules with inherent thermal stability:
        sugar alcohols, terpenes, amino acid derivatives.
        """
    ),
    TechnicalContradiction(
        improving_parameter="Low viscosity (easy pumping)",
        worsening_parameter="Low volatility (stays in column)",
        description="""
        Low MW = low viscosity but high vapor pressure.
        High MW = low VP but high viscosity.
        """,
        relevant_principles=[35, 3, 15, 19],
        molecular_interpretation="""
        Branched structures: higher MW without excessive viscosity.
        Or ionic liquids (low VP but requires handling viscosity).
        """
    ),
]

ETHANOL_WATER_PHYSICAL_CONTRADICTIONS = [
    PhysicalContradiction(
        parameter="Polarity",
        required_state_a="High polarity (to preferentially interact with water)",
        required_state_b="Low polarity (to easily separate from water/ethanol mix)",
        description="""
        The entrainer must be polar enough to disrupt water-ethanol H-bonds
        but non-polar enough to phase separate or distill cleanly.
        """,
        separation_strategy="CONDITION - pH or temperature dependent polarity",
        molecular_interpretation="""
        Molecules with switchable polarity: 
        - CO2-switchable solvents (tertiary amines)
        - Temperature-responsive polymers (LCST behavior)
        - pH-responsive systems
        """
    ),
    PhysicalContradiction(
        parameter="Water affinity",
        required_state_a="Strong water affinity (during separation)",
        required_state_b="Weak water affinity (during regeneration)",
        description="Must grab water tightly then release it easily.",
        separation_strategy="TIME - different behavior at different T",
        molecular_interpretation="""
        Hydrogen bond donors/acceptors with temperature-dependent 
        H-bonding strength. Consider molecules where H-bond geometry 
        becomes unfavorable at high T.
        """
    ),
    PhysicalContradiction(
        parameter="Molecular weight",
        required_state_a="High MW (low volatility for easy recovery)",
        required_state_b="Low MW (fast mass transfer, low viscosity)",
        description="Large molecules stay in column but diffuse slowly.",
        separation_strategy="SCALE - nanoscale properties differ from bulk",
        molecular_interpretation="""
        Oligomeric glycols (PEG 200-400): large enough for low VP
        but still reasonably mobile. Or structured ILs with 
        nano-segregated domains.
        """
    ),
]

# ============================================================================
# 40 INVENTIVE PRINCIPLES - MOLECULAR INTERPRETATION
# ============================================================================

# Reference: Altshuller's 40 Principles
# NOTE: Not all 40 principles translate meaningfully to molecular design.
# Below are the most relevant ones for entrainer selection.

RELEVANT_INVENTIVE_PRINCIPLES = {
    1: {
        "name": "Segmentation",
        "original": "Divide an object into independent parts",
        "molecular_interpretation": """
        Use modular molecular design: functional groups that can be 
        combined independently. Example: varying alkyl chain length 
        on a glycol backbone.
        """,
        "entrainer_application": """
        Don't search for one perfect molecule - search for optimal 
        COMBINATIONS of functional groups. Modular DES design.
        """
    },
    2: {
        "name": "Taking out / Extraction",
        "original": "Extract the disturbing part or property",
        "molecular_interpretation": """
        Remove molecular features that cause unwanted properties.
        If a good entrainer is toxic due to a specific group, 
        find analogs without that group.
        """,
        "entrainer_application": """
        Identify the structural features causing high selectivity 
        SEPARATELY from those causing toxicity. Keep the former.
        """
    },
    3: {
        "name": "Local quality",
        "original": "Change uniform structure to non-uniform",
        "molecular_interpretation": """
        Amphiphilic molecules with distinct polar/non-polar regions.
        The non-uniformity creates interfacial activity.
        """,
        "entrainer_application": """
        Glycol ethers: polar hydroxyl end + non-polar alkyl chain.
        This non-uniformity may enhance selectivity.
        """
    },
    10: {
        "name": "Preliminary action",
        "original": "Perform required changes in advance",
        "molecular_interpretation": """
        Pre-functionalize molecules. Add protecting groups that 
        activate under separation conditions.
        """,
        "entrainer_application": """
        Salt-addition to ILs to pre-tune water affinity before 
        introducing to column.
        """
    },
    15: {
        "name": "Dynamization / Dynamics",
        "original": "Make rigid objects movable or adaptive",
        "molecular_interpretation": """
        Molecules that change conformation in response to conditions.
        Flexible vs. rigid backbone effects.
        """,
        "entrainer_application": """
        Consider conformationally flexible molecules that can 
        adapt their shape to optimize water binding geometry.
        """
    },
    22: {
        "name": "Blessing in disguise",
        "original": "Use harmful factors to achieve positive effect",
        "molecular_interpretation": """
        The 'problematic' property of one molecule might be 
        beneficial in context.
        """,
        "entrainer_application": """
        High viscosity of ILs: problem for pumping, but creates 
        film that might enhance mass transfer in structured packing.
        """
    },
    27: {
        "name": "Cheap short-living objects",
        "original": "Replace expensive, durable with cheap, disposable",
        "molecular_interpretation": """
        Bio-derived solvents that may degrade but are cheap to 
        replace. Renewable feedstocks.
        """,
        "entrainer_application": """
        Glycerol, sorbitol, cheap sugar alcohols. Some loss is 
        acceptable if replacement cost is low.
        """
    },
    28: {
        "name": "Mechanics substitution",
        "original": "Replace mechanical with other fields",
        "molecular_interpretation": """
        Use non-covalent interactions instead of physical separation.
        Electric fields, magnetic separation.
        """,
        "entrainer_application": """
        Paramagnetic ILs that could be recovered magnetically.
        [NEEDS VERIFICATION: Current state of this technology]
        """
    },
    35: {
        "name": "Parameter changes",
        "original": "Change physical state, concentration, flexibility, temperature",
        "molecular_interpretation": """
        Operate at different T/P to change molecular behavior.
        Solvent properties are highly T-dependent.
        """,
        "entrainer_application": """
        Map selectivity vs. temperature for candidates.
        Some may show non-linear improvements at specific T ranges.
        """
    },
    39: {
        "name": "Inert atmosphere",
        "original": "Replace normal environment with inert",
        "molecular_interpretation": """
        Change the medium surrounding the molecules. 
        Supercritical CO2 as modifier.
        """,
        "entrainer_application": """
        Entrainer + CO2 combinations for enhanced separation.
        [NEEDS VERIFICATION: Industrial applicability]
        """
    },
}

# ============================================================================
# SEPARATION PRINCIPLES FOR PHYSICAL CONTRADICTIONS
# ============================================================================

@dataclass
class SeparationPrinciple:
    """
    Physical contradictions are resolved by separating requirements:
    - In TIME: requirement A at t1, requirement B at t2
    - In SPACE: requirement A in region 1, requirement B in region 2  
    - In CONDITION: requirement A under condition C1, B under condition C2
    - In SCALE: requirement A at scale S1 (nano), B at scale S2 (macro)
    """
    name: str
    description: str
    molecular_examples: List[str]

SEPARATION_PRINCIPLES = [
    SeparationPrinciple(
        name="Separation in TIME",
        description="""
        The contradictory requirements are met at different times.
        In molecular terms: temperature-dependent behavior.
        """,
        molecular_examples=[
            "Thermoresponsive polymers (LCST/UCST behavior)",
            "H-bond strength decreasing with temperature",
            "Entrainers with T-dependent phase behavior",
        ]
    ),
    SeparationPrinciple(
        name="Separation in SPACE",
        description="""
        Different regions of the system meet different requirements.
        In molecular terms: amphiphilicity, compartmentalization.
        """,
        molecular_examples=[
            "Amphiphilic molecules with polar/non-polar domains",
            "Micelle-forming surfactants",
            "Membrane-active compounds",
        ]
    ),
    SeparationPrinciple(
        name="Separation in CONDITION",
        description="""
        Different conditions trigger different behaviors.
        pH, solvent composition, salt concentration as triggers.
        """,
        molecular_examples=[
            "CO2-switchable solvents (tertiary amines)",
            "pH-responsive polymers",
            "Salt-sensitive phase separation",
        ]
    ),
    SeparationPrinciple(
        name="Separation in SCALE",
        description="""
        Behavior differs at different scales (nano vs macro).
        In molecular terms: nanoscale self-assembly effects.
        """,
        molecular_examples=[
            "Nano-segregated ionic liquids",
            "Hierarchical porous materials (MOFs with multiple pore sizes)",
            "Microphase-separated block copolymers",
        ]
    ),
]

# ============================================================================
# IDEAL FINAL RESULT (IFR) FOR ETHANOL-WATER SEPARATION
# ============================================================================

IDEAL_FINAL_RESULT = """
The IDEAL entrainer for ethanol-water separation:

1. DELIVERS THE FUNCTION WITHOUT EXISTING:
   - The ideal entrainer requires zero material - separation happens spontaneously
   - Approximation: membrane separation (no entrainer mass in product)
   
2. IF IT MUST EXIST, IT COSTS NOTHING:
   - Water itself as the "entrainer" (pressure-swing distillation)
   - Waste streams as entrainers (if chemically suitable)
   
3. IF IT COSTS SOMETHING, IT DOES MULTIPLE FUNCTIONS:
   - Entrainer that is also the fuel product (gasoline blend)
   - Entrainer that is a valuable co-product
   
4. IF SINGLE FUNCTION, IT HAS ZERO SIDE EFFECTS:
   - Non-toxic, non-flammable, thermally stable, fully recoverable
   - Zero azeotrope formation with either component
   
5. IF SIDE EFFECTS EXIST, THEY ARE BENEFICIAL:
   - Entrainer losses result in biodegradable, non-harmful residues
   - Trace entrainer in product improves product (e.g., fuel additive)

APPROACHING IDEALITY (practical targets):
- Selectivity > 3 (significant enhancement over unity)
- Boiling point > ethanol BP + 50°C (easy separation)
- Zero azeotrope formation with ethanol or water
- GHS acute toxicity category ≥ 4 (low hazard)
- Flash point > 60°C (reduced flammability)
- Cost < $5/kg (commodity pricing)
- Thermal stability > 200°C (no degradation in column)
"""

# ============================================================================
# 9 WINDOWS (SYSTEM OPERATOR) FOR ETHANOL-WATER SEPARATION
# ============================================================================

NINE_WINDOWS = """
The 9 Windows tool examines the system across:
- Hierarchy: Supersystem / System / Subsystem
- Time: Past / Present / Future

For Ethanol-Water Separation:

                    PAST                    PRESENT                 FUTURE
                    
SUPERSYSTEM     Petroleum refining       Bioethanol fuel         Electrofuels,
(Industry)      Benzene was standard     industry                direct CO2-to-fuel
                No safety concerns       Safety regulations      Zero-waste circular
                                         Environmental focus     economy

SYSTEM          Extractive distillation  ED with glycols,        Hybrid separation?
(Separation     with benzene, gasoline   some IL research,       Membrane-ED combo?
Process)                                 DES emerging            Direct biological?

SUBSYSTEM       Single toxic molecule    Multi-component         Responsive materials?
(Entrainer)     High selectivity         Balancing safety/       Self-regenerating?
                Cheap but hazardous      cost/performance        Bio-derived only?

INSIGHTS FROM 9 WINDOWS:
1. Industry is moving toward bio-based and circular approaches
2. Future entrainers likely need to be renewable/biodegradable
3. Hybrid systems may obviate need for traditional entrainers
4. Past mistakes (benzene) inform current safety requirements
5. Subsystem evolution: single molecule → mixtures → smart materials
"""

# ============================================================================
# TRENDS OF ENGINEERING SYSTEM EVOLUTION
# ============================================================================

EVOLUTION_TRENDS = [
    {
        "trend": "Increasing Ideality",
        "description": "Systems evolve toward delivering function with less material/energy",
        "molecular_implication": "Future entrainers will use less material for same effect. High-activity compounds.",
    },
    {
        "trend": "Transition to Supersystem",
        "description": "System becomes part of a larger system",
        "molecular_implication": "Entrainer becomes part of product? (fuel additive that serves dual purpose)",
    },
    {
        "trend": "Increasing Dynamism",
        "description": "Rigid → hinged → flexible → field-based",
        "molecular_implication": "Switchable solvents, stimuli-responsive materials",
    },
    {
        "trend": "Mono-Bi-Poly",
        "description": "Single element → multiple → many optimized elements",
        "molecular_implication": "Single entrainer → binary mixtures → ternary DES → tunable IL mixtures",
    },
    {
        "trend": "Increased Coordination",
        "description": "Uncoordinated actions → synchronized → intelligent control",
        "molecular_implication": "Smart entrainers that respond to local conditions in the column",
    },
]
```

---

## Agent Implementation Framework

### Agent 1: Contradiction Analysis Agent

```python
# src/triz/agents/contradiction_agent.py
"""
Phase II-B: TRIZ Contradiction Analysis Agent

This agent analyzes the ethanol-water separation problem through the lens of
Technical and Physical Contradictions, suggesting molecular candidates based
on contradiction resolution strategies.

References:
- Altshuller, G. "TRIZ: The Theory of Inventive Problem Solving"
- Contradiction Matrix: https://www.triz40.com/ 
  [VERIFY: Check if this resource is still maintained]
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json

# Import domain mapping (from previous section)
# from src.triz.domain_mapping import (
#     ETHANOL_WATER_TECHNICAL_CONTRADICTIONS,
#     ETHANOL_WATER_PHYSICAL_CONTRADICTIONS,
#     RELEVANT_INVENTIVE_PRINCIPLES,
#     SEPARATION_PRINCIPLES,
# )

@dataclass
class ContradictionInsight:
    """Output from contradiction analysis"""
    contradiction_type: str  # "technical" or "physical"
    contradiction_description: str
    resolution_strategy: str
    suggested_molecular_features: List[str]
    candidate_molecules: List[Dict]  # smiles, name, rationale
    confidence: str  # high/medium/low
    triz_principles_used: List[int]

class ContradictionAnalysisAgent:
    """
    Agent that applies TRIZ Contradiction Analysis to molecule selection.
    
    Workflow:
    1. Analyze pre-defined contradictions for ethanol-water separation
    2. Apply relevant Inventive Principles
    3. For physical contradictions, apply Separation Principles
    4. Use LLM to suggest specific molecular features that resolve contradictions
    5. Query molecule database for candidates matching those features
    """
    
    SYSTEM_PROMPT = """You are a TRIZ (Theory of Inventive Problem Solving) expert 
    applying contradiction analysis to molecular design for ethanol-water separation.

Your task is to:
1. Analyze the given contradiction
2. Apply the specified TRIZ Inventive Principles
3. Translate abstract principles into CONCRETE molecular features
4. Suggest specific functional groups or molecular characteristics

IMPORTANT RULES:
- Be SPECIFIC about molecular features (e.g., "hydroxyl groups on adjacent carbons" not "polar groups")
- Only suggest features that are chemically plausible
- Consider synthesis feasibility and cost
- Flag any uncertain suggestions with [NEEDS VERIFICATION]

Output format:
MOLECULAR FEATURES:
- Feature 1: [description] - [which principle this resolves]
- Feature 2: [description] - [which principle this resolves]

CANDIDATE MOLECULAR CLASSES:
- Class 1: [name] - [why it fits]
- Class 2: [name] - [why it fits]

SMARTS PATTERN (if possible):
[SMARTS pattern to search for these features]

CONFIDENCE: [high/medium/low]
REASONING: [explanation]
"""

    def __init__(self, llm_client, molecule_database):
        """
        Args:
            llm_client: LLM client (Gemini or Claude) for reasoning
            molecule_database: Database client for searching candidates
        """
        self.llm = llm_client
        self.db = molecule_database
        
    def analyze_technical_contradiction(
        self, 
        contradiction: Dict
    ) -> ContradictionInsight:
        """
        Analyze a technical contradiction and suggest resolution strategies.
        
        Args:
            contradiction: Dict with keys: improving_parameter, worsening_parameter,
                          description, relevant_principles
        """
        # Build prompt with contradiction details and relevant principles
        principles_text = "\n".join([
            f"Principle {p}: {RELEVANT_INVENTIVE_PRINCIPLES.get(p, {}).get('name', 'Unknown')} - "
            f"{RELEVANT_INVENTIVE_PRINCIPLES.get(p, {}).get('molecular_interpretation', 'No interpretation')}"
            for p in contradiction.get('relevant_principles', [])
        ])
        
        prompt = f"""Analyze this Technical Contradiction for entrainer molecule design:

IMPROVING PARAMETER: {contradiction['improving_parameter']}
WORSENING PARAMETER: {contradiction['worsening_parameter']}

DESCRIPTION:
{contradiction['description']}

MOLECULAR INTERPRETATION:
{contradiction.get('molecular_interpretation', 'Not provided')}

RELEVANT TRIZ PRINCIPLES TO APPLY:
{principles_text}

Based on this analysis, what specific molecular features would resolve this 
contradiction? Be as specific as possible about chemical structures."""

        # Query LLM
        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse response (simplified - production would use structured output)
            insight = self._parse_contradiction_response(
                response_text,
                contradiction_type="technical",
                contradiction=contradiction
            )
            
            # Search for candidate molecules based on suggested features
            if insight.suggested_molecular_features:
                candidates = self._search_candidates_by_features(
                    insight.suggested_molecular_features
                )
                insight.candidate_molecules = candidates
            
            return insight
            
        except Exception as e:
            return ContradictionInsight(
                contradiction_type="technical",
                contradiction_description=contradiction['description'],
                resolution_strategy=f"Error: {e}",
                suggested_molecular_features=[],
                candidate_molecules=[],
                confidence="low",
                triz_principles_used=contradiction.get('relevant_principles', [])
            )
    
    def analyze_physical_contradiction(
        self,
        contradiction: Dict
    ) -> ContradictionInsight:
        """
        Analyze a physical contradiction using Separation Principles.
        """
        prompt = f"""Analyze this Physical Contradiction for entrainer molecule design:

PARAMETER: {contradiction['parameter']}
REQUIRED STATE A: {contradiction['required_state_a']}
REQUIRED STATE B: {contradiction['required_state_b']}

DESCRIPTION:
{contradiction['description']}

SUGGESTED SEPARATION STRATEGY: {contradiction.get('separation_strategy', 'Not specified')}

MOLECULAR INTERPRETATION:
{contradiction.get('molecular_interpretation', 'Not provided')}

SEPARATION PRINCIPLES TO CONSIDER:
1. TIME: Different behavior at different times/temperatures
2. SPACE: Different regions have different properties
3. CONDITION: Behavior changes with pH, salt, solvent
4. SCALE: Nanoscale vs bulk behavior differs

How can we design a molecule that exhibits BOTH required states by separating 
them in time, space, condition, or scale? Be specific about molecular mechanisms."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            insight = self._parse_contradiction_response(
                response_text,
                contradiction_type="physical",
                contradiction=contradiction
            )
            
            if insight.suggested_molecular_features:
                candidates = self._search_candidates_by_features(
                    insight.suggested_molecular_features
                )
                insight.candidate_molecules = candidates
            
            return insight
            
        except Exception as e:
            return ContradictionInsight(
                contradiction_type="physical",
                contradiction_description=contradiction['description'],
                resolution_strategy=f"Error: {e}",
                suggested_molecular_features=[],
                candidate_molecules=[],
                confidence="low",
                triz_principles_used=[]
            )
    
    def _parse_contradiction_response(
        self, 
        response_text: str,
        contradiction_type: str,
        contradiction: Dict
    ) -> ContradictionInsight:
        """Parse LLM response into structured insight."""
        # Simple parsing - extract key sections
        features = []
        
        lines = response_text.split('\n')
        in_features_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'molecular features' in line_lower or 'feature' in line_lower[:20]:
                in_features_section = True
                continue
            
            if in_features_section and line.strip().startswith('-'):
                feature = line.strip().lstrip('-').strip()
                if feature:
                    features.append(feature)
            
            if 'confidence' in line_lower:
                in_features_section = False
        
        # Determine confidence
        confidence = "medium"
        if 'high confidence' in response_text.lower():
            confidence = "high"
        elif 'low confidence' in response_text.lower():
            confidence = "low"
        
        return ContradictionInsight(
            contradiction_type=contradiction_type,
            contradiction_description=contradiction['description'],
            resolution_strategy=response_text[:500],  # First 500 chars as summary
            suggested_molecular_features=features[:10],  # Limit features
            candidate_molecules=[],
            confidence=confidence,
            triz_principles_used=contradiction.get('relevant_principles', [])
        )
    
    def _search_candidates_by_features(
        self, 
        features: List[str],
        max_candidates: int = 10
    ) -> List[Dict]:
        """
        Search molecule database for candidates matching suggested features.
        
        This is a placeholder - actual implementation depends on your database.
        You might:
        1. Convert features to SMARTS patterns
        2. Use semantic search over molecule descriptions
        3. Query by functional group flags
        """
        # Placeholder - return empty list
        # In production, implement actual search
        return []
    
    def run_full_contradiction_analysis(self) -> List[ContradictionInsight]:
        """Run analysis on all pre-defined contradictions."""
        results = []
        
        # Analyze technical contradictions
        for tc in ETHANOL_WATER_TECHNICAL_CONTRADICTIONS:
            insight = self.analyze_technical_contradiction(tc.__dict__)
            results.append(insight)
        
        # Analyze physical contradictions
        for pc in ETHANOL_WATER_PHYSICAL_CONTRADICTIONS:
            insight = self.analyze_physical_contradiction(pc.__dict__)
            results.append(insight)
        
        return results
```

### Agent 2: System Evolution Agent

```python
# src/triz/agents/evolution_agent.py
"""
Phase II-B: TRIZ System Evolution Agent

This agent applies:
- 9 Windows (System Operator) analysis
- Trends of Engineering System Evolution
- Ideality analysis
- Trimming

to identify future-oriented molecular candidates.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class EvolutionInsight:
    """Output from system evolution analysis"""
    tool_used: str  # "9_windows", "trends", "ideality", "trimming"
    temporal_position: str  # "past", "present", "future"
    hierarchy_level: str  # "supersystem", "system", "subsystem"
    insight: str
    molecular_implications: List[str]
    suggested_directions: List[str]
    candidate_molecules: List[Dict]
    confidence: str

class SystemEvolutionAgent:
    """
    Agent that analyzes ethanol-water separation through evolutionary lens.
    
    Key insight: Systems evolve predictably. By understanding current position
    in evolution, we can anticipate future requirements and select molecules
    that will remain relevant.
    """
    
    SYSTEM_PROMPT = """You are a TRIZ expert applying System Evolution analysis 
to molecular design for ethanol-water separation entrainers.

Your tools:
1. 9 WINDOWS: Analyze system across time (past/present/future) and 
   hierarchy (supersystem/system/subsystem)
2. EVOLUTION TRENDS: Apply known patterns of technological evolution
3. IDEALITY: Move toward ideal system (function with minimal resources)
4. TRIMMING: Remove components while preserving function

Current state of ethanol-water separation:
- Supersystem: Bioethanol industry, moving toward sustainability
- System: Extractive distillation with entrainers
- Subsystem: The entrainer molecule itself

Your goal: Identify molecular characteristics that align with FUTURE needs,
not just current optimization.

IMPORTANT:
- Consider regulatory trajectory (likely stricter safety requirements)
- Consider sustainability trends (bio-based, circular economy)
- Consider hybrid process development (membrane + distillation)
- Be specific about molecular implications"""

    def __init__(self, llm_client, molecule_database):
        self.llm = llm_client
        self.db = molecule_database
    
    def analyze_nine_windows(self) -> List[EvolutionInsight]:
        """
        Apply 9 Windows analysis to identify future-oriented requirements.
        """
        windows = [
            ("supersystem", "past", "Historical industrial context"),
            ("supersystem", "present", "Current bioethanol industry state"),
            ("supersystem", "future", "Where is the industry heading?"),
            ("system", "past", "Past separation technologies"),
            ("system", "present", "Current extractive distillation"),
            ("system", "future", "Future separation approaches"),
            ("subsystem", "past", "Historical entrainers (benzene era)"),
            ("subsystem", "present", "Current entrainer choices"),
            ("subsystem", "future", "What will future entrainers look like?"),
        ]
        
        insights = []
        
        # Focus on future windows for molecule selection
        future_prompt = """Analyze the FUTURE windows for ethanol-water separation:

FUTURE SUPERSYSTEM (Industry in 10-20 years):
- What will the bioethanol/biofuels industry look like?
- What regulations will likely exist?
- What sustainability requirements?

FUTURE SYSTEM (Separation technology in 10-20 years):
- Will extractive distillation still be used?
- What hybrid approaches might emerge?
- What efficiency requirements?

FUTURE SUBSYSTEM (Entrainer molecules in 10-20 years):
- What molecular characteristics will be required?
- What will be banned or restricted?
- What new molecular classes might emerge?

Based on this future analysis, what molecular features should we prioritize 
TODAY to select molecules that will still be viable in the future?

Provide:
1. Key molecular features for future-proofing
2. Molecular classes likely to remain viable
3. Molecular classes likely to face restrictions
4. Emerging opportunities (new chemistry)"""

        try:
            response = self.llm.generate(future_prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            insights.append(EvolutionInsight(
                tool_used="9_windows",
                temporal_position="future",
                hierarchy_level="all",
                insight=response_text[:1000],
                molecular_implications=self._extract_implications(response_text),
                suggested_directions=self._extract_directions(response_text),
                candidate_molecules=[],
                confidence="medium"  # Future predictions inherently uncertain
            ))
            
        except Exception as e:
            insights.append(EvolutionInsight(
                tool_used="9_windows",
                temporal_position="future",
                hierarchy_level="all",
                insight=f"Analysis error: {e}",
                molecular_implications=[],
                suggested_directions=[],
                candidate_molecules=[],
                confidence="low"
            ))
        
        return insights
    
    def analyze_ideality(self) -> EvolutionInsight:
        """
        Apply Ideality analysis: move toward function with minimal resources.
        """
        prompt = """Apply TRIZ Ideality analysis to entrainer selection:

THE IDEAL ENTRAINER:
Level 1: Delivers separation without existing (no material needed)
Level 2: If it must exist, costs nothing
Level 3: If it costs something, delivers multiple functions
Level 4: If single function, has zero side effects
Level 5: If side effects exist, they are beneficial

CURRENT REALITY:
- Entrainers are physical materials with cost
- They require regeneration energy
- They have safety/environmental impacts
- They're single-purpose

QUESTIONS:
1. How can we APPROACH ideality without reaching it?
2. What molecular characteristics minimize material usage?
3. What molecules could serve multiple purposes (entrainer + fuel additive)?
4. What degradation products would be beneficial or neutral?

Suggest specific molecular strategies that move toward ideality."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return EvolutionInsight(
                tool_used="ideality",
                temporal_position="future",
                hierarchy_level="subsystem",
                insight=response_text[:1000],
                molecular_implications=self._extract_implications(response_text),
                suggested_directions=self._extract_directions(response_text),
                candidate_molecules=[],
                confidence="medium"
            )
            
        except Exception as e:
            return EvolutionInsight(
                tool_used="ideality",
                temporal_position="future",
                hierarchy_level="subsystem",
                insight=f"Error: {e}",
                molecular_implications=[],
                suggested_directions=[],
                candidate_molecules=[],
                confidence="low"
            )
    
    def analyze_trimming(self) -> EvolutionInsight:
        """
        Apply Trimming analysis: what can we remove while preserving function?
        """
        prompt = """Apply TRIZ Trimming to entrainer molecule design:

TRIMMING PRINCIPLE: Remove components while transferring their function 
to remaining components or the supersystem.

CURRENT ENTRAINER SYSTEM:
- Polar functional groups (for water affinity)
- Alkyl chains (for volatility control)
- H-bond donors/acceptors
- Molecular size/weight

TRIMMING QUESTIONS:
1. What molecular features are TRULY essential vs. traditionally included?
2. Can the column packing take over some entrainer functions?
3. Can process conditions replace some molecular features?
4. What is the MINIMUM molecular structure that delivers function?

Goal: Identify simplified molecular architectures that preserve function.

Suggest molecular structures that represent "trimmed" entrainers - 
minimum effective structures."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return EvolutionInsight(
                tool_used="trimming",
                temporal_position="present",
                hierarchy_level="subsystem",
                insight=response_text[:1000],
                molecular_implications=self._extract_implications(response_text),
                suggested_directions=self._extract_directions(response_text),
                candidate_molecules=[],
                confidence="medium"
            )
            
        except Exception as e:
            return EvolutionInsight(
                tool_used="trimming",
                temporal_position="present",
                hierarchy_level="subsystem",
                insight=f"Error: {e}",
                molecular_implications=[],
                suggested_directions=[],
                candidate_molecules=[],
                confidence="low"
            )
    
    def _extract_implications(self, text: str) -> List[str]:
        """Extract molecular implications from LLM response."""
        implications = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in 
                   ['molecular', 'structure', 'functional', 'feature', 'group']):
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    implications.append(line.strip().lstrip('-•').strip())
        
        return implications[:10]  # Limit
    
    def _extract_directions(self, text: str) -> List[str]:
        """Extract suggested research directions."""
        directions = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in 
                   ['suggest', 'recommend', 'direction', 'future', 'explore']):
                if len(line.strip()) > 20:
                    directions.append(line.strip())
        
        return directions[:5]
    
    def run_full_evolution_analysis(self) -> List[EvolutionInsight]:
        """Run all evolution-based analyses."""
        results = []
        
        results.extend(self.analyze_nine_windows())
        results.append(self.analyze_ideality())
        results.append(self.analyze_trimming())
        
        return results
```

### Agent 3: Su-Field and Standard Solutions Agent

```python
# src/triz/agents/sufield_agent.py
"""
Phase II-B: TRIZ Su-Field (Substance-Field) Analysis Agent

Su-Field models systems as interactions between substances via fields.
The 76 Standard Solutions provide patterns for improving these interactions.

For molecular design, we interpret:
- Substances: Entrainer, water, ethanol, column materials
- Fields: Hydrogen bonding, electrostatic, van der Waals, thermal

References:
- Salamatov, Y. "TRIZ: The Right Solution at the Right Time"
- The 76 Standard Solutions (grouped into 5 classes)
  [NEEDS VERIFICATION: Check standard TRIZ resources for current formulation]
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SuFieldModel:
    """Substance-Field model representation"""
    substances: List[str]
    fields: List[str]
    interaction_type: str  # "effective", "insufficient", "harmful"
    desired_outcome: str
    
@dataclass
class SuFieldInsight:
    """Output from Su-Field analysis"""
    model: SuFieldModel
    standard_solution_class: int  # 1-5
    standard_solution_applied: str
    molecular_interpretation: str
    suggested_modifications: List[str]
    candidate_molecules: List[Dict]
    confidence: str

class SuFieldAgent:
    """
    Agent that applies Su-Field Analysis and Standard Solutions
    to molecule selection.
    
    The 5 Classes of Standard Solutions:
    1. Building/destroying Su-Field models (13 solutions)
    2. Developing Su-Field models (23 solutions)
    3. Transition to supersystem/micro-level (6 solutions)
    4. Standards for detection and measurement (17 solutions)
    5. Standards for applying standards (17 solutions)
    
    Most relevant for entrainer selection: Classes 1, 2, and 3.
    """
    
    # Su-Field models for ethanol-water separation
    SEPARATION_SUFIELD_MODELS = [
        SuFieldModel(
            substances=["Water", "Ethanol", "Entrainer"],
            fields=["Hydrogen bonding"],
            interaction_type="insufficient",
            desired_outcome="Entrainer preferentially bonds to water over ethanol"
        ),
        SuFieldModel(
            substances=["Entrainer", "Distillation column"],
            fields=["Thermal", "Mass transfer"],
            interaction_type="harmful",
            desired_outcome="Minimal entrainer loss, efficient heat transfer"
        ),
        SuFieldModel(
            substances=["Entrainer", "Environment"],
            fields=["Chemical (toxicity)"],
            interaction_type="harmful",
            desired_outcome="Zero toxicity, full biodegradability"
        ),
    ]
    
    # Relevant Standard Solutions (simplified)
    RELEVANT_STANDARDS = {
        # Class 1: Building/destroying models
        "1.1.1": {
            "name": "Add S3 to incomplete model",
            "description": "If interaction is insufficient, add a third substance",
            "molecular_interpretation": "Add co-solvent or additive to enhance selectivity"
        },
        "1.1.2": {
            "name": "Add modified S3",
            "description": "Add a modified version of existing substance",
            "molecular_interpretation": "Add modified entrainer (functionalized version)"
        },
        "1.2.1": {
            "name": "Introduce ferromagnetic substance",
            "description": "Add ferromagnetic substance for magnetic field interaction",
            "molecular_interpretation": "Paramagnetic ILs for magnetic recovery [NEEDS VERIFICATION]"
        },
        # Class 2: Developing models
        "2.1.1": {
            "name": "Chain Su-Field",
            "description": "Create chain of substances with progressive field interaction",
            "molecular_interpretation": "Use molecular cascade: entrainer → intermediate → water"
        },
        "2.2.1": {
            "name": "Segmentation",
            "description": "Segment one substance to increase field interaction area",
            "molecular_interpretation": "Use smaller/more polar functional groups distributed across molecule"
        },
        # Class 3: Transition to supersystem/micro
        "3.1.1": {
            "name": "Transition to bi-system",
            "description": "Combine with another system",
            "molecular_interpretation": "Binary entrainer mixtures, DES systems"
        },
        "3.2.1": {
            "name": "Transition to micro-level",
            "description": "Move to smaller scale for field interaction",
            "molecular_interpretation": "Nanoscale effects: self-assembly, nano-segregation"
        },
    }
    
    SYSTEM_PROMPT = """You are a TRIZ expert applying Substance-Field (Su-Field) 
analysis to molecular design for entrainer selection.

Su-Field modeling views systems as substances (S1, S2, S3...) interacting via 
fields (F: mechanical, thermal, chemical, magnetic, etc.).

For entrainer selection:
SUBSTANCES:
- S1: Water (to be removed)
- S2: Ethanol (product to purify)
- S3: Entrainer (our design target)
- S4: Column internals (context)

FIELDS:
- F1: Hydrogen bonding
- F2: Electrostatic interactions
- F3: Van der Waals forces
- F4: Thermal energy

Your task: Apply Standard Solutions to improve the S1-S2-S3 interaction system.

IMPORTANT:
- Translate abstract Standard Solutions into CONCRETE molecular features
- Consider how molecular modifications change the "field" interactions
- Be specific about functional groups and structural features"""

    def __init__(self, llm_client, molecule_database):
        self.llm = llm_client
        self.db = molecule_database
    
    def analyze_sufield_model(
        self, 
        model: SuFieldModel
    ) -> List[SuFieldInsight]:
        """
        Analyze a Su-Field model and apply relevant Standard Solutions.
        """
        insights = []
        
        # Determine which standard solutions apply
        if model.interaction_type == "insufficient":
            applicable_standards = ["1.1.1", "1.1.2", "2.1.1", "2.2.1", "3.1.1"]
        elif model.interaction_type == "harmful":
            applicable_standards = ["1.2.1", "3.2.1"]  # Transform or eliminate
        else:
            applicable_standards = list(self.RELEVANT_STANDARDS.keys())
        
        for std_id in applicable_standards:
            std = self.RELEVANT_STANDARDS.get(std_id, {})
            
            prompt = f"""Apply Standard Solution {std_id} to this Su-Field model:

MODEL:
Substances: {', '.join(model.substances)}
Fields: {', '.join(model.fields)}
Current interaction: {model.interaction_type}
Desired outcome: {model.desired_outcome}

STANDARD SOLUTION {std_id}: {std.get('name', 'Unknown')}
Description: {std.get('description', 'N/A')}
Molecular interpretation hint: {std.get('molecular_interpretation', 'N/A')}

How can we apply this standard solution to select or modify entrainer molecules?
Be specific about:
1. What molecular features would implement this solution?
2. What functional groups or structural modifications?
3. Example molecules or molecular classes that embody this?"""

            try:
                response = self.llm.generate(prompt)
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                insights.append(SuFieldInsight(
                    model=model,
                    standard_solution_class=int(std_id[0]),
                    standard_solution_applied=f"{std_id}: {std.get('name', 'Unknown')}",
                    molecular_interpretation=response_text[:800],
                    suggested_modifications=self._extract_modifications(response_text),
                    candidate_molecules=[],
                    confidence="medium"
                ))
                
            except Exception as e:
                insights.append(SuFieldInsight(
                    model=model,
                    standard_solution_class=int(std_id[0]),
                    standard_solution_applied=f"{std_id}: Error",
                    molecular_interpretation=f"Error: {e}",
                    suggested_modifications=[],
                    candidate_molecules=[],
                    confidence="low"
                ))
        
        return insights
    
    def analyze_smart_little_people(self) -> Dict:
        """
        Apply Smart Little People (SLP) modeling.
        
        SLP: Imagine the system as tiny intelligent beings. 
        What would they need to do to achieve the desired function?
        """
        prompt = """Apply the Smart Little People (SLP) technique:

Imagine the entrainer molecules as tiny intelligent beings in the distillation 
column. They can sense their environment and make decisions.

SCENARIO:
The "entrainer people" encounter water molecules and ethanol molecules.
They need to:
1. Recognize water vs ethanol
2. Grab water preferentially
3. Carry water away from ethanol
4. Release water at the right time
5. Return for more (regeneration)

QUESTIONS:
1. What "tools" (functional groups) would these little people need?
2. What "sensors" (recognition sites) would help them distinguish water?
3. What "muscles" (interaction mechanisms) would they use to grab water?
4. What would trigger them to release water?

Translate this anthropomorphic model into concrete molecular features and 
suggest molecular classes that behave as these "smart" molecules."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "technique": "Smart Little People (SLP)",
                "analysis": response_text,
                "molecular_insights": self._extract_modifications(response_text),
                "confidence": "medium"  # Heuristic technique
            }
            
        except Exception as e:
            return {
                "technique": "Smart Little People (SLP)",
                "analysis": f"Error: {e}",
                "molecular_insights": [],
                "confidence": "low"
            }
    
    def analyze_effects_database(self) -> Dict:
        """
        Apply Effects Database concept.
        
        In TRIZ, the Effects Database maps functions to physical/chemical effects
        that can achieve them.
        
        NOTE: A full effects database is outside scope. This is a simplified
        mapping for separation science.
        """
        # Simplified effects mapping for separation
        separation_effects = {
            "selective_binding": [
                {"effect": "Hydrogen bonding specificity", 
                 "molecular_feature": "H-bond donors adjacent to acceptors"},
                {"effect": "Ionic interaction", 
                 "molecular_feature": "Charged groups for electrostatic binding"},
                {"effect": "Coordination chemistry", 
                 "molecular_feature": "Lewis acid/base sites"},
            ],
            "volatility_control": [
                {"effect": "Molecular weight", 
                 "molecular_feature": "Higher MW, lower vapor pressure"},
                {"effect": "Intermolecular association", 
                 "molecular_feature": "Self-H-bonding groups"},
                {"effect": "Ionic character", 
                 "molecular_feature": "Charged species have negligible VP"},
            ],
            "easy_regeneration": [
                {"effect": "Temperature-dependent H-bonding", 
                 "molecular_feature": "H-bonds that weaken significantly with T"},
                {"effect": "Phase transition", 
                 "molecular_feature": "LCST/UCST behavior"},
                {"effect": "Stripping volatility", 
                 "molecular_feature": "Large VP difference from water at high T"},
            ],
            "low_toxicity": [
                {"effect": "Biogenic origin", 
                 "molecular_feature": "Natural product derivatives"},
                {"effect": "Rapid biodegradation", 
                 "molecular_feature": "Ester/amide linkages"},
                {"effect": "Low membrane permeability", 
                 "molecular_feature": "Large, polar molecules"},
            ],
        }
        
        return {
            "technique": "Effects Database (Scientific Effects)",
            "effects_mapping": separation_effects,
            "note": "This is a simplified mapping. Full TRIZ effects databases contain "
                    "thousands of physical/chemical/biological effects. [NEEDS VERIFICATION: "
                    "Check if specialized chemical effects databases exist for TRIZ]"
        }
    
    def _extract_modifications(self, text: str) -> List[str]:
        """Extract suggested molecular modifications from text."""
        modifications = []
        lines = text.split('\n')
        
        for line in lines:
            line_strip = line.strip()
            if line_strip.startswith('-') or line_strip.startswith('•'):
                content = line_strip.lstrip('-•').strip()
                if len(content) > 10 and len(content) < 200:
                    modifications.append(content)
        
        return modifications[:10]
    
    def run_full_sufield_analysis(self) -> Dict:
        """Run complete Su-Field based analysis."""
        results = {
            "sufield_insights": [],
            "slp_analysis": None,
            "effects_database": None
        }
        
        # Analyze each Su-Field model
        for model in self.SEPARATION_SUFIELD_MODELS:
            insights = self.analyze_sufield_model(model)
            results["sufield_insights"].extend(insights)
        
        # Apply SLP
        results["slp_analysis"] = self.analyze_smart_little_people()
        
        # Get effects mapping
        results["effects_database"] = self.analyze_effects_database()
        
        return results
```

### Agent 4: First Principles Agent

```python
# src/triz/agents/first_principles_agent.py
"""
Phase II-B: First Principles Thinking Agent

This agent applies ab initio reasoning to molecule selection:
- Start from fundamental physics/chemistry
- Derive requirements from basic thermodynamic principles
- Avoid assumptions from existing solutions

This complements TRIZ by grounding innovation in physical law.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class FirstPrinciplesInsight:
    """Output from first principles analysis"""
    principle_category: str  # "thermodynamic", "kinetic", "structural"
    fundamental_law: str
    derived_requirement: str
    molecular_implication: str
    suggested_features: List[str]
    confidence: str

class FirstPrinciplesAgent:
    """
    Agent that derives molecular requirements from fundamental principles.
    
    Key principles for separation:
    1. Thermodynamics: ΔG = ΔH - TΔS (free energy determines spontaneity)
    2. Phase equilibria: Raoult's Law, activity coefficients
    3. Mass transfer: Diffusion, film theory
    4. Molecular recognition: Lock-key, H-bonding geometry
    """
    
    FUNDAMENTAL_PRINCIPLES = [
        {
            "category": "thermodynamic",
            "principle": "Relative Volatility Enhancement",
            "law": "α = (γ_ethanol * P°_ethanol) / (γ_water * P°_water)",
            "explanation": """
            Relative volatility (α) determines separation ease. 
            For water removal: need α_ethanol/water > 1 with entrainer.
            Entrainer must increase γ_water (water activity coefficient) 
            more than γ_ethanol.
            """,
            "molecular_requirement": """
            Entrainer must interact MORE strongly with water than ethanol.
            Water has: 2 H-bond donors, 2 H-bond acceptors, high polarity.
            Ethanol has: 1 H-bond donor, 1 H-bond acceptor, amphiphilic.
            Entrainer needs features that preferentially match water's pattern.
            """
        },
        {
            "category": "thermodynamic",
            "principle": "Azeotrope Breaking",
            "law": "Azeotrope exists when vapor and liquid compositions equal",
            "explanation": """
            Ethanol-water azeotrope at ~95.6% ethanol exists because 
            γ_ethanol and γ_water curves intersect at this composition.
            Entrainer must shift the curves to eliminate this intersection.
            """,
            "molecular_requirement": """
            Entrainer must NOT form new azeotropes with either component.
            This constrains boiling point (should be >150°C) and 
            interaction pattern (avoid symmetric H-bonding with both).
            """
        },
        {
            "category": "kinetic",
            "principle": "Mass Transfer Efficiency",
            "law": "k_L = D / δ (mass transfer coefficient)",
            "explanation": """
            Separation rate depends on how fast molecules move between phases.
            Viscous entrainers slow diffusion (lower D).
            Thick films (high δ) also reduce transfer.
            """,
            "molecular_requirement": """
            Entrainer should have: 
            - Low viscosity (< 10 cP at operating T)
            - No excessive film-forming tendency
            - Moderate molecular size (too large = slow diffusion)
            """
        },
        {
            "category": "structural",
            "principle": "Hydrogen Bond Complementarity",
            "law": "H-bond strength depends on geometry and distance",
            "explanation": """
            Water forms tetrahedral H-bond network.
            Ethanol forms linear H-bond chains.
            Entrainer geometry determines which network it disrupts.
            """,
            "molecular_requirement": """
            Entrainer should have H-bond acceptor pattern that 
            matches water's tetrahedral arrangement better than 
            ethanol's linear arrangement.
            1,2-diols (glycols) can form water-like local structure.
            """
        },
    ]
    
    SYSTEM_PROMPT = """You are a physical chemist applying first principles 
reasoning to entrainer molecule selection.

DO NOT rely on "what has worked before" - derive requirements from 
fundamental physics and chemistry.

Start from:
1. Thermodynamic laws (ΔG, equilibrium, activity coefficients)
2. Molecular physics (intermolecular forces, geometry)
3. Transport phenomena (diffusion, viscosity)

Your goal: Derive molecular structural requirements that MUST exist 
for effective separation, based purely on physical law.

Be rigorous: cite specific physical principles for each requirement."""

    def __init__(self, llm_client, molecule_database):
        self.llm = llm_client
        self.db = molecule_database
    
    def derive_requirements_from_principles(self) -> List[FirstPrinciplesInsight]:
        """
        For each fundamental principle, derive molecular requirements.
        """
        insights = []
        
        for principle in self.FUNDAMENTAL_PRINCIPLES:
            prompt = f"""Apply first principles analysis:

PRINCIPLE: {principle['principle']}
PHYSICAL LAW: {principle['law']}

EXPLANATION:
{principle['explanation']}

Based on this fundamental principle, derive SPECIFIC molecular features 
that an entrainer MUST have for effective ethanol-water separation.

Be specific:
1. What functional groups are required?
2. What structural arrangements?
3. What property ranges (MW, polarity, H-bond count)?
4. Any features that would VIOLATE this principle?

Ground every requirement in the physical law stated above."""

            try:
                response = self.llm.generate(prompt)
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                insights.append(FirstPrinciplesInsight(
                    principle_category=principle['category'],
                    fundamental_law=principle['law'],
                    derived_requirement=principle['molecular_requirement'],
                    molecular_implication=response_text[:800],
                    suggested_features=self._extract_features(response_text),
                    confidence="high"  # Grounded in physics
                ))
                
            except Exception as e:
                insights.append(FirstPrinciplesInsight(
                    principle_category=principle['category'],
                    fundamental_law=principle['law'],
                    derived_requirement=principle['molecular_requirement'],
                    molecular_implication=f"Error: {e}",
                    suggested_features=[],
                    confidence="low"
                ))
        
        return insights
    
    def derive_from_activity_coefficients(self) -> Dict:
        """
        Specific analysis based on activity coefficient theory.
        
        This is the core thermodynamic framework for entrainer selection.
        
        Reference: UNIFAC, NRTL models for activity coefficients
        """
        prompt = """Apply activity coefficient theory to derive entrainer requirements:

THEORETICAL FRAMEWORK:
Activity coefficient γ describes non-ideal mixing behavior.
γ > 1: positive deviation (molecules "dislike" mixing)
γ < 1: negative deviation (favorable mixing)

FOR ETHANOL-WATER SEPARATION:
We want: γ_water (in entrainer-rich phase) >> γ_ethanol (in entrainer-rich phase)
This makes water "want to leave" the liquid phase more than ethanol.

QUESTION:
What molecular features create high γ_water but low γ_ethanol?

Consider:
1. UNIFAC group contributions
2. H-bond donor/acceptor balance
3. Dispersion interactions
4. Molecular size effects

Provide specific molecular features that would achieve this activity 
coefficient pattern, grounded in UNIFAC or similar theory.

[NOTE: You may reference UNIFAC group contributions, but do not invent 
specific numerical parameters without citing a source.]"""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "analysis_type": "Activity Coefficient Derivation",
                "theoretical_basis": "UNIFAC/NRTL activity coefficient models",
                "analysis": response_text,
                "molecular_features": self._extract_features(response_text),
                "confidence": "medium",  # UNIFAC is approximate
                "verification_note": "UNIFAC predictions should be verified against experimental VLE data where available"
            }
            
        except Exception as e:
            return {
                "analysis_type": "Activity Coefficient Derivation",
                "error": str(e),
                "confidence": "low"
            }
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract molecular features from analysis text."""
        features = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in 
                   ['must have', 'require', 'need', 'should contain', 'feature']):
                if line.strip().startswith(('-', '•', '*')):
                    features.append(line.strip().lstrip('-•*').strip())
                elif len(line.strip()) > 20:
                    features.append(line.strip())
        
        return features[:10]
    
    def run_full_first_principles_analysis(self) -> Dict:
        """Run complete first principles analysis."""
        return {
            "derived_requirements": self.derive_requirements_from_principles(),
            "activity_coefficient_analysis": self.derive_from_activity_coefficients()
        }
```

### Agent 5: Inverse Design Agent

```python
# src/triz/agents/inverse_design_agent.py
"""
Phase II-B: Inverse Design Agent

Traditional approach: Molecule → Properties (forward problem)
Inverse design: Desired Properties → Molecule (reverse problem)

This agent specifies target property profiles and searches for matching molecules.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PropertyTarget:
    """Target property specification"""
    property_name: str
    target_value: float
    tolerance: float  # +/- range
    unit: str
    priority: str  # "required", "important", "nice_to_have"
    rationale: str

@dataclass
class InverseDesignResult:
    """Result from inverse design search"""
    property_targets: List[PropertyTarget]
    matching_molecules: List[Dict]
    partial_matches: List[Dict]
    design_insights: str

class InverseDesignAgent:
    """
    Agent that applies inverse design thinking.
    
    Workflow:
    1. Define target property profile from separation requirements
    2. Search molecular databases for matches
    3. Identify near-matches for structural modification
    4. Use generative AI to propose novel structures (if appropriate)
    """
    
    # Property targets derived from separation requirements
    # Values based on general separation science - [VERIFY with specific literature]
    DEFAULT_PROPERTY_TARGETS = [
        PropertyTarget(
            property_name="Boiling Point",
            target_value=180.0,
            tolerance=30.0,
            unit="°C",
            priority="required",
            rationale="Must be >ethanol BP (78°C) by significant margin for easy separation"
        ),
        PropertyTarget(
            property_name="Molecular Weight",
            target_value=150.0,
            tolerance=50.0,
            unit="g/mol",
            priority="important",
            rationale="Large enough for low VP, small enough for good diffusion"
        ),
        PropertyTarget(
            property_name="H-Bond Acceptors",
            target_value=4.0,
            tolerance=2.0,
            unit="count",
            priority="required",
            rationale="Multiple acceptors for water interaction"
        ),
        PropertyTarget(
            property_name="H-Bond Donors",
            target_value=2.0,
            tolerance=1.0,
            unit="count",
            priority="important",
            rationale="Donors for H-bond network participation"
        ),
        PropertyTarget(
            property_name="LogP",
            target_value=-0.5,
            tolerance=1.0,
            unit="dimensionless",
            priority="important",
            rationale="Slightly hydrophilic for water affinity"
        ),
        PropertyTarget(
            property_name="TPSA",
            target_value=60.0,
            tolerance=20.0,
            unit="Å²",
            priority="important",
            rationale="Moderate polar surface area for water interaction"
        ),
        # Safety targets
        PropertyTarget(
            property_name="Flash Point",
            target_value=100.0,
            tolerance=40.0,
            unit="°C",
            priority="required",
            rationale="High flash point for reduced flammability"
        ),
    ]
    
    def __init__(self, llm_client, molecule_database, property_calculator=None):
        """
        Args:
            llm_client: LLM for reasoning
            molecule_database: Database with molecular properties
            property_calculator: Optional RDKit-based property calculator
        """
        self.llm = llm_client
        self.db = molecule_database
        self.prop_calc = property_calculator
    
    def define_target_profile(
        self, 
        override_targets: Optional[List[PropertyTarget]] = None
    ) -> List[PropertyTarget]:
        """
        Define or refine the target property profile.
        """
        if override_targets:
            return override_targets
        return self.DEFAULT_PROPERTY_TARGETS
    
    def search_by_properties(
        self,
        targets: List[PropertyTarget],
        max_results: int = 50
    ) -> InverseDesignResult:
        """
        Search molecule database for compounds matching target profile.
        
        This is a template - actual implementation depends on your database.
        """
        # Build query from targets
        required_targets = [t for t in targets if t.priority == "required"]
        important_targets = [t for t in targets if t.priority == "important"]
        
        # Placeholder for actual database query
        # In production, implement actual property-based search
        
        query_description = "Searching for molecules with:\n"
        for t in required_targets:
            query_description += f"  - {t.property_name}: {t.target_value} ± {t.tolerance} {t.unit}\n"
        
        return InverseDesignResult(
            property_targets=targets,
            matching_molecules=[],  # Populate from actual search
            partial_matches=[],
            design_insights=query_description
        )
    
    def propose_novel_structures(
        self,
        targets: List[PropertyTarget],
        seed_molecules: Optional[List[str]] = None
    ) -> Dict:
        """
        Use LLM to propose novel molecular structures meeting target profile.
        
        IMPORTANT: LLM-proposed structures MUST be validated:
        1. Check SMILES validity with RDKit
        2. Verify predicted properties match targets
        3. Verify chemical stability/synthesizability
        """
        target_summary = "\n".join([
            f"- {t.property_name}: {t.target_value} ± {t.tolerance} {t.unit} [{t.priority}]"
            for t in targets
        ])
        
        seed_context = ""
        if seed_molecules:
            seed_context = f"\nStarting from these seed structures:\n" + \
                          "\n".join([f"- {s}" for s in seed_molecules[:5]])
        
        prompt = f"""Design novel molecules meeting this target profile for 
ethanol-water separation entrainer:

TARGET PROPERTIES:
{target_summary}

CONSTRAINTS:
- Must be chemically stable at temperatures up to 200°C
- Should be synthetically accessible (not exotic chemistry)
- Prefer molecules with known synthesis routes or close analogs
{seed_context}

For each proposed molecule, provide:
1. SMILES string (valid, canonical)
2. Common name (if known) or systematic name
3. Why it meets the targets
4. Any concerns or uncertainties

IMPORTANT: Only propose molecules you are confident are chemically valid.
If uncertain about a structure, mark it with [NEEDS VERIFICATION].

Propose 3-5 novel or underexplored structures."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse proposed molecules
            proposals = self._parse_proposals(response_text)
            
            # Validate SMILES with RDKit (if available)
            validated = []
            for proposal in proposals:
                if self._validate_smiles(proposal.get('smiles', '')):
                    proposal['validated'] = True
                    validated.append(proposal)
                else:
                    proposal['validated'] = False
                    proposal['validation_note'] = "SMILES failed RDKit parsing"
                    validated.append(proposal)
            
            return {
                "proposed_molecules": validated,
                "raw_response": response_text,
                "note": "All proposals require experimental validation before use"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "proposed_molecules": []
            }
    
    def _parse_proposals(self, text: str) -> List[Dict]:
        """Parse LLM response for proposed molecules."""
        proposals = []
        current = {}
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'smiles' in line_lower and ':' in line:
                if current.get('smiles'):
                    proposals.append(current)
                    current = {}
                current['smiles'] = line.split(':', 1)[1].strip()
            elif 'name' in line_lower and ':' in line:
                current['name'] = line.split(':', 1)[1].strip()
            elif 'reason' in line_lower or 'why' in line_lower:
                current['rationale'] = line
        
        if current.get('smiles'):
            proposals.append(current)
        
        return proposals
    
    def _validate_smiles(self, smiles: str) -> bool:
        """Validate SMILES string with RDKit."""
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except ImportError:
            # RDKit not available
            return True  # Assume valid, note for manual verification
        except Exception:
            return False
    
    def run_inverse_design(self) -> Dict:
        """Run complete inverse design analysis."""
        targets = self.define_target_profile()
        
        return {
            "target_profile": [
                {
                    "property": t.property_name,
                    "target": t.target_value,
                    "tolerance": t.tolerance,
                    "unit": t.unit,
                    "priority": t.priority
                }
                for t in targets
            ],
            "database_search": self.search_by_properties(targets),
            "novel_proposals": self.propose_novel_structures(targets)
        }
```

### Agent 6: Bio-isosterism & Scaffold Hopping Agent

```python
# src/triz/agents/bioisostere_agent.py
"""
Phase II-B: Bio-isosterism & Scaffold Hopping Agent

Bio-isosteres: Functional groups with similar biological/physical effects
Scaffold hopping: Replacing core structure while maintaining activity

This is "lateral thinking" for molecular design - finding non-obvious analogs.

Reference:
- Meanwell, N. A. (2011). "Synopsis of Some Recent Tactical Application of 
  Bioisosteres in Drug Design" J. Med. Chem.
  [NEEDS VERIFICATION: Check if industrial solvent applications exist]
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class BioisostereMapping:
    """Mapping between functional groups with similar properties"""
    original_group: str
    bioisostere: str
    smarts_original: str
    smarts_replacement: str
    property_similarity: str  # What properties are preserved
    property_differences: str  # What changes
    example_original: str
    example_analog: str

class BioisostereAgent:
    """
    Agent that applies bio-isosterism and scaffold hopping to find
    non-obvious molecular analogs.
    
    Key insight: If a molecule has desirable properties but undesirable
    safety profile, we can replace problematic groups with safer bioisosteres.
    """
    
    # Common bioisosteric replacements relevant to entrainer design
    # Reference: General medicinal chemistry principles
    # [NEEDS VERIFICATION: Some may not preserve separation properties]
    BIOISOSTERE_MAPPINGS = [
        BioisostereMapping(
            original_group="Carboxylic acid (-COOH)",
            bioisostere="Tetrazole",
            smarts_original="[CX3](=O)[OX2H1]",
            smarts_replacement="c1nnn[nH]1",  # Tetrazole ring
            property_similarity="pKa, H-bond donor/acceptor",
            property_differences="Tetrazole more metabolically stable",
            example_original="Acetic acid",
            example_analog="5-methyl-1H-tetrazole"
        ),
        BioisostereMapping(
            original_group="Hydroxyl (-OH)",
            bioisostere="Thiol (-SH)",
            smarts_original="[OX2H]",
            smarts_replacement="[SX2H]",
            property_similarity="H-bond donor capacity",
            property_differences="Thiol is weaker H-bond, more lipophilic",
            example_original="Ethanol",
            example_analog="Ethanethiol"
        ),
        BioisostereMapping(
            original_group="Ether (-O-)",
            bioisostere="Thioether (-S-)",
            smarts_original="[OX2]([#6])[#6]",
            smarts_replacement="[SX2]([#6])[#6]",
            property_similarity="Molecular geometry",
            property_differences="Thioether larger, more polarizable",
            example_original="Diethyl ether",
            example_analog="Diethyl sulfide"
        ),
        BioisostereMapping(
            original_group="Amide (-CONH-)",
            bioisostere="Sulfonamide (-SO2NH-)",
            smarts_original="[CX3](=O)[NX3]",
            smarts_replacement="[SX4](=O)(=O)[NX3]",
            property_similarity="H-bond pattern, metabolic stability",
            property_differences="Sulfonamide more acidic, larger",
            example_original="Dimethylformamide",
            example_analog="Dimethylsulfamide"
        ),
        BioisostereMapping(
            original_group="Benzene ring",
            bioisostere="Pyridine ring",
            smarts_original="c1ccccc1",
            smarts_replacement="c1ccncc1",
            property_similarity="Aromatic, planar",
            property_differences="Pyridine is H-bond acceptor, more polar",
            example_original="Toluene (toxic)",
            example_analog="Picoline (less toxic)"
        ),
        BioisostereMapping(
            original_group="Ester (-COO-)",
            bioisostere="Oxadiazole",
            smarts_original="[CX3](=O)[OX2]",
            smarts_replacement="c1nnoc1",  # 1,2,4-oxadiazole
            property_similarity="H-bond acceptor pattern",
            property_differences="Oxadiazole resistant to hydrolysis",
            example_original="Ethyl acetate",
            example_analog="2,5-dimethyl-1,3,4-oxadiazole"
        ),
    ]
    
    SYSTEM_PROMPT = """You are an expert in medicinal chemistry applying 
bio-isosterism and scaffold hopping to industrial solvent design.

Bio-isosteres are functional groups that have similar physical or biological 
properties despite different chemical structures.

Scaffold hopping replaces the core structure of a molecule while maintaining 
its key properties.

Your goal: Find safer or more effective alternatives to known entrainers 
by systematic group replacement.

IMPORTANT:
- Not all medicinal chemistry bioisosteres work for separation applications
- Prioritize replacements that maintain H-bonding pattern and polarity
- Consider thermal stability for high-temperature operation
- Always note when a replacement might significantly change properties"""

    def __init__(self, llm_client, molecule_database):
        self.llm = llm_client
        self.db = molecule_database
    
    def find_safer_analogs(
        self, 
        problematic_molecule: Dict
    ) -> Dict:
        """
        Given a molecule with good separation properties but safety issues,
        find bioisosteric replacements that might be safer.
        
        Args:
            problematic_molecule: Dict with smiles, name, safety_concerns
        """
        smiles = problematic_molecule.get('smiles', '')
        name = problematic_molecule.get('name', 'Unknown')
        safety_issues = problematic_molecule.get('safety_concerns', [])
        
        prompt = f"""Find safer alternatives to this entrainer using bio-isosterism:

MOLECULE: {name}
SMILES: {smiles}
SAFETY CONCERNS: {', '.join(safety_issues)}

This molecule has good separation properties but unacceptable safety profile.

TASK: 
1. Identify which functional groups might cause the safety issues
2. Propose bioisosteric replacements that might reduce toxicity
3. Consider if the replacement would maintain separation properties

For each proposed analog:
- Provide SMILES
- Explain the replacement made
- Predict effect on separation properties
- Predict effect on safety

Only propose chemically valid structures. Mark uncertain proposals with 
[NEEDS VERIFICATION]."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "original_molecule": problematic_molecule,
                "analysis": response_text,
                "proposed_analogs": self._parse_analogs(response_text),
                "note": "All proposed analogs require experimental validation"
            }
            
        except Exception as e:
            return {
                "original_molecule": problematic_molecule,
                "error": str(e),
                "proposed_analogs": []
            }
    
    def scaffold_hop_from_template(
        self,
        template_smiles: str,
        template_name: str,
        desired_properties: List[str]
    ) -> Dict:
        """
        Perform scaffold hopping: keep key properties, change core structure.
        """
        prompt = f"""Perform scaffold hopping on this entrainer template:

TEMPLATE: {template_name}
SMILES: {template_smiles}

DESIRED PROPERTIES TO MAINTAIN:
{chr(10).join(['- ' + p for p in desired_properties])}

Scaffold hopping replaces the core structure while maintaining key functional 
groups and their spatial arrangement.

Propose 3-5 alternative scaffolds that could:
1. Maintain similar H-bonding pattern
2. Maintain similar polarity/size
3. Potentially improve one of: safety, stability, cost

For each proposal:
- New SMILES
- Name (if known) or description
- What scaffold was changed
- Expected effect on properties

Mark speculative proposals with [SPECULATIVE]."""

        try:
            response = self.llm.generate(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "template": {"smiles": template_smiles, "name": template_name},
                "desired_properties": desired_properties,
                "analysis": response_text,
                "scaffold_hops": self._parse_analogs(response_text)
            }
            
        except Exception as e:
            return {
                "template": {"smiles": template_smiles, "name": template_name},
                "error": str(e),
                "scaffold_hops": []
            }
    
    def apply_systematic_replacements(
        self,
        target_molecules: List[Dict]
    ) -> Dict:
        """
        Apply systematic bioisosteric replacements to a set of molecules.
        """
        results = {
            "replacements_attempted": 0,
            "valid_analogs": [],
            "failed_analogs": []
        }
        
        for mol in target_molecules:
            smiles = mol.get('smiles', '')
            
            for mapping in self.BIOISOSTERE_MAPPINGS:
                # Check if original group is present
                if self._contains_substructure(smiles, mapping.smarts_original):
                    # Attempt replacement
                    analog = self._apply_replacement(
                        smiles, 
                        mapping.smarts_original,
                        mapping.smarts_replacement
                    )
                    
                    if analog:
                        results["valid_analogs"].append({
                            "original": mol,
                            "replacement": mapping.bioisostere,
                            "analog_smiles": analog,
                            "property_note": mapping.property_differences
                        })
                    
                    results["replacements_attempted"] += 1
        
        return results
    
    def _contains_substructure(self, smiles: str, smarts: str) -> bool:
        """Check if molecule contains substructure."""
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            pattern = Chem.MolFromSmarts(smarts)
            if mol and pattern:
                return mol.HasSubstructMatch(pattern)
            return False
        except ImportError:
            return False
        except Exception:
            return False
    
    def _apply_replacement(
        self, 
        smiles: str, 
        smarts_orig: str, 
        smarts_new: str
    ) -> Optional[str]:
        """Apply substructure replacement."""
        # This is a simplified placeholder
        # Real implementation would use RDKit's AllChem.ReplaceSubstructs
        # [NEEDS IMPLEMENTATION with proper RDKit]
        return None
    
    def _parse_analogs(self, text: str) -> List[Dict]:
        """Parse LLM response for proposed analogs."""
        analogs = []
        current = {}
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'smiles' in line_lower and ':' in line:
                if current.get('smiles'):
                    analogs.append(current)
                    current = {}
                current['smiles'] = line.split(':', 1)[1].strip()
            elif 'name' in line_lower and ':' in line:
                current['name'] = line.split(':', 1)[1].strip()
            elif 'replacement' in line_lower or 'change' in line_lower:
                current['modification'] = line
        
        if current.get('smiles'):
            analogs.append(current)
        
        return analogs
    
    def run_bioisostere_analysis(
        self,
        problematic_molecules: List[Dict]
    ) -> Dict:
        """Run complete bioisosteric analysis on problematic molecules."""
        results = {
            "safer_analogs": [],
            "scaffold_hops": [],
            "systematic_replacements": None
        }
        
        for mol in problematic_molecules:
            analog_result = self.find_safer_analogs(mol)
            results["safer_analogs"].append(analog_result)
        
        # Example scaffold hop on ethylene glycol template
        results["scaffold_hops"].append(
            self.scaffold_hop_from_template(
                template_smiles="OCCO",
                template_name="Ethylene Glycol",
                desired_properties=[
                    "Two H-bond donors",
                    "Two H-bond acceptors",
                    "High polarity",
                    "Low volatility"
                ]
            )
        )
        
        return results
```

---

## Orchestrator and Synthesis Agent

```python
# src/triz/engine_b_orchestrator.py
"""
Phase II-B: Engine B Orchestrator

This orchestrates all TRIZ agents and synthesizes their outputs
into a final selection of 25-50 molecules.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime

@dataclass
class EngineAMolecule:
    """Reference to Engine A selection for overlap detection"""
    smiles: str
    name: str
    selection_rationale: str

@dataclass
class EngineBResult:
    """Final output from Engine B"""
    selected_molecules: List[Dict]
    directional_insights: List[str]
    engine_a_overlaps: List[str]  # SMILES that also appear in Engine A
    triz_techniques_used: List[str]
    confidence_assessment: Dict
    provenance: Dict  # Which agent contributed each molecule

class EngineBOrchestrator:
    """
    Orchestrates all TRIZ agents and synthesizes final selection.
    
    Workflow:
    1. Load Engine A results (for overlap detection)
    2. Run all TRIZ agents
    3. Collect molecular suggestions from each
    4. Apply ARIZ for complex contradictions (if needed)
    5. Synthesize and rank final selection
    6. Flag Engine A overlaps
    """
    
    def __init__(
        self,
        llm_client,
        molecule_database,
        engine_a_results_path: Optional[Path] = None
    ):
        self.llm = llm_client
        self.db = molecule_database
        
        # Load Engine A results for overlap detection
        self.engine_a_molecules: Set[str] = set()
        if engine_a_results_path and engine_a_results_path.exists():
            with open(engine_a_results_path) as f:
                engine_a_data = json.load(f)
                for mol in engine_a_data.get('molecules', []):
                    self.engine_a_molecules.add(mol.get('smiles', ''))
        
        # Initialize agents (lazy loading)
        self._contradiction_agent = None
        self._evolution_agent = None
        self._sufield_agent = None
        self._first_principles_agent = None
        self._inverse_design_agent = None
        self._bioisostere_agent = None
    
    @property
    def contradiction_agent(self):
        if self._contradiction_agent is None:
            from src.triz.agents.contradiction_agent import ContradictionAnalysisAgent
            self._contradiction_agent = ContradictionAnalysisAgent(
                self.llm, self.db
            )
        return self._contradiction_agent
    
    @property
    def evolution_agent(self):
        if self._evolution_agent is None:
            from src.triz.agents.evolution_agent import SystemEvolutionAgent
            self._evolution_agent = SystemEvolutionAgent(
                self.llm, self.db
            )
        return self._evolution_agent
    
    @property
    def sufield_agent(self):
        if self._sufield_agent is None:
            from src.triz.agents.sufield_agent import SuFieldAgent
            self._sufield_agent = SuFieldAgent(
                self.llm, self.db
            )
        return self._sufield_agent
    
    @property
    def first_principles_agent(self):
        if self._first_principles_agent is None:
            from src.triz.agents.first_principles_agent import FirstPrinciplesAgent
            self._first_principles_agent = FirstPrinciplesAgent(
                self.llm, self.db
            )
        return self._first_principles_agent
    
    @property
    def inverse_design_agent(self):
        if self._inverse_design_agent is None:
            from src.triz.agents.inverse_design_agent import InverseDesignAgent
            self._inverse_design_agent = InverseDesignAgent(
                self.llm, self.db
            )
        return self._inverse_design_agent
    
    @property
    def bioisostere_agent(self):
        if self._bioisostere_agent is None:
            from src.triz.agents.bioisostere_agent import BioisostereAgent
            self._bioisostere_agent = BioisostereAgent(
                self.llm, self.db
            )
        return self._bioisostere_agent
    
    def run_all_agents(self) -> Dict:
        """Run all TRIZ agents and collect results."""
        results = {
            "run_timestamp": datetime.now().isoformat(),
            "agents_results": {}
        }
        
        print("Running TRIZ agents...")
        
        # Agent 1: Contradiction Analysis
        print("  [1/6] Contradiction Analysis Agent...")
        try:
            results["agents_results"]["contradiction"] = {
                "insights": self.contradiction_agent.run_full_contradiction_analysis()
            }
        except Exception as e:
            results["agents_results"]["contradiction"] = {"error": str(e)}
        
        # Agent 2: System Evolution
        print("  [2/6] System Evolution Agent...")
        try:
            results["agents_results"]["evolution"] = \
                self.evolution_agent.run_full_evolution_analysis()
        except Exception as e:
            results["agents_results"]["evolution"] = {"error": str(e)}
        
        # Agent 3: Su-Field Analysis
        print("  [3/6] Su-Field Analysis Agent...")
        try:
            results["agents_results"]["sufield"] = \
                self.sufield_agent.run_full_sufield_analysis()
        except Exception as e:
            results["agents_results"]["sufield"] = {"error": str(e)}
        
        # Agent 4: First Principles
        print("  [4/6] First Principles Agent...")
        try:
            results["agents_results"]["first_principles"] = \
                self.first_principles_agent.run_full_first_principles_analysis()
        except Exception as e:
            results["agents_results"]["first_principles"] = {"error": str(e)}
        
        # Agent 5: Inverse Design
        print("  [5/6] Inverse Design Agent...")
        try:
            results["agents_results"]["inverse_design"] = \
                self.inverse_design_agent.run_inverse_design()
        except Exception as e:
            results["agents_results"]["inverse_design"] = {"error": str(e)}
        
        # Agent 6: Bio-isosterism (on problematic molecules if any)
        print("  [6/6] Bio-isosterism Agent...")
        try:
            # Example problematic molecules - these would come from database
            problematic = [
                {
                    "smiles": "c1ccccc1",
                    "name": "Benzene",
                    "safety_concerns": ["carcinogenic", "IARC Group 1"]
                }
            ]
            results["agents_results"]["bioisostere"] = \
                self.bioisostere_agent.run_bioisostere_analysis(problematic)
        except Exception as e:
            results["agents_results"]["bioisostere"] = {"error": str(e)}
        
        return results
    
    def synthesize_molecules(
        self, 
        agent_results: Dict,
        target_count: int = 50
    ) -> List[Dict]:
        """
        Synthesize all agent outputs into a ranked molecule list.
        
        This uses LLM reasoning to:
        1. Extract concrete molecule suggestions from each agent
        2. Score by number of agent "votes"
        3. Prioritize molecules with multiple supporting rationales
        """
        synthesis_prompt = f"""You are synthesizing the outputs of 6 TRIZ-based 
analysis agents for entrainer molecule selection.

AGENT OUTPUTS:
{json.dumps(agent_results, indent=2, default=str)[:8000]}  # Truncate for context

TASK:
From these analyses, identify the top {target_count} concrete molecular 
candidates or molecular classes for ethanol-water separation entrainers.

For each molecule/class:
1. SMILES (if specific molecule) or SMARTS pattern (if class)
2. Name
3. Which agents support this choice
4. Key properties/features mentioned
5. Any safety concerns flagged
6. Confidence score (1-10)

Prioritize molecules that:
- Are supported by multiple agents
- Resolve identified contradictions
- Align with first principles requirements
- Have favorable safety profile

Only include molecules with actual SMILES or well-defined molecular classes.
Do not include vague descriptions."""

        try:
            response = self.llm.generate(synthesis_prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse molecules from response
            molecules = self._parse_synthesized_molecules(response_text)
            
            return molecules[:target_count]
            
        except Exception as e:
            print(f"Synthesis error: {e}")
            return []
    
    def _parse_synthesized_molecules(self, text: str) -> List[Dict]:
        """Parse synthesized molecule list from LLM response."""
        molecules = []
        current = {}
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'smiles' in line_lower and ':' in line:
                if current.get('smiles'):
                    molecules.append(current)
                    current = {}
                current['smiles'] = line.split(':', 1)[1].strip()
            elif 'name' in line_lower and ':' in line:
                current['name'] = line.split(':', 1)[1].strip()
            elif 'confidence' in line_lower and ':' in line:
                try:
                    score = float(line.split(':')[1].strip().split('/')[0])
                    current['confidence'] = score / 10.0  # Normalize to 0-1
                except:
                    current['confidence'] = 0.5
            elif 'agent' in line_lower and ':' in line:
                current['supporting_agents'] = line.split(':', 1)[1].strip()
        
        if current.get('smiles'):
            molecules.append(current)
        
        return molecules
    
    def check_engine_a_overlap(
        self, 
        molecules: List[Dict]
    ) -> List[str]:
        """Identify molecules that overlap with Engine A selection."""
        overlaps = []
        
        for mol in molecules:
            smiles = mol.get('smiles', '')
            if smiles in self.engine_a_molecules:
                overlaps.append(smiles)
                mol['engine_a_overlap'] = True
            else:
                mol['engine_a_overlap'] = False
        
        return overlaps
    
    def extract_directional_insights(
        self, 
        agent_results: Dict
    ) -> List[str]:
        """
        Extract non-molecule insights (research directions, trends, etc.)
        that are valuable even without specific molecular candidates.
        """
        insights = []
        
        # From evolution agent: future trends
        evolution_data = agent_results.get("agents_results", {}).get("evolution", {})
        if isinstance(evolution_data, list):
            for item in evolution_data:
                if hasattr(item, 'suggested_directions'):
                    insights.extend(item.suggested_directions)
        
        # From first principles: derived requirements
        fp_data = agent_results.get("agents_results", {}).get("first_principles", {})
        if isinstance(fp_data, dict):
            for req in fp_data.get("derived_requirements", []):
                if hasattr(req, 'molecular_implication'):
                    insights.append(f"First Principles: {req.molecular_implication[:200]}")
        
        return insights[:20]  # Limit to top 20 insights
    
    def run_engine_b(self, target_molecules: int = 50) -> EngineBResult:
        """
        Run complete Engine B pipeline.
        
        Returns:
            EngineBResult with selected molecules and insights
        """
        print("="*60)
        print("ENGINE B: TRIZ-POWERED CONSULTATION MODULE")
        print("="*60)
        
        # Step 1: Run all agents
        agent_results = self.run_all_agents()
        
        # Step 2: Synthesize molecules
        print("\nSynthesizing molecule selections...")
        molecules = self.synthesize_molecules(agent_results, target_molecules)
        
        # Step 3: Check Engine A overlaps
        print("Checking for Engine A overlaps...")
        overlaps = self.check_engine_a_overlap(molecules)
        
        # Step 4: Extract directional insights
        print("Extracting directional insights...")
        insights = self.extract_directional_insights(agent_results)
        
        # Step 5: Compile final result
        result = EngineBResult(
            selected_molecules=molecules,
            directional_insights=insights,
            engine_a_overlaps=overlaps,
            triz_techniques_used=[
                "Contradiction Analysis (Technical & Physical)",
                "40 Inventive Principles",
                "Separation Principles",
                "9 Windows System Operator",
                "Ideality Analysis",
                "Trimming",
                "Su-Field Analysis",
                "76 Standard Solutions (selected)",
                "Smart Little People",
                "Effects Database",
                "First Principles Derivation",
                "Inverse Design",
                "Bio-isosterism & Scaffold Hopping"
            ],
            confidence_assessment={
                "high_confidence_molecules": len([m for m in molecules if m.get('confidence', 0) > 0.7]),
                "medium_confidence_molecules": len([m for m in molecules if 0.4 <= m.get('confidence', 0) <= 0.7]),
                "low_confidence_molecules": len([m for m in molecules if m.get('confidence', 0) < 0.4]),
            },
            provenance={"agent_results": agent_results}
        )
        
        print(f"\n{'='*60}")
        print(f"ENGINE B COMPLETE")
        print(f"Selected: {len(molecules)} molecules")
        print(f"Engine A overlaps: {len(overlaps)} (prioritize these!)")
        print(f"Directional insights: {len(insights)}")
        print(f"{'='*60}")
        
        return result
    
    def export_results(
        self, 
        result: EngineBResult, 
        output_path: Path
    ) -> Path:
        """Export Engine B results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "engine": "B",
            "methodology": "TRIZ-Powered Consultation",
            "selected_molecules": result.selected_molecules,
            "directional_insights": result.directional_insights,
            "engine_a_overlaps": result.engine_a_overlaps,
            "triz_techniques_used": result.triz_techniques_used,
            "confidence_assessment": result.confidence_assessment,
            # Don't export full provenance to save space
            "provenance_summary": {
                "agents_run": list(result.provenance.get("agent_results", {}).keys())
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return output_path


# Main execution function
def run_engine_b_pipeline(
    engine_a_results: Optional[Path] = None,
    output_path: Optional[Path] = None
):
    """
    Main entry point for Engine B.
    
    Args:
        engine_a_results: Path to Engine A results JSON (for overlap detection)
        output_path: Where to save Engine B results
    """
    # Initialize LLM client
    # [VERIFY: Current API initialization]
    import google.generativeai as genai
    import os
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Set GOOGLE_API_KEY environment variable")
    
    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel("gemini-1.5-pro")
    
    # Mock database for template (replace with actual)
    mock_db = None
    
    # Initialize orchestrator
    orchestrator = EngineBOrchestrator(
        llm_client=llm,
        molecule_database=mock_db,
        engine_a_results_path=engine_a_results
    )
    
    # Run pipeline
    result = orchestrator.run_engine_b(target_molecules=50)
    
    # Export
    if output_path is None:
        output_path = Path("data/engine_b_results.json")
    
    orchestrator.export_results(result, output_path)
    print(f"\nResults saved to: {output_path}")
    
    return result


if __name__ == "__main__":
    run_engine_b_pipeline()
```

---

## Code Artifacts Summary

### Project Structure Addition

```
src/
├── triz/
│   ├── __init__.py
│   ├── domain_mapping.py          # TRIZ → Chemistry translations
│   ├── engine_b_orchestrator.py   # Main orchestrator
│   └── agents/
│       ├── __init__.py
│       ├── contradiction_agent.py
│       ├── evolution_agent.py
│       ├── sufield_agent.py
│       ├── first_principles_agent.py
│       ├── inverse_design_agent.py
│       └── bioisostere_agent.py
```

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `10_triz_domain_mapping.ipynb` | Explore TRIZ-chemistry translations interactively |
| `11_contradiction_analysis.ipynb` | Test contradiction analysis agent |
| `12_evolution_analysis.ipynb` | Test 9 Windows and Ideality agents |
| `13_sufield_analysis.ipynb` | Test Su-Field and Standard Solutions |
| `14_first_principles.ipynb` | Test first principles derivations |
| `15_inverse_design.ipynb` | Test property-based molecule search |
| `16_bioisostere_search.ipynb` | Test scaffold hopping |
| `17_engine_b_integration.ipynb` | Full Engine B pipeline |

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | Note |
|------|-----------------|------|
| TRIZ 40 Principles interpretation | Review against TRIZ literature | Molecular interpretations are novel applications |
| Su-Field applicability | Consult TRIZ expert if available | Not standard TRIZ application domain |
| Bioisostere mappings | Verify with medicinal chemistry sources | May not all apply to industrial solvents |
| ARIZ implementation | Full ARIZ is complex | Consider simplified version first |
| LLM-generated SMILES | Always validate with RDKit | LLMs can generate invalid structures |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| TRIZ 40 Principles | Altshuller, G. "The Innovation Algorithm" | High confidence - foundational TRIZ text |
| 9 Windows technique | Standard TRIZ methodology | High confidence |
| Su-Field modeling | Salamatov, Y. "TRIZ: Right Solution at Right Time" | High confidence |
| 76 Standard Solutions | Established TRIZ resource | High confidence - verify specific wording |
| Bioisostere concepts | Medicinal chemistry literature | Moderate - verify application to solvents |
| Separation science fundamentals | Perry's Handbook, Seader et al. | High confidence |

### Limitations and Caveats

1. **TRIZ-Chemistry Translation**: The mapping of TRIZ principles to molecular design is **novel and experimental**. There is no established literature on using TRIZ specifically for entrainer selection. Consider this a hypothesis-generation approach, not a validated methodology.

2. **LLM Reliability**: All molecular suggestions from LLM agents **must be validated**:
   - SMILES must parse in RDKit
   - Properties must be calculated and verified
   - Safety data must be checked against databases

3. **Agent Independence**: The agents may generate overlapping or contradictory suggestions. The synthesis step is critical.

4. **ARIZ Not Fully Implemented**: The full ARIZ algorithm (Algorithm of Inventive Problem Solving) is complex and would require significant additional work. The current implementation uses simplified TRIZ tools.

---

## GitHub Portfolio Framing

### README Section for Phase II-B

```markdown
## Phase II-B: Multi-Vector Initial Selection 🔧

### Engine B: TRIZ-Powered Consultation Module

**Status:** In Development

This module applies the Theory of Inventive Problem Solving (TRIZ) as a 
systematic innovation methodology for molecule selection.

#### Unique Approach
- **First application of TRIZ to entrainer selection** (novel methodology)
- Multi-agent architecture with specialized TRIZ tools
- Complements data-driven Engine A with structured expert intuition

#### TRIZ Techniques Applied
| Technique | Agent | Purpose |
|-----------|-------|---------|
| Contradiction Analysis | Agent 1 | Resolve competing requirements |
| 40 Inventive Principles | Agent 1 | Systematic solution generation |
| 9 Windows | Agent 2 | Temporal/hierarchical analysis |
| Ideality Analysis | Agent 2 | Move toward ideal system |
| Su-Field Modeling | Agent 3 | Substance-field interaction analysis |
| First Principles | Agent 4 | Physics-based requirement derivation |
| Inverse Design | Agent 5 | Property → structure mapping |
| Bio-isosterism | Agent 6 | Lateral thinking for analogs |

#### Key Innovation
This module treats molecular selection as an **inventive problem** rather than 
a search problem. By formalizing contradictions (e.g., "high selectivity vs. 
low toxicity"), we systematically explore non-obvious solution spaces.

#### Outputs
- 25-50 molecules with TRIZ-based selection rationale
- Directional insights for research exploration
- Flagged overlaps with Engine A (prioritized candidates)
```

### Suggested Badges

```markdown
![TRIZ](https://img.shields.io/badge/Methodology-TRIZ-red)
![Multi--Agent](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![Innovation](https://img.shields.io/badge/Approach-Systematic%20Innovation-green)
```

---

## Confidence Assessment

### High Confidence
- Overall multi-agent architecture design
- General TRIZ methodology descriptions
- First principles physics/chemistry for separation
- Code structure and error handling patterns
- Integration with Engine A (overlap detection)

### Needs Verification
- **TRIZ-to-chemistry mappings**: Novel application, not validated
- **Specific 40 Principles interpretations**: May need adjustment
- **Su-Field applicability**: Non-standard application domain
- **Bioisostere applicability**: From drug design, may not transfer
- **Gemini API specifics**: Verify current model names and API

### Outside My Expertise
- Whether TRIZ has been formally applied to molecular design before
- Optimal TRIZ technique prioritization for chemistry problems
- Industrial feasibility of LLM-generated molecular suggestions
- Current state of paramagnetic ionic liquid research

---

## Next Steps for Implementation

1. **Start with domain_mapping.py** - Define contradictions and translations
2. **Test one agent at a time** - Contradiction agent first (most structured)
3. **Validate LLM outputs** - Create validation pipeline for SMILES
4. **Iterate on prompts** - TRIZ prompts may need refinement
5. **Connect to molecule database** - Replace mock database with real queries
6. **Run integration test** - Full Engine B with Engine A results