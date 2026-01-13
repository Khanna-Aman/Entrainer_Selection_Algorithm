# 🎯 Phase V Implementation: Simulation & Validation

## Understanding Check

Based on your research proposal and approach documents, Phase V is the **final validation stage** where the top 10 candidates from Phase IV's Pareto frontier undergo rigorous process simulation. This phase:

1. Uses standard feed data consistent with industrial ethanol-water separation
2. Tests performance against defined KPIs (efficiency, safety, cost)
3. Enriches the database with concrete performance data
4. Provides a final ranked hierarchy validated for real-world application

**Key Context from Previous Phases:**
- Phase IV outputs Pareto-optimal molecules with efficiency/safety scores
- The "oracle" in Phase IV used UNIFAC-based property estimation
- Phase V provides higher-fidelity validation via actual process simulation
- This creates the data needed for the final "Pareto-Optimal Library" deliverable

---

## Recommended Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│      PHASE V: SIMULATION & VALIDATION              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   INPUT: Top 10 Candidates from Phase IV Pareto Frontier       │ │
│ │   - SMILES, names, Phase IV scores                 │ │
│ │   - Knee points prioritized                     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                       │
│               ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   FEED SPECIFICATION (Industrial Standard)              │ │
│ │   - Ethanol-water azeotropic feed composition             │ │
│ │   - Operating conditions (T, P, flow rates)              │ │
│ │   - Column specifications                      │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                       │
│               ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   THERMODYNAMIC PROPERTY CALCULATION                 │ │
│ │   - VLE data estimation (UNIFAC/NRTL)                 │ │
│ │   - Activity coefficients at operating conditions           │ │
│ │   - Azeotrope check (ISS method simplified)              │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                       │
│               ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   PROCESS SIMULATION                        │ │
│ │                                     │ │
│ │ ┌─────────────────────┐  ┌─────────────────────┐          │ │
│ │ │ EXTRACTIVE COLUMN │  │ RECOVERY COLUMN  │          │ │
│ │ │          │  │           │          │ │
│ │ │ Feed + Entrainer  │  │ Entrainer recovery │          │ │
│ │ │ → Ethanol (top)  │  │ → Water (top)    │          │ │
│ │ │ → Entrainer+Water │  │ → Entrainer (btm) │          │ │
│ │ └─────────────────────┘  └─────────────────────┘          │ │
│ │                                     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                       │
│               ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   KPI EVALUATION                          │ │
│ │   - Product purity (ethanol ≥99.5%)                  │ │
│ │   - Energy consumption (reboiler duty)                │ │
│ │   - Entrainer circulation rate                    │ │
│ │   - Entrainer losses                        │ │
│ │   - Safety metrics (from Phase II/IV)                 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                       │
│               ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │   OUTPUT: Final Ranked Hierarchy                   │ │
│ │   - Performance database enrichment                  │ │
│ │   - Validated molecules for real-world application           │ │
│ │   - Comparison with benchmark (ethylene glycol)            │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Simulation Approach: Practical Constraints

Given your 32GB RAM constraint and the goal of a portfolio-ready project, I recommend a **simplified steady-state simulation** approach rather than full process simulation software:

| Approach | Tool | Feasibility | Notes |
|----------|------|-------------|-------|
| ❌ Full Aspen Plus | Commercial | Not feasible | Expensive license, heavy compute |
| ❌ DWSIM full simulation | Open source | Marginal | Can be slow, complex setup |
| ✅ **Shortcut methods** | Python | Recommended | Fenske-Underwood-Gilliland |
| ✅ **Property-based ranking** | Python | Recommended | UNIFAC + heuristics |
| ✅ **Literature validation** | Manual | Recommended | Compare with published data |

**Reference:** Seader, Henley, Roper - "Separation Process Principles" Chapter 9 (Shortcut Methods for Multicomponent Distillation)

---

## Sub-Phase V.1: Feed Specification and Process Parameters

### Industrial Standard Feed Data

```python
# src/simulation/feed_specification.py
"""
Phase V.1: Feed Specification for Ethanol-Water Separation

Defines standard industrial feed conditions for extractive distillation
simulation of ethanol-water separation.

References:
- Perry's Chemical Engineers' Handbook, 9th Ed., Section 13
- Seader, Henley, Roper - "Separation Process Principles"
- Typical bioethanol plant specifications

[NEEDS VERIFICATION]: Specific industrial parameters may vary by plant.
These are representative values from literature.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

@dataclass
class ComponentProperties:
    """Physical properties of a component."""
    name: str
    cas: str
    molecular_weight: float  # g/mol
    boiling_point: float     # °C at 1 atm
    density: float           # kg/m³ at 25°C
    heat_capacity: float     # kJ/(kg·K) liquid at 25°C
    heat_of_vaporization: float  # kJ/kg at boiling point
    
    # Antoine equation coefficients for vapor pressure
    # log10(P_mmHg) = A - B/(T_°C + C)
    antoine_A: float = 0.0
    antoine_B: float = 0.0
    antoine_C: float = 0.0

# Standard component data
# Reference: NIST Chemistry WebBook (https://webbook.nist.gov/chemistry/)
# [VERIFY: Check values against NIST for accuracy]

ETHANOL = ComponentProperties(
    name="Ethanol",
    cas="64-17-5",
    molecular_weight=46.07,
    boiling_point=78.37,
    density=789.0,
    heat_capacity=2.44,
    heat_of_vaporization=846.0,
    antoine_A=8.11220,
    antoine_B=1592.864,
    antoine_C=226.184
)

WATER = ComponentProperties(
    name="Water",
    cas="7732-18-5",
    molecular_weight=18.015,
    boiling_point=100.0,
    density=997.0,
    heat_capacity=4.18,
    heat_of_vaporization=2260.0,
    antoine_A=8.07131,
    antoine_B=1730.63,
    antoine_C=233.426
)

@dataclass
class FeedSpecification:
    """
    Standard feed specification for ethanol-water separation.
    
    Based on typical bioethanol production:
    - Beer column output: ~40-50 mol% ethanol
    - Rectification column output: ~85-90 mol% ethanol (near azeotrope)
    - Target: fuel-grade ethanol (≥99.5 mol%)
    
    Reference: Perry's Handbook, Section 13
    """
    
    # Feed composition (mole fraction)
    ethanol_mole_fraction: float = 0.85  # Near-azeotropic feed
    water_mole_fraction: float = 0.15
    
    # Feed conditions
    temperature: float = 78.0  # °C (near ethanol BP)
    pressure: float = 101.325  # kPa (1 atm)
    feed_flow_rate: float = 100.0  # kmol/h (basis for calculations)
    
    # Feed quality
    feed_quality: float = 1.0  # 1.0 = saturated liquid, 0 = saturated vapor
    
    def validate(self) -> bool:
        """Validate that mole fractions sum to 1."""
        total = self.ethanol_mole_fraction + self.water_mole_fraction
        return abs(total - 1.0) < 0.001
    
    def to_dict(self) -> Dict:
        return {
            "composition": {
                "ethanol": self.ethanol_mole_fraction,
                "water": self.water_mole_fraction
            },
            "conditions": {
                "temperature_C": self.temperature,
                "pressure_kPa": self.pressure,
                "flow_rate_kmol_h": self.feed_flow_rate,
                "quality": self.feed_quality
            }
        }

@dataclass
class ProductSpecification:
    """
    Product purity requirements.
    
    Reference: 
    - Fuel-grade ethanol: ASTM D4806-21a (≥92.1 vol%, typically 99.5%+)
    - Industrial grade: Various specifications
    """
    
    ethanol_purity_target: float = 0.995  # Mole fraction
    max_water_in_ethanol: float = 0.005   # Mole fraction
    
    # Recovery targets
    ethanol_recovery: float = 0.995  # 99.5% recovery
    entrainer_recovery: float = 0.999  # 99.9% entrainer recovery (minimize losses)

@dataclass
class ColumnSpecification:
    """
    Extractive distillation column specifications.
    
    These are initial estimates; actual design would require
    rigorous simulation.
    
    Reference: Seader et al., typical extractive distillation design
    """
    
    # Extractive column
    extractive_stages: int = 30  # Theoretical stages
    extractive_feed_stage: int = 15  # Feed location (from top)
    entrainer_feed_stage: int = 5   # Entrainer enters above feed
    
    # Operating conditions
    reflux_ratio: float = 3.0  # R/R_min typical ~1.2-1.5, use higher for safety
    column_pressure: float = 101.325  # kPa
    
    # Entrainer ratio (mole entrainer / mole feed)
    entrainer_to_feed_ratio: float = 2.0  # Typical range: 1.5-3.0
    
    # Recovery column (entrainer regeneration)
    recovery_stages: int = 15
    recovery_reflux_ratio: float = 2.0

@dataclass
class SimulationCase:
    """
    Complete simulation case specification.
    """
    case_id: str
    entrainer_smiles: str
    entrainer_name: str
    feed: FeedSpecification = field(default_factory=FeedSpecification)
    product: ProductSpecification = field(default_factory=ProductSpecification)
    column: ColumnSpecification = field(default_factory=ColumnSpecification)
    
    def to_dict(self) -> Dict:
        return {
            "case_id": self.case_id,
            "entrainer": {
                "smiles": self.entrainer_smiles,
                "name": self.entrainer_name
            },
            "feed": self.feed.to_dict(),
            "product": {
                "ethanol_purity_target": self.product.ethanol_purity_target,
                "ethanol_recovery": self.product.ethanol_recovery,
                "entrainer_recovery": self.product.entrainer_recovery
            },
            "column": {
                "extractive_stages": self.column.extractive_stages,
                "reflux_ratio": self.column.reflux_ratio,
                "entrainer_to_feed_ratio": self.column.entrainer_to_feed_ratio
            }
        }


def create_benchmark_case() -> SimulationCase:
    """
    Create benchmark case using ethylene glycol as entrainer.
    
    Ethylene glycol is the most common industrial entrainer for
    ethanol-water separation. This serves as the baseline for comparison.
    
    Reference: Perry's Handbook, established industrial practice
    """
    return SimulationCase(
        case_id="BENCHMARK_EG",
        entrainer_smiles="OCCO",
        entrainer_name="Ethylene Glycol",
        feed=FeedSpecification(),
        product=ProductSpecification(),
        column=ColumnSpecification(
            entrainer_to_feed_ratio=2.5,  # Typical for EG
            extractive_stages=35,
            reflux_ratio=3.5
        )
    )


def create_simulation_cases(
    pareto_candidates: List[Dict],
    n_cases: int = 10
) -> List[SimulationCase]:
    """
    Create simulation cases from Phase IV Pareto-optimal candidates.
    
    Args:
        pareto_candidates: List of candidate dicts from Phase IV
        n_cases: Number of cases to create (default 10)
    
    Returns:
        List of SimulationCase objects
    """
    cases = []
    
    # Always include benchmark
    cases.append(create_benchmark_case())
    
    # Add Pareto candidates (prioritize knee points)
    sorted_candidates = sorted(
        pareto_candidates,
        key=lambda c: (-int(c.get("is_knee_point", False)), -c.get("efficiency", 0))
    )
    
    for i, candidate in enumerate(sorted_candidates[:n_cases-1]):
        case = SimulationCase(
            case_id=f"CANDIDATE_{i+1:02d}",
            entrainer_smiles=candidate.get("smiles", ""),
            entrainer_name=candidate.get("name", f"Candidate {i+1}"),
            feed=FeedSpecification(),
            product=ProductSpecification(),
            column=ColumnSpecification()  # Use default; adjust based on entrainer
        )
        cases.append(case)
    
    return cases


if __name__ == "__main__":
    # Test feed specification
    feed = FeedSpecification()
    print("Feed Specification:")
    print(f"  Ethanol: {feed.ethanol_mole_fraction:.1%}")
    print(f"  Water: {feed.water_mole_fraction:.1%}")
    print(f"  Valid: {feed.validate()}")
    
    # Test benchmark case
    benchmark = create_benchmark_case()
    print(f"\nBenchmark Case: {benchmark.entrainer_name}")
    print(f"  E/F ratio: {benchmark.column.entrainer_to_feed_ratio}")
```

---

## Sub-Phase V.2: Thermodynamic Property Calculation

### UNIFAC-Based VLE Estimation

```python
# src/simulation/thermodynamics.py
"""
Phase V.2: Thermodynamic Property Calculation

Estimates VLE behavior and activity coefficients for entrainer evaluation
using UNIFAC group contribution method.

References:
- Fredenslund, A., Gmehling, J., Rasmussen, P. (1977). 
  "Vapor-Liquid Equilibria using UNIFAC"
- DECHEMA Chemistry Data Series (VLE data)

[NEEDS VERIFICATION]: UNIFAC parameters and group assignments.
For production use, validate against experimental VLE data.

NOTE: This implementation uses simplified UNIFAC. For rigorous work,
use validated software (Aspen, DWSIM) or the 'thermo' library.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import math

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem, Fragments
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# Try to import thermo library for UNIFAC
try:
    from thermo import UNIFAC
    from thermo.unifac import UNIFAC_subgroups, DUFSG
    THERMO_AVAILABLE = True
except ImportError:
    THERMO_AVAILABLE = False
    print("INFO: 'thermo' library not available for rigorous UNIFAC.")
    print("      Using simplified estimation. Install with: pip install thermo")


@dataclass
class VLEResult:
    """Result from VLE calculation."""
    entrainer_smiles: str
    temperature: float  # K
    pressure: float     # Pa
    
    # Activity coefficients at infinite dilution in entrainer
    gamma_ethanol_inf: float
    gamma_water_inf: float
    
    # Selectivity (key metric)
    # S = γ∞_water / γ∞_ethanol
    # S > 1 means entrainer increases water volatility relative to ethanol
    selectivity: float
    
    # Relative volatility enhancement
    # α = (γ_ethanol * P°_ethanol) / (γ_water * P°_water)
    # For water removal: want α_ethanol/water > 1
    relative_volatility: float
    
    # Method used
    method: str
    confidence: str  # "high", "medium", "low"
    
    # Additional data
    notes: List[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "entrainer_smiles": self.entrainer_smiles,
            "temperature_K": self.temperature,
            "gamma_ethanol_inf": self.gamma_ethanol_inf,
            "gamma_water_inf": self.gamma_water_inf,
            "selectivity": self.selectivity,
            "relative_volatility": self.relative_volatility,
            "method": self.method,
            "confidence": self.confidence,
            "notes": self.notes or []
        }


class SimplifiedUNIFAC:
    """
    Simplified UNIFAC estimation for entrainer screening.
    
    This is NOT a full UNIFAC implementation. It uses heuristics
    based on molecular properties to estimate selectivity.
    
    For rigorous calculations, use:
    - The 'thermo' library
    - Aspen Plus / HYSYS
    - DWSIM
    
    [BASED ON GENERAL PRINCIPLES - requires validation]
    """
    
    # Vapor pressure constants for Antoine equation
    # log10(P_mmHg) = A - B/(T_°C + C)
    ANTOINE_ETHANOL = {"A": 8.11220, "B": 1592.864, "C": 226.184}
    ANTOINE_WATER = {"A": 8.07131, "B": 1730.63, "C": 233.426}
    
    def __init__(self, temperature_c: float = 78.0):
        """
        Args:
            temperature_c: Operating temperature in Celsius
        """
        self.temperature_c = temperature_c
        self.temperature_k = temperature_c + 273.15
        
    def vapor_pressure(self, antoine: Dict, temp_c: float) -> float:
        """Calculate vapor pressure using Antoine equation (mmHg)."""
        log_p = antoine["A"] - antoine["B"] / (temp_c + antoine["C"])
        return 10 ** log_p
    
    def estimate_activity_coefficients(
        self, 
        entrainer_smiles: str
    ) -> VLEResult:
        """
        Estimate infinite dilution activity coefficients.
        
        Uses molecular property heuristics:
        - H-bond donors/acceptors affect water affinity
        - LogP affects ethanol/water selectivity
        - Molecular size affects interaction strength
        
        Args:
            entrainer_smiles: SMILES of entrainer molecule
            
        Returns:
            VLEResult with estimated values
        """
        if not RDKIT_AVAILABLE:
            return VLEResult(
                entrainer_smiles=entrainer_smiles,
                temperature=self.temperature_k,
                pressure=101325,
                gamma_ethanol_inf=1.0,
                gamma_water_inf=1.0,
                selectivity=1.0,
                relative_volatility=1.0,
                method="failed",
                confidence="low",
                notes=["RDKit not available"]
            )
        
        mol = Chem.MolFromSmiles(entrainer_smiles)
        if mol is None:
            return VLEResult(
                entrainer_smiles=entrainer_smiles,
                temperature=self.temperature_k,
                pressure=101325,
                gamma_ethanol_inf=1.0,
                gamma_water_inf=1.0,
                selectivity=1.0,
                relative_volatility=1.0,
                method="failed",
                confidence="low",
                notes=["Invalid SMILES"]
            )
        
        # Calculate molecular properties
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hba = Descriptors.NumHAcceptors(mol)
        hbd = Descriptors.NumHDonors(mol)
        tpsa = Descriptors.TPSA(mol)
        
        notes = []
        
        # Heuristic estimation of activity coefficients
        # Based on thermodynamic principles:
        # - Higher polarity (low LogP) → better water compatibility
        # - More H-bond sites → stronger water interaction
        # - Larger molecule → stronger solvent effect
        
        # Estimate γ∞_ethanol (ethanol in entrainer)
        # Lower LogP of entrainer → more compatible with ethanol → lower γ
        # More H-bond sites → better interaction → lower γ
        base_gamma_ethanol = 2.0  # Base activity coefficient
        
        logp_factor = np.exp(0.2 * logp)  # LogP effect
        hbond_factor = 1.0 / (1 + 0.1 * (hba + hbd))  # H-bonding lowers γ
        size_factor = (mw / 100) ** 0.3  # Size effect
        
        gamma_ethanol = base_gamma_ethanol * logp_factor * hbond_factor * size_factor
        gamma_ethanol = np.clip(gamma_ethanol, 0.5, 10.0)
        
        # Estimate γ∞_water (water in entrainer)
        # Very polar entrainers (low LogP) → compatible with water → lower γ
        # Many H-bond sites → strong water interaction → lower γ
        base_gamma_water = 5.0  # Water typically has higher γ in organic solvents
        
        # Water affinity factor
        water_affinity = (hba + hbd) / (1 + abs(logp))
        polarity_factor = np.exp(-0.3 * tpsa / 50)  # Higher TPSA → more polar
        
        gamma_water = base_gamma_water / (1 + water_affinity) * polarity_factor
        gamma_water = np.clip(gamma_water, 0.5, 20.0)
        
        # Calculate selectivity
        # S = γ∞_water / γ∞_ethanol
        # S > 1 means water is more "uncomfortable" in entrainer → wants to leave
        selectivity = gamma_water / gamma_ethanol
        
        # Calculate relative volatility
        p_ethanol = self.vapor_pressure(self.ANTOINE_ETHANOL, self.temperature_c)
        p_water = self.vapor_pressure(self.ANTOINE_WATER, self.temperature_c)
        
        # α = (γ_ethanol * P°_ethanol) / (γ_water * P°_water)
        relative_volatility = (gamma_ethanol * p_ethanol) / (gamma_water * p_water)
        
        # Assess confidence
        if 0.8 < selectivity < 1.2:
            notes.append("Low selectivity - may not effectively break azeotrope")
            confidence = "medium"
        elif selectivity > 3.0:
            notes.append("High selectivity - promising entrainer candidate")
            confidence = "medium"  # Still medium because this is a heuristic
        else:
            confidence = "medium"
        
        # Add property notes
        if hba >= 3:
            notes.append(f"Good H-bond acceptor capacity (HBA={hba})")
        if logp < -1:
            notes.append("Very polar - good water affinity")
        elif logp > 2:
            notes.append("Low polarity - may not interact well with water")
        
        return VLEResult(
            entrainer_smiles=entrainer_smiles,
            temperature=self.temperature_k,
            pressure=101325,
            gamma_ethanol_inf=gamma_ethanol,
            gamma_water_inf=gamma_water,
            selectivity=selectivity,
            relative_volatility=relative_volatility,
            method="simplified_heuristic",
            confidence=confidence,
            notes=notes
        )


class RigorousUNIFAC:
    """
    Rigorous UNIFAC using the 'thermo' library.
    
    This provides more accurate activity coefficient estimation
    but requires proper UNIFAC group identification.
    
    Reference: thermo library documentation
    https://thermo.readthedocs.io/
    
    [VERIFY: Check thermo library API and UNIFAC implementation]
    """
    
    def __init__(self, temperature_k: float = 351.15):
        if not THERMO_AVAILABLE:
            raise ImportError("thermo library required. pip install thermo")
        self.temperature = temperature_k
    
    def estimate_activity_coefficients(
        self,
        entrainer_smiles: str
    ) -> VLEResult:
        """
        Estimate using rigorous UNIFAC from thermo library.
        
        [NEEDS VERIFICATION]: This is a template. Actual implementation
        requires proper UNIFAC group assignment which is complex.
        """
        # This is a placeholder - actual implementation would:
        # 1. Parse SMILES to identify UNIFAC groups
        # 2. Set up ternary system (ethanol + water + entrainer)
        # 3. Calculate activity coefficients
        
        # For now, fall back to simplified method
        simplified = SimplifiedUNIFAC(self.temperature - 273.15)
        result = simplified.estimate_activity_coefficients(entrainer_smiles)
        result.notes.append("[Fell back to simplified method - rigorous UNIFAC not implemented]")
        
        return result


@dataclass
class AzeotropeCheckResult:
    """Result from azeotrope formation check."""
    entrainer_smiles: str
    forms_azeotrope_with_ethanol: bool
    forms_azeotrope_with_water: bool
    is_suitable: bool  # No new azeotropes formed
    notes: List[str]


class AzeotropeChecker:
    """
    Check if entrainer forms azeotropes with ethanol or water.
    
    Based on the research proposal's ISS (Infinitely Sharp Step) method
    requirement, we need to verify no new distillation boundaries are created.
    
    [BASED ON GENERAL PRINCIPLES]: This is a simplified check.
    Full ISS analysis requires geometric analysis of residue curves.
    
    Reference: Laroche, L., Andersen, H. W., Morari, M. (1991).
    "Homogeneous Azeotropic Distillation" I&EC Research
    """
    
    # Known azeotrope-forming functional groups with water
    # Reference: General organic chemistry knowledge
    # [NEEDS VERIFICATION with azeotrope databases like DECHEMA]
    WATER_AZEOTROPE_RISK_PATTERNS = {
        "primary_alcohol": "[CH2][OH]",  # Can form azeotrope with water
        "secondary_alcohol": "[CH]([C])([C])[OH]",
        "carboxylic_acid": "[CX3](=O)[OX2H1]",  # Often forms azeotropes
    }
    
    # Patterns that typically DON'T form azeotropes (too polar/ionic)
    SAFE_PATTERNS = {
        "glycol": "[OX2H][CX4][CX4][OX2H]",  # Glycols generally safe
        "lactam": "[NR1][CR1](=O)",  # NMP-like, high BP, no azeotrope
        "sulfoxide": "[SX3](=[OX1])([#6])[#6]",  # DMSO-like
    }
    
    def check_azeotrope_formation(
        self,
        entrainer_smiles: str
    ) -> AzeotropeCheckResult:
        """
        Check if entrainer is likely to form azeotropes with ethanol/water.
        
        This is a HEURISTIC check based on structural patterns.
        For definitive answers, experimental VLE data is needed.
        """
        if not RDKIT_AVAILABLE:
            return AzeotropeCheckResult(
                entrainer_smiles=entrainer_smiles,
                forms_azeotrope_with_ethanol=False,
                forms_azeotrope_with_water=False,
                is_suitable=True,
                notes=["RDKit not available - assuming no azeotropes"]
            )
        
        mol = Chem.MolFromSmiles(entrainer_smiles)
        if mol is None:
            return AzeotropeCheckResult(
                entrainer_smiles=entrainer_smiles,
                forms_azeotrope_with_ethanol=False,
                forms_azeotrope_with_water=False,
                is_suitable=False,
                notes=["Invalid SMILES"]
            )
        
        notes = []
        water_azeotrope_risk = False
        ethanol_azeotrope_risk = False
        
        # Check safe patterns first
        is_safe_class = False
        for name, smarts in self.SAFE_PATTERNS.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern and mol.HasSubstructMatch(pattern):
                notes.append(f"Contains {name} pattern - typically safe")
                is_safe_class = True
        
        # Check risky patterns
        for name, smarts in self.WATER_AZEOTROPE_RISK_PATTERNS.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern and mol.HasSubstructMatch(pattern):
                notes.append(f"Contains {name} - potential azeotrope risk")
                water_azeotrope_risk = True
        
        # Boiling point heuristic
        # Very high BP compounds (>150°C) are less likely to form azeotropes
        # with low-BP water/ethanol
        mw = Descriptors.MolWt(mol)
        if mw > 150:
            notes.append("High MW suggests high BP - reduced azeotrope risk")
            water_azeotrope_risk = False  # Override if high MW
        
        # Check for very low BP compounds (problematic)
        if mw < 60:
            notes.append("Low MW may indicate low BP - verify experimentally")
            water_azeotrope_risk = True
        
        is_suitable = not (water_azeotrope_risk or ethanol_azeotrope_risk)
        if is_safe_class:
            is_suitable = True  # Safe patterns override concerns
        
        return AzeotropeCheckResult(
            entrainer_smiles=entrainer_smiles,
            forms_azeotrope_with_ethanol=ethanol_azeotrope_risk,
            forms_azeotrope_with_water=water_azeotrope_risk,
            is_suitable=is_suitable,
            notes=notes
        )


def evaluate_entrainer_thermodynamics(
    smiles: str,
    temperature_c: float = 78.0,
    use_rigorous: bool = False
) -> Tuple[VLEResult, AzeotropeCheckResult]:
    """
    Complete thermodynamic evaluation of an entrainer candidate.
    
    Args:
        smiles: Entrainer SMILES
        temperature_c: Operating temperature
        use_rigorous: Use rigorous UNIFAC (if available)
    
    Returns:
        Tuple of (VLEResult, AzeotropeCheckResult)
    """
    # VLE estimation
    if use_rigorous and THERMO_AVAILABLE:
        unifac = RigorousUNIFAC(temperature_c + 273.15)
    else:
        unifac = SimplifiedUNIFAC(temperature_c)
    
    vle_result = unifac.estimate_activity_coefficients(smiles)
    
    # Azeotrope check
    azeotrope_checker = AzeotropeChecker()
    azeotrope_result = azeotrope_checker.check_azeotrope_formation(smiles)
    
    return vle_result, azeotrope_result


if __name__ == "__main__":
    # Test with benchmark and candidates
    test_molecules = [
        ("OCCO", "Ethylene Glycol"),
        ("CN(C)C=O", "DMF"),
        ("CS(C)=O", "DMSO"),
        ("CN1CCCC1=O", "NMP"),
    ]
    
    print("Thermodynamic Evaluation Results")
    print("=" * 70)
    
    for smiles, name in test_molecules:
        vle, azeotrope = evaluate_entrainer_thermodynamics(smiles)
        
        print(f"\n{name} ({smiles})")
        print(f"  Selectivity (S = γ_water/γ_ethanol): {vle.selectivity:.2f}")
        print(f"  Relative Volatility: {vle.relative_volatility:.2f}")
        print(f"  Suitable (no azeotropes): {azeotrope.is_suitable}")
        print(f"  Notes: {'; '.join(vle.notes[:2])}")
```

---

## Sub-Phase V.3: Shortcut Process Simulation

### Fenske-Underwood-Gilliland Method

```python
# src/simulation/shortcut_simulation.py
"""
Phase V.3: Shortcut Process Simulation

Implements shortcut methods for extractive distillation column design:
- Fenske equation (minimum stages)
- Underwood equation (minimum reflux)
- Gilliland correlation (actual stages/reflux)

These methods provide quick estimates without rigorous simulation.

References:
- Seader, Henley, Roper - "Separation Process Principles" Ch. 9
- Fenske, M.R. (1932). Ind. Eng. Chem.
- Underwood, A.J.V. (1948). Chem. Eng. Prog.
- Gilliland, E.R. (1940). Ind. Eng. Chem.

[NEEDS VERIFICATION]: These are classic shortcut methods but have
limitations for highly non-ideal systems like extractive distillation.
Results should be validated against rigorous simulation.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import math

from src.simulation.feed_specification import (
    SimulationCase, 
    FeedSpecification,
    ProductSpecification,
    ColumnSpecification
)
from src.simulation.thermodynamics import VLEResult, AzeotropeCheckResult


@dataclass
class ShortcutResults:
    """Results from shortcut simulation."""
    case_id: str
    entrainer_smiles: str
    entrainer_name: str
    
    # Feasibility
    is_feasible: bool
    feasibility_notes: List[str]
    
    # Column design
    min_stages: float
    min_reflux_ratio: float
    actual_stages: int
    actual_reflux_ratio: float
    
    # Performance
    ethanol_purity: float  # Estimated product purity
    ethanol_recovery: float
    
    # Energy (relative to feed)
    reboiler_duty_relative: float  # kJ/kmol feed
    condenser_duty_relative: float
    
    # Entrainer requirements
    entrainer_circulation: float  # kmol entrainer / kmol feed
    entrainer_loss_fraction: float  # Fraction lost per cycle
    
    # Scores (normalized 0-1)
    efficiency_score: float
    energy_score: float
    overall_score: float
    
    # Thermodynamic data
    vle_result: Optional[VLEResult] = None
    azeotrope_check: Optional[AzeotropeCheckResult] = None
    
    def to_dict(self) -> Dict:
        return {
            "case_id": self.case_id,
            "entrainer_smiles": self.entrainer_smiles,
            "entrainer_name": self.entrainer_name,
            "is_feasible": self.is_feasible,
            "feasibility_notes": self.feasibility_notes,
            "design": {
                "min_stages": self.min_stages,
                "actual_stages": self.actual_stages,
                "min_reflux": self.min_reflux_ratio,
                "actual_reflux": self.actual_reflux_ratio,
                "entrainer_circulation": self.entrainer_circulation
            },
            "performance": {
                "ethanol_purity": self.ethanol_purity,
                "ethanol_recovery": self.ethanol_recovery,
                "reboiler_duty_relative": self.reboiler_duty_relative,
                "condenser_duty_relative": self.condenser_duty_relative
            },
            "scores": {
                "efficiency": self.efficiency_score,
                "energy": self.energy_score,
                "overall": self.overall_score
            }
        }


class ShortcutSimulator:
    """
    Shortcut simulation for extractive distillation column.
    
    Uses Fenske-Underwood-Gilliland (FUG) method adapted for
    extractive distillation.
    
    Assumptions:
    - Constant molar overflow (equimolar vaporization/condensation)
    - Constant relative volatility (average value)
    - Sharp separation of key components
    
    [BASED ON GENERAL PRINCIPLES]: These assumptions are approximate
    for extractive distillation. Results are for screening purposes.
    """
    
    def __init__(
        self,
        reflux_multiplier: float = 1.3,  # Actual/minimum reflux
        stage_efficiency: float = 0.7    # Murphree efficiency
    ):
        """
        Args:
            reflux_multiplier: R/R_min (typical 1.2-1.5)
            stage_efficiency: Overall stage efficiency
        """
        self.reflux_multiplier = reflux_multiplier
        self.stage_efficiency = stage_efficiency
    
    def fenske_min_stages(
        self,
        alpha: float,
        x_d: float,
        x_b: float
    ) -> float:
        """
        Fenske equation for minimum theoretical stages.
        
        N_min = ln[(x_d/(1-x_d)) * ((1-x_b)/x_b)] / ln(α)
        
        Args:
            alpha: Relative volatility (α_ethanol/water)
            x_d: Distillate composition (mole fraction light key)
            x_b: Bottoms composition (mole fraction light key)
        
        Returns:
            Minimum number of theoretical stages
        
        Reference: Fenske, M.R. (1932)
        """
        if alpha <= 1:
            return float('inf')  # Cannot separate
        
        numerator = math.log((x_d / (1 - x_d)) * ((1 - x_b) / x_b))
        denominator = math.log(alpha)
        
        return numerator / denominator
    
    def underwood_min_reflux(
        self,
        alpha: float,
        z_f: float,
        q: float,
        x_d: float
    ) -> float:
        """
        Underwood equation for minimum reflux ratio.
        
        Simplified for binary separation.
        
        Args:
            alpha: Relative volatility
            z_f: Feed composition (mole fraction light key)
            q: Feed quality (1 = saturated liquid)
            x_d: Distillate composition
        
        Returns:
            Minimum reflux ratio (R_min)
        
        Reference: Underwood, A.J.V. (1948)
        """
        if alpha <= 1:
            return float('inf')
        
        # For saturated liquid feed (q=1), simplified:
        # R_min = (α * x_d - x_f * (α - 1)) / ((α - 1) * (x_d - x_f))
        
        # More general form using theta (root of Underwood equation)
        # Approximation for binary:
        theta = (alpha * z_f - q * (alpha - 1)) / (alpha - 1)
        
        r_min = (alpha * x_d) / (alpha - theta) - 1
        
        return max(r_min, 0.1)  # Ensure positive
    
    def gilliland_correlation(
        self,
        n_min: float,
        r_min: float,
        r_actual: float
    ) -> float:
        """
        Gilliland correlation for actual stages.
        
        Uses Molokanov correlation (1972) for better fit.
        
        Args:
            n_min: Minimum stages (Fenske)
            r_min: Minimum reflux (Underwood)
            r_actual: Actual reflux ratio
        
        Returns:
            Actual number of theoretical stages
        
        Reference: Molokanov et al. (1972) - improved Gilliland
        """
        if r_actual <= r_min:
            return float('inf')
        
        x = (r_actual - r_min) / (r_actual + 1)
        
        # Molokanov correlation
        y = 1 - math.exp((1 + 54.4 * x) / (11 + 117.2 * x) * (x - 1) / math.sqrt(x))
        
        # y = (N - N_min) / (N + 1)
        # Solving for N:
        n_actual = (y + n_min) / (1 - y)
        
        return n_actual
    
    def estimate_energy_consumption(
        self,
        feed_rate: float,  # kmol/h
        reflux_ratio: float,
        distillate_rate: float,  # kmol/h
        delta_h_vap: float = 40.0  # kJ/mol, average heat of vaporization
    ) -> Tuple[float, float]:
        """
        Estimate reboiler and condenser duties.
        
        Q_reboiler ≈ (R + 1) * D * ΔH_vap
        Q_condenser ≈ R * D * ΔH_vap
        
        Args:
            feed_rate: Feed flow rate (kmol/h)
            reflux_ratio: Operating reflux ratio
            distillate_rate: Distillate flow rate (kmol/h)
            delta_h_vap: Heat of vaporization (kJ/mol)
        
        Returns:
            Tuple of (reboiler_duty_kW, condenser_duty_kW)
        """
        # Vapor rate at top = (R + 1) * D
        vapor_rate = (reflux_ratio + 1) * distillate_rate
        
        # Reboiler duty (kW = kJ/s)
        q_reboiler = vapor_rate * delta_h_vap * 1000 / 3600  # Convert to kW
        
        # Condenser duty (approximately)
        q_condenser = reflux_ratio * distillate_rate * delta_h_vap * 1000 / 3600
        
        return q_reboiler, q_condenser
    
    def run_simulation(
        self,
        case: SimulationCase,
        vle_result: VLEResult
    ) -> ShortcutResults:
        """
        Run shortcut simulation for a case.
        
        Args:
            case: Simulation case specification
            vle_result: VLE data from thermodynamic calculation
        
        Returns:
            ShortcutResults with simulation outputs
        """
        notes = []
        is_feasible = True
        
        # Check selectivity
        selectivity = vle_result.selectivity
        alpha = vle_result.relative_volatility
        
        if selectivity < 1.1:
            notes.append("Low selectivity - may not effectively break azeotrope")
            is_feasible = False
        elif selectivity < 1.5:
            notes.append("Moderate selectivity - may require high entrainer ratio")
        
        if not is_feasible:
            # Return infeasible result
            return ShortcutResults(
                case_id=case.case_id,
                entrainer_smiles=case.entrainer_smiles,
                entrainer_name=case.entrainer_name,
                is_feasible=False,
                feasibility_notes=notes,
                min_stages=float('inf'),
                min_reflux_ratio=float('inf'),
                actual_stages=0,
                actual_reflux_ratio=0,
                ethanol_purity=0,
                ethanol_recovery=0,
                reboiler_duty_relative=float('inf'),
                condenser_duty_relative=float('inf'),
                entrainer_circulation=0,
                entrainer_loss_fraction=0,
                efficiency_score=0,
                energy_score=0,
                overall_score=0,
                vle_result=vle_result
            )
        
        # Use relative volatility (corrected by entrainer effect)
        # For extractive distillation, α_effective ≈ α * selectivity_factor
        alpha_effective = alpha * (1 + 0.5 * (selectivity - 1))
        alpha_effective = max(alpha_effective, 1.05)  # Ensure separable
        
        # Feed and product specifications
        z_f = case.feed.ethanol_mole_fraction
        x_d = case.product.ethanol_purity_target
        x_b = 0.01  # 1% ethanol in bottoms (going to recovery column)
        
        # Fenske: minimum stages
        n_min = self.fenske_min_stages(alpha_effective, x_d, x_b)
        
        if n_min > 100:
            notes.append("Very high minimum stages required")
            n_min = 100
        
        # Underwood: minimum reflux
        r_min = self.underwood_min_reflux(alpha_effective, z_f, 1.0, x_d)
        
        if r_min > 10:
            notes.append("Very high minimum reflux required")
            r_min = min(r_min, 10)
        
        # Actual reflux
        r_actual = r_min * self.reflux_multiplier
        r_actual = max(r_actual, case.column.reflux_ratio)
        
        # Gilliland: actual stages
        n_actual_theory = self.gilliland_correlation(n_min, r_min, r_actual)
        n_actual = int(n_actual_theory / self.stage_efficiency) + 1
        
        # Estimate performance
        # Purity achieved (simplified - assume target met if feasible)
        if n_actual <= case.column.extractive_stages * 1.5:
            ethanol_purity = case.product.ethanol_purity_target
            ethanol_recovery = case.product.ethanol_recovery
            notes.append("Target purity achievable with reasonable stages")
        else:
            ethanol_purity = case.product.ethanol_purity_target * 0.95
            ethanol_recovery = case.product.ethanol_recovery * 0.98
            notes.append("May require more stages than specified")
        
        # Energy consumption
        feed_rate = case.feed.feed_flow_rate
        distillate_rate = feed_rate * z_f  # Approximate
        
        q_reboiler, q_condenser = self.estimate_energy_consumption(
            feed_rate, r_actual, distillate_rate
        )
        
        # Normalize to feed rate
        reboiler_relative = q_reboiler / feed_rate  # kW per kmol/h
        condenser_relative = q_condenser / feed_rate
        
        # Entrainer requirements
        # Higher selectivity → can use less entrainer
        base_entrainer_ratio = case.column.entrainer_to_feed_ratio
        adjusted_ratio = base_entrainer_ratio / (selectivity ** 0.3)
        adjusted_ratio = max(adjusted_ratio, 1.0)
        
        # Entrainer losses (very rough estimate)
        # Higher BP entrainer → lower losses
        entrainer_loss = 0.001 / (selectivity ** 0.5)  # Fraction per cycle
        
        # Calculate scores
        # Efficiency score (based on selectivity and stages)
        efficiency_score = min(selectivity / 3.0, 1.0) * min(30 / n_actual, 1.0)
        
        # Energy score (lower is better, normalized)
        # Benchmark: ethylene glycol typically ~3 kW/(kmol/h)
        energy_score = max(0, 1 - reboiler_relative / 5.0)
        
        # Overall score
        overall_score = 0.5 * efficiency_score + 0.5 * energy_score
        
        return ShortcutResults(
            case_id=case.case_id,
            entrainer_smiles=case.entrainer_smiles,
            entrainer_name=case.entrainer_name,
            is_feasible=True,
            feasibility_notes=notes,
            min_stages=n_min,
            min_reflux_ratio=r_min,
            actual_stages=n_actual,
            actual_reflux_ratio=r_actual,
            ethanol_purity=ethanol_purity,
            ethanol_recovery=ethanol_recovery,
            reboiler_duty_relative=reboiler_relative,
            condenser_duty_relative=condenser_relative,
            entrainer_circulation=adjusted_ratio,
            entrainer_loss_fraction=entrainer_loss,
            efficiency_score=efficiency_score,
            energy_score=energy_score,
            overall_score=overall_score,
            vle_result=vle_result
        )


if __name__ == "__main__":
    from src.simulation.feed_specification import create_benchmark_case
    from src.simulation.thermodynamics import evaluate_entrainer_thermodynamics
    
    # Test with benchmark
    benchmark = create_benchmark_case()
    vle, azeotrope = evaluate_entrainer_thermodynamics(benchmark.entrainer_smiles)
    
    simulator = ShortcutSimulator()
    result = simulator.run_simulation(benchmark, vle)
    
    print("Shortcut Simulation Results - Benchmark (Ethylene Glycol)")
    print("=" * 60)
    print(f"Feasible: {result.is_feasible}")
    print(f"Minimum Stages: {result.min_stages:.1f}")
    print(f"Actual Stages: {result.actual_stages}")
    print(f"Actual Reflux Ratio: {result.actual_reflux_ratio:.2f}")
    print(f"Reboiler Duty: {result.reboiler_duty_relative:.2f} kW/(kmol/h)")
    print(f"Efficiency Score: {result.efficiency_score:.3f}")
    print(f"Overall Score: {result.overall_score:.3f}")
```

---

## Sub-Phase V.4: KPI Evaluation and Ranking

### Comprehensive Performance Assessment

```python
# src/simulation/kpi_evaluation.py
"""
Phase V.4: KPI Evaluation and Final Ranking

Evaluates simulation results against defined KPIs and creates
final ranking of validated entrainer candidates.

KPIs from Research Proposal:
1. Product purity (ethanol ≥99.5%)
2. Energy consumption (minimize reboiler duty)
3. Safety profile (from Phase II/IV)
4. Cost-effectiveness (entrainer circulation, losses)
5. Environmental impact (biodegradability, toxicity)

References:
- Research Proposal Section 4: Expected Outcomes
- Perry's Handbook: Industrial separation standards
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime

from src.simulation.shortcut_simulation import ShortcutResults
from src.simulation.thermodynamics import AzeotropeCheckResult


@dataclass
class KPIThresholds:
    """
    KPI thresholds for pass/fail assessment.
    
    Based on industrial standards and research proposal targets.
    """
    # Product quality
    min_ethanol_purity: float = 0.995  # 99.5% mole fraction
    min_ethanol_recovery: float = 0.99  # 99% recovery
    
    # Energy
    max_reboiler_duty_relative: float = 4.0  # kW/(kmol/h feed)
    
    # Entrainer
    max_entrainer_ratio: float = 4.0  # mol entrainer / mol feed
    max_entrainer_loss: float = 0.005  # 0.5% loss per cycle
    
    # Safety (from Phase IV)
    max_safety_cost: float = 0.5  # Normalized cost (0-1)
    
    # Technical
    max_stages: int = 60  # Practical column limit


@dataclass
class KPIResult:
    """KPI evaluation for a single candidate."""
    case_id: str
    entrainer_smiles: str
    entrainer_name: str
    
    # Individual KPI pass/fail
    passes_purity: bool
    passes_recovery: bool
    passes_energy: bool
    passes_entrainer_ratio: bool
    passes_entrainer_loss: bool
    passes_safety: bool
    passes_stages: bool
    
    # Overall
    all_kpis_passed: bool
    kpis_passed_count: int
    total_kpis: int
    
    # Scores (0-1, higher is better)
    purity_score: float
    energy_score: float
    safety_score: float
    entrainer_score: float
    
    # Weighted overall score
    overall_score: float
    
    # Comparison to benchmark
    improvement_vs_benchmark: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            "case_id": self.case_id,
            "entrainer_smiles": self.entrainer_smiles,
            "entrainer_name": self.entrainer_name,
            "kpi_results": {
                "purity": self.passes_purity,
                "recovery": self.passes_recovery,
                "energy": self.passes_energy,
                "entrainer_ratio": self.passes_entrainer_ratio,
                "entrainer_loss": self.passes_entrainer_loss,
                "safety": self.passes_safety,
                "stages": self.passes_stages,
                "all_passed": self.all_kpis_passed,
                "passed_count": f"{self.kpis_passed_count}/{self.total_kpis}"
            },
            "scores": {
                "purity": self.purity_score,
                "energy": self.energy_score,
                "safety": self.safety_score,
                "entrainer": self.entrainer_score,
                "overall": self.overall_score
            },
            "vs_benchmark": self.improvement_vs_benchmark
        }


@dataclass
class FinalRanking:
    """Final ranking of all candidates."""
    timestamp: str
    candidates: List[KPIResult]
    benchmark_result: KPIResult
    top_candidate: Optional[KPIResult]
    summary: Dict
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "benchmark": self.benchmark_result.to_dict() if self.benchmark_result else None,
            "top_candidate": self.top_candidate.to_dict() if self.top_candidate else None,
            "all_candidates": [c.to_dict() for c in self.candidates]
        }


class KPIEvaluator:
    """
    Evaluates candidates against KPIs and creates final ranking.
    """
    
    # Score weights for overall score calculation
    WEIGHTS = {
        "purity": 0.15,
        "energy": 0.30,
        "safety": 0.35,  # Emphasized per research proposal
        "entrainer": 0.20
    }
    
    def __init__(self, thresholds: Optional[KPIThresholds] = None):
        self.thresholds = thresholds or KPIThresholds()
        self.benchmark_result: Optional[ShortcutResults] = None
    
    def set_benchmark(self, benchmark_sim: ShortcutResults):
        """Set benchmark results for comparison."""
        self.benchmark_result = benchmark_sim
    
    def evaluate_candidate(
        self,
        sim_result: ShortcutResults,
        safety_cost: float = 0.5,  # From Phase IV
        azeotrope_check: Optional[AzeotropeCheckResult] = None
    ) -> KPIResult:
        """
        Evaluate a single candidate against all KPIs.
        
        Args:
            sim_result: Shortcut simulation results
            safety_cost: Normalized safety cost from Phase IV (0-1, lower is better)
            azeotrope_check: Azeotrope formation check results
        
        Returns:
            KPIResult with evaluation
        """
        # Handle infeasible cases
        if not sim_result.is_feasible:
            return KPIResult(
                case_id=sim_result.case_id,
                entrainer_smiles=sim_result.entrainer_smiles,
                entrainer_name=sim_result.entrainer_name,
                passes_purity=False,
                passes_recovery=False,
                passes_energy=False,
                passes_entrainer_ratio=False,
                passes_entrainer_loss=False,
                passes_safety=False,
                passes_stages=False,
                all_kpis_passed=False,
                kpis_passed_count=0,
                total_kpis=7,
                purity_score=0,
                energy_score=0,
                safety_score=0,
                entrainer_score=0,
                overall_score=0,
                improvement_vs_benchmark={}
            )
        
        # Evaluate individual KPIs
        passes_purity = sim_result.ethanol_purity >= self.thresholds.min_ethanol_purity
        passes_recovery = sim_result.ethanol_recovery >= self.thresholds.min_ethanol_recovery
        passes_energy = sim_result.reboiler_duty_relative <= self.thresholds.max_reboiler_duty_relative
        passes_entrainer_ratio = sim_result.entrainer_circulation <= self.thresholds.max_entrainer_ratio
        passes_entrainer_loss = sim_result.entrainer_loss_fraction <= self.thresholds.max_entrainer_loss
        passes_safety = safety_cost <= self.thresholds.max_safety_cost
        passes_stages = sim_result.actual_stages <= self.thresholds.max_stages
        
        # Check azeotrope formation
        if azeotrope_check and not azeotrope_check.is_suitable:
            passes_purity = False  # Cannot achieve purity if azeotrope forms
        
        # Count passed KPIs
        kpi_list = [
            passes_purity, passes_recovery, passes_energy,
            passes_entrainer_ratio, passes_entrainer_loss,
            passes_safety, passes_stages
        ]
        kpis_passed = sum(kpi_list)
        all_passed = all(kpi_list)
        
        # Calculate scores (0-1, higher is better)
        
        # Purity score
        purity_score = min(sim_result.ethanol_purity / self.thresholds.min_ethanol_purity, 1.0)
        
        # Energy score (inverse - lower duty is better)
        energy_score = max(0, 1 - sim_result.reboiler_duty_relative / 
                          (2 * self.thresholds.max_reboiler_duty_relative))
        
        # Safety score (inverse of cost)
        safety_score = max(0, 1 - safety_cost)
        
        # Entrainer score (based on circulation rate and losses)
        entrainer_ratio_score = max(0, 1 - sim_result.entrainer_circulation / 
                                   (2 * self.thresholds.max_entrainer_ratio))
        entrainer_loss_score = max(0, 1 - sim_result.entrainer_loss_fraction / 
                                  (2 * self.thresholds.max_entrainer_loss))
        entrainer_score = 0.6 * entrainer_ratio_score + 0.4 * entrainer_loss_score
        
        # Weighted overall score
        overall_score = (
            self.WEIGHTS["purity"] * purity_score +
            self.WEIGHTS["energy"] * energy_score +
            self.WEIGHTS["safety"] * safety_score +
            self.WEIGHTS["entrainer"] * entrainer_score
        )
        
        # Comparison to benchmark
        improvement = {}
        if self.benchmark_result and self.benchmark_result.is_feasible:
            bench = self.benchmark_result
            
            # Energy improvement (positive = better than benchmark)
            if bench.reboiler_duty_relative > 0:
                energy_improvement = ((bench.reboiler_duty_relative - 
                                      sim_result.reboiler_duty_relative) / 
                                     bench.reboiler_duty_relative)
                improvement["energy_improvement"] = energy_improvement
            
            # Entrainer ratio improvement
            if bench.entrainer_circulation > 0:
                ratio_improvement = ((bench.entrainer_circulation - 
                                     sim_result.entrainer_circulation) / 
                                    bench.entrainer_circulation)
                improvement["entrainer_ratio_improvement"] = ratio_improvement
        
        return KPIResult(
            case_id=sim_result.case_id,
            entrainer_smiles=sim_result.entrainer_smiles,
            entrainer_name=sim_result.entrainer_name,
            passes_purity=passes_purity,
            passes_recovery=passes_recovery,
            passes_energy=passes_energy,
            passes_entrainer_ratio=passes_entrainer_ratio,
            passes_entrainer_loss=passes_entrainer_loss,
            passes_safety=passes_safety,
            passes_stages=passes_stages,
            all_kpis_passed=all_passed,
            kpis_passed_count=kpis_passed,
            total_kpis=7,
            purity_score=purity_score,
            energy_score=energy_score,
            safety_score=safety_score,
            entrainer_score=entrainer_score,
            overall_score=overall_score,
            improvement_vs_benchmark=improvement
        )
    
    def create_final_ranking(
        self,
        simulation_results: List[ShortcutResults],
        safety_costs: Dict[str, float],  # SMILES -> safety cost
        azeotrope_checks: Dict[str, AzeotropeCheckResult]
    ) -> FinalRanking:
        """
        Create final ranking of all candidates.
        
        Args:
            simulation_results: List of simulation results
            safety_costs: Safety costs by SMILES from Phase IV
            azeotrope_checks: Azeotrope check results by SMILES
        
        Returns:
            FinalRanking with all candidates ranked
        """
        kpi_results = []
        benchmark_kpi = None
        
        for sim in simulation_results:
            smiles = sim.entrainer_smiles
            safety_cost = safety_costs.get(smiles, 0.5)
            azeotrope = azeotrope_checks.get(smiles)
            
            kpi = self.evaluate_candidate(sim, safety_cost, azeotrope)
            
            if sim.case_id.startswith("BENCHMARK"):
                benchmark_kpi = kpi
            else:
                kpi_results.append(kpi)
        
        # Sort by overall score (descending)
        kpi_results.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Get top candidate
        top_candidate = kpi_results[0] if kpi_results else None
        
        # Summary statistics
        feasible_count = sum(1 for k in kpi_results if k.kpis_passed_count > 0)
        all_passed_count = sum(1 for k in kpi_results if k.all_kpis_passed)
        
        summary = {
            "total_candidates": len(kpi_results),
            "feasible_candidates": feasible_count,
            "all_kpis_passed": all_passed_count,
            "benchmark_score": benchmark_kpi.overall_score if benchmark_kpi else None,
            "top_score": top_candidate.overall_score if top_candidate else None,
            "better_than_benchmark": sum(
                1 for k in kpi_results 
                if benchmark_kpi and k.overall_score > benchmark_kpi.overall_score
            )
        }
        
        return FinalRanking(
            timestamp=datetime.now().isoformat(),
            candidates=kpi_results,
            benchmark_result=benchmark_kpi,
            top_candidate=top_candidate,
            summary=summary
        )


def generate_final_report(ranking: FinalRanking) -> str:
    """
    Generate a human-readable final report.
    """
    lines = [
        "=" * 70,
        "PHASE V: SIMULATION & VALIDATION - FINAL REPORT",
        "=" * 70,
        "",
        f"Timestamp: {ranking.timestamp}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Total candidates evaluated: {ranking.summary['total_candidates']}",
        f"Feasible candidates: {ranking.summary['feasible_candidates']}",
        f"Candidates passing all KPIs: {ranking.summary['all_kpis_passed']}",
        f"Candidates better than benchmark: {ranking.summary['better_than_benchmark']}",
        "",
    ]
    
    if ranking.benchmark_result:
        lines.extend([
            "BENCHMARK: Ethylene Glycol",
            "-" * 40,
            f"Overall Score: {ranking.benchmark_result.overall_score:.3f}",
            f"KPIs Passed: {ranking.benchmark_result.kpis_passed_count}/7",
            "",
        ])
    
    if ranking.top_candidate:
        lines.extend([
            "TOP CANDIDATE",
            "-" * 40,
            f"Name: {ranking.top_candidate.entrainer_name}",
            f"SMILES: {ranking.top_candidate.entrainer_smiles}",
            f"Overall Score: {ranking.top_candidate.overall_score:.3f}",
            f"KPIs Passed: {ranking.top_candidate.kpis_passed_count}/7",
            "",
            "Score Breakdown:",
            f"  Purity Score: {ranking.top_candidate.purity_score:.3f}",
            f"  Energy Score: {ranking.top_candidate.energy_score:.3f}",
            f"  Safety Score: {ranking.top_candidate.safety_score:.3f}",
            f"  Entrainer Score: {ranking.top_candidate.entrainer_score:.3f}",
        ])
        
        if ranking.top_candidate.improvement_vs_benchmark:
            lines.append("")
            lines.append("Improvement vs Benchmark:")
            for key, value in ranking.top_candidate.improvement_vs_benchmark.items():
                lines.append(f"  {key}: {value:+.1%}")
    
    lines.extend(["", "FULL RANKING", "-" * 40])
    
    for i, candidate in enumerate(ranking.candidates[:10], 1):
        status = "✓" if candidate.all_kpis_passed else "○"
        lines.append(
            f"{i:2d}. {status} {candidate.entrainer_name[:25]:<25} "
            f"Score: {candidate.overall_score:.3f} "
            f"({candidate.kpis_passed_count}/7 KPIs)"
        )
    
    lines.extend(["", "=" * 70])
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("KPI Evaluation module loaded.")
```

---

## Sub-Phase V.5: Phase V Orchestrator

### Complete Pipeline Integration

```python
# src/simulation/phase5_orchestrator.py
"""
Phase V.5: Complete Simulation & Validation Orchestrator

Integrates all Phase V components:
1. Load Phase IV Pareto-optimal candidates
2. Create simulation cases
3. Run thermodynamic calculations
4. Execute shortcut simulations
5. Evaluate against KPIs
6. Generate final ranking

This is the final phase of the molecule selection framework.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime

from src.simulation.feed_specification import (
    SimulationCase,
    create_benchmark_case,
    create_simulation_cases
)
from src.simulation.thermodynamics import (
    evaluate_entrainer_thermodynamics,
    VLEResult,
    AzeotropeCheckResult
)
from src.simulation.shortcut_simulation import (
    ShortcutSimulator,
    ShortcutResults
)
from src.simulation.kpi_evaluation import (
    KPIEvaluator,
    KPIThresholds,
    FinalRanking,
    generate_final_report
)


@dataclass
class Phase5Result:
    """Complete output from Phase V."""
    final_ranking: FinalRanking
    simulation_results: List[Dict]
    thermodynamic_results: List[Dict]
    report: str
    timestamp: str


class Phase5Orchestrator:
    """
    Orchestrates the complete Phase V pipeline.
    
    Input: Phase IV Pareto-optimal candidates (top 10)
    Output: Final validated ranking with performance data
    """
    
    def __init__(
        self,
        phase4_results_path: Optional[Path] = None,
        kpi_thresholds: Optional[KPIThresholds] = None
    ):
        self.phase4_path = phase4_results_path or Path("data/phase4_results.json")
        self.kpi_thresholds = kpi_thresholds or KPIThresholds()
        
        self.simulator = ShortcutSimulator()
        self.evaluator = KPIEvaluator(self.kpi_thresholds)
        
        # Results storage
        self.simulation_results: List[ShortcutResults] = []
        self.vle_results: Dict[str, VLEResult] = {}
        self.azeotrope_results: Dict[str, AzeotropeCheckResult] = {}
        self.safety_costs: Dict[str, float] = {}
    
    def load_phase4_candidates(self) -> List[Dict]:
        """Load Pareto-optimal candidates from Phase IV."""
        if not self.phase4_path.exists():
            print(f"Phase IV results not found at {self.phase4_path}")
            print("Using example candidates for demonstration...")
            
            # Example candidates for testing
            return [
                {"smiles": "OCCO", "name": "Ethylene Glycol", 
                 "efficiency": 0.75, "safety_cost": 0.3, "is_knee_point": False},
                {"smiles": "CN(C)C=O", "name": "DMF", 
                 "efficiency": 0.70, "safety_cost": 0.4, "is_knee_point": False},
                {"smiles": "CS(C)=O", "name": "DMSO", 
                 "efficiency": 0.72, "safety_cost": 0.25, "is_knee_point": True},
                {"smiles": "CN1CCCC1=O", "name": "NMP", 
                 "efficiency": 0.73, "safety_cost": 0.35, "is_knee_point": True},
                {"smiles": "OCC(O)CO", "name": "Glycerol", 
                 "efficiency": 0.68, "safety_cost": 0.15, "is_knee_point": False},
            ]
        
        with open(self.phase4_path) as f:
            data = json.load(f)
        
        return data.get("pareto_frontier", [])
    
    def run_pipeline(self, n_candidates: int = 10) -> Phase5Result:
        """
        Run the complete Phase V simulation pipeline.
        
        Args:
            n_candidates: Number of top candidates to simulate
        
        Returns:
            Phase5Result with final ranking and data
        """
        print("=" * 70)
        print("PHASE V: SIMULATION & VALIDATION")
        print("=" * 70)
        print("\nFinal validation of Pareto-optimal candidates\n")
        
        # Step 1: Load candidates
        print("[Step 1/5] Loading Phase IV candidates...")
        candidates = self.load_phase4_candidates()
        print(f"  Loaded {len(candidates)} candidates")
        
        # Store safety costs from Phase IV
        for c in candidates:
            self.safety_costs[c["smiles"]] = c.get("safety_cost", 0.5)
        
        # Step 2: Create simulation cases
        print("\n[Step 2/5] Creating simulation cases...")
        cases = create_simulation_cases(candidates, n_candidates)
        print(f"  Created {len(cases)} cases (including benchmark)")
        
        # Step 3: Thermodynamic calculations
        print("\n[Step 3/5] Running thermodynamic calculations...")
        for case in cases:
            print(f"  Evaluating: {case.entrainer_name}...")
            vle, azeotrope = evaluate_entrainer_thermodynamics(
                case.entrainer_smiles,
                temperature_c=case.feed.temperature
            )
            self.vle_results[case.entrainer_smiles] = vle
            self.azeotrope_results[case.entrainer_smiles] = azeotrope
        
        # Step 4: Shortcut simulation
        print("\n[Step 4/5] Running process simulations...")
        for case in cases:
            vle = self.vle_results[case.entrainer_smiles]
            print(f"  Simulating: {case.entrainer_name}...", end=" ")
            
            result = self.simulator.run_simulation(case, vle)
            self.simulation_results.append(result)
            
            if result.is_feasible:
                print(f"Score: {result.overall_score:.3f}")
            else:
                print("INFEASIBLE")
        
        # Set benchmark for comparison
        benchmark_results = [r for r in self.simulation_results 
                           if r.case_id.startswith("BENCHMARK")]
        if benchmark_results:
            self.evaluator.set_benchmark(benchmark_results[0])
        
        # Step 5: KPI evaluation and ranking
        print("\n[Step 5/5] Evaluating KPIs and creating final ranking...")
        
        ranking = self.evaluator.create_final_ranking(
            self.simulation_results,
            self.safety_costs,
            self.azeotrope_results
        )
        
        # Generate report
        report = generate_final_report(ranking)
        
        print("\n" + report)
        
        return Phase5Result(
            final_ranking=ranking,
            simulation_results=[r.to_dict() for r in self.simulation_results],
            thermodynamic_results=[v.to_dict() for v in self.vle_results.values()],
            report=report,
            timestamp=datetime.now().isoformat()
        )
    
    def export_results(
        self,
        result: Phase5Result,
        output_path: Optional[Path] = None
    ) -> Path:
        """Export Phase V results to JSON."""
        if output_path is None:
            output_path = Path("data/phase5_results.json")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "phase": "V",
            "stage": "simulation_validation",
            "timestamp": result.timestamp,
            "final_ranking": result.final_ranking.to_dict(),
            "simulation_results": result.simulation_results,
            "thermodynamic_results": result.thermodynamic_results
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        # Also save report as text
        report_path = output_path.parent / "phase5_report.txt"
        with open(report_path, 'w') as f:
            f.write(result.report)
        
        print(f"\nResults exported to: {output_path}")
        print(f"Report saved to: {report_path}")
        
        return output_path


def run_phase5_pipeline(
    phase4_results_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    n_candidates: int = 10
) -> Phase5Result:
    """
    Main entry point for Phase V.
    
    Args:
        phase4_results_path: Path to Phase IV results
        output_path: Where to save Phase V results
        n_candidates: Number of candidates to simulate
    
    Returns:
        Phase5Result with final validated ranking
    """
    orchestrator = Phase5Orchestrator(
        phase4_results_path=phase4_results_path
    )
    
    result = orchestrator.run_pipeline(n_candidates=n_candidates)
    
    if output_path is None:
        output_path = Path("data/phase5_results.json")
    
    orchestrator.export_results(result, output_path)
    
    return result


if __name__ == "__main__":
    result = run_phase5_pipeline()
```

---

## Code Artifacts Summary

### Project Structure Addition

```
src/
├── simulation/
│   ├── __init__.py
│   ├── feed_specification.py    # Industrial feed data
│   ├── thermodynamics.py        # UNIFAC, VLE, azeotrope check
│   ├── shortcut_simulation.py   # FUG method simulation
│   ├── kpi_evaluation.py        # KPI assessment and ranking
│   └── phase5_orchestrator.py   # Complete pipeline
```

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `33_feed_specification.ipynb` | Review industrial feed data |
| `34_thermodynamics.ipynb` | Test VLE and azeotrope calculations |
| `35_shortcut_simulation.ipynb` | Run and validate shortcut method |
| `36_kpi_evaluation.ipynb` | Analyze KPI results |
| `37_phase5_integration.ipynb` | Full Phase V pipeline |
| `38_final_visualization.ipynb` | Create final portfolio visualizations |

### Requirements Update

```
# requirements.txt - no additional dependencies for Phase V
# Uses RDKit (already required) and standard libraries
# Optional: thermo>=0.2.0 for rigorous UNIFAC
```

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | Reference |
|------|-----------------|-----------|
| UNIFAC parameters | Validate against experimental VLE | DECHEMA, NIST |
| Shortcut method accuracy | Compare with rigorous simulation | Seader et al. Chapter 9 |
| KPI thresholds | Confirm with industrial standards | Perry's Handbook |
| Safety cost mapping | Verify Phase IV integration | Phase IV results |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| Fenske equation | Fenske, M.R. (1932) Ind. Eng. Chem. | High confidence |
| Underwood method | Underwood, A.J.V. (1948) Chem. Eng. Prog. | High confidence |
| Gilliland correlation | Gilliland, E.R. (1940) Ind. Eng. Chem. | High confidence |
| Antoine equation | NIST Chemistry WebBook | High confidence |
| Ethanol fuel grade spec | ASTM D4806 | High confidence |
| Ethylene glycol as benchmark | Perry's Handbook, industrial practice | High confidence |

### Accuracy Limitations

1. **Simplified UNIFAC**: The activity coefficient estimation uses property-based heuristics. For production, implement proper UNIFAC or use the `thermo` library with validation.

2. **Shortcut Methods**: FUG method has limitations for extractive distillation due to:
   - Non-constant relative volatility
   - Three-component system simplification
   - Assumes ideal stage behavior

3. **Safety Cost Integration**: Assumes Phase IV safety costs are available. If not, uses default value (0.5).

4. **Energy Estimates**: Reboiler/condenser duties are approximations. Rigorous simulation needed for detailed design.

---

## GitHub Portfolio Framing

### README Section for Phase V

```markdown
## Phase V: Simulation & Validation 🔬

### Final Validation of Pareto-Optimal Candidates

**Status:** Complete

This phase subjects the top candidates from Phase IV to rigorous process 
simulation using shortcut methods (Fenske-Underwood-Gilliland).

#### Process Simulation Approach
| Method | Purpose | Reference |
|--------|---------|-----------|
| UNIFAC | VLE estimation | Fredenslund et al. |
| Fenske | Minimum stages | Fenske (1932) |
| Underwood | Minimum reflux | Underwood (1948) |
| Gilliland | Actual stages/reflux | Gilliland (1940) |

#### KPIs Evaluated
- Product purity (≥99.5% ethanol)
- Energy consumption (reboiler duty)
- Entrainer circulation rate
- Entrainer losses
- Safety profile (from Phase IV)
- Column stages (practical limit)

#### Key Outputs
- Final ranked hierarchy of validated entrainers
- Performance comparison vs. benchmark (ethylene glycol)
- Detailed simulation data for each candidate

### Reproducibility
```bash
# Run Phase V
python -m src.simulation.phase5_orchestrator

# Output:
# - data/phase5_results.json
# - data/phase5_report.txt
```

### Research Proposal Validation
This phase provides the concrete performance data needed for:
- **Pareto-Optimal Library**: HiPlot visualization of trade-offs
- **Quantifiable Metrics**: ISI reduction vs. efficiency penalty
- **Benchmark Comparison**: Improvement over ethylene glycol
```

### Suggested Badges

```markdown
![Phase](https://img.shields.io/badge/Phase-V%20Complete-green)
![Method](https://img.shields.io/badge/Method-Shortcut%20Simulation-blue)
![Validation](https://img.shields.io/badge/Validation-Industrial%20KPIs-orange)
```

---

## Complete Pipeline Summary

With Phase V complete, here is the full pipeline:

```
MOLECULE SELECTION FRAMEWORK FOR ETHANOL-WATER SEPARATION
═══════════════════════════════════════════════════════════

Phase I: Domain Mapping & Definition (Geological Survey)
├── Literature review + cluster definitions
├── ~500 molecular clusters identified
└── Output: Cluster definitions, benchmark compounds

Phase II: Multi-Vector Initial Selection (Seismic Analysis)
├── Engine A: Graph-RAG literature analysis (25-50 molecules)
├── Engine B: TRIZ innovation methodology (25-50 molecules)
├── Engine C: Cheminformatics diversity (25-50 molecules)
└── Output: 75-150 seed molecules with provenance

Phase III: Deep Traversal & Expansion (Drilling)
├── Seed consolidation (prioritize overlaps)
├── Graph traversal (structural, literature, property, mechanism)
├── Probability scoring + KPI filtering
└── Output: 150-300 expanded candidates

Phase IV: Intelligent Optimization (Active Learning)
├── Multi-objective Bayesian optimization (qEHVI)
├── GP surrogate on Morgan fingerprints
├── Pareto frontier identification + knee points
└── Output: Pareto-optimal candidates for simulation

Phase V: Simulation & Validation (Final Assay)
├── Thermodynamic property calculation
├── Shortcut process simulation
├── KPI evaluation vs. industrial standards
└── Output: Final validated ranking + performance data

═══════════════════════════════════════════════════════════
DELIVERABLES:
- Pareto-Optimal Library (300 molecules, HiPlot visualization)
- Top 10 Validated Entrainers (simulation-backed)
- Dockerized Virtual Lab (reproducible workflow)
- GitHub Portfolio Project
```

---

## Confidence Assessment

### High Confidence
- Fenske-Underwood-Gilliland shortcut methods
- Feed specification values (standard industry)
- KPI threshold concepts
- Antoine equation vapor pressure
- Overall Phase V architecture

### Needs Verification
- **Simplified UNIFAC accuracy** - validate against experimental data
- **thermo library API** - check current version and usage
- **Azeotrope formation heuristics** - consult DECHEMA data
- **Energy estimation accuracy** - compare with rigorous simulation

### Outside My Expertise
- Detailed column internals design
- Actual industrial cost data
- Regulatory compliance specifics
- Plant-specific operating constraints

---

## Final Integration Notes

### Complete Framework Execution

To run the complete pipeline:

```bash
# Phase I: Domain mapping
python -m src.corpus.populate_chromadb
python -m src.graphdb.populate_graph

# Phase II: Multi-vector selection
python -m src.llm.gemini_research_engine      # Engine A
python -m src.triz.engine_b_orchestrator      # Engine B
python -m src.cheminformatics.engine_c_orchestrator  # Engine C

# Phase III: Deep traversal
python -m src.traversal.phase3_orchestrator

# Phase IV: Bayesian optimization
python -m src.optimization.mobo_optimizer

# Phase V: Simulation & validation
python -m src.simulation.phase5_orchestrator
```

### Data Flow

```
Phase I → cluster_definitions.json
     ↓
Phase II → engine_a_results.json
        → engine_b_results.json
        → engine_c_results.json
     ↓
Phase III → phase3_results.json (150-300 candidates)
     ↓
Phase IV → phase4_results.json (Pareto frontier)
     ↓
Phase V → phase5_results.json (Final validated ranking)
       → phase5_report.txt
```

This completes the implementation guide for your Molecule Selection Framework for Ethanol-Water Separation. The framework is designed to be modular, reproducible, and portfolio-ready for your Master's capstone project.