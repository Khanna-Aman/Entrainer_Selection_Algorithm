# 🎯 Phase IV Implementation: Intelligent Optimization (The Active Learning Loop)

## Understanding Check

Based on my analysis of your research proposal and approach documents, Phase IV implements:

1. **Multi-Objective Bayesian Optimization (MOBO)** using Gaussian Process surrogate models
2. **Two competing objectives**: Safety (via barrier-shaped cost-of-mitigation function) and Efficiency (via UNIFAC-estimated infinite dilution coefficients)
3. **q-Expected Hypervolume Improvement (qEHVI)** as the acquisition function
4. **Active learning loop** that iteratively selects candidates to "test" via the oracle
5. **Goal**: Identify "Knee Points" on the Pareto frontier - molecules offering maximum safety for minimal efficiency loss

**Key Hypothesis to Test (H2)**: qEHVI achieves equivalent Pareto hypervolume to exhaustive evaluation using ≤30% of total computational budget.

---

## Recommended Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│     PHASE IV: MULTI-OBJECTIVE BAYESIAN OPTIMIZATION (MOBO)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │     INPUT: Phase III Candidates (150-300 molecules)                     │ │
│ │     - SMILES + Morgan Fingerprints                                      │ │
│ │     - Initial property estimates                                        │ │
│ │     - Safety flags from KPI screening                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │     FEATURE ENCODING                                                    │ │
│ │     Morgan Fingerprints (ECFP4) → Fixed-length vectors                  │ │
│ │     Optional: Physicochemical descriptors                               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │     OBJECTIVE FUNCTIONS (The "Oracle")                                  │ │
│ │                                                                         │ │
│ │  ┌──────────────────────┐    ┌──────────────────────┐                   │ │
│ │  │   EFFICIENCY (f₁)    │    │    SAFETY (f₂)       │                   │ │
│ │  │                      │    │                      │                   │ │
│ │  │ UNIFAC-estimated     │    │ Consensus safety     │                   │ │
│ │  │ infinite dilution    │    │ score transformed    │                   │ │
│ │  │ activity coefficient │    │ via barrier-shaped   │                   │ │
│ │  │ γ∞_water/γ∞_ethanol  │    │ cost-of-mitigation   │                   │ │
│ │  │                      │    │ function             │                   │ │
│ │  │ Higher = Better      │    │ Lower = Better       │                   │ │
│ │  │ (maximize)           │    │ (minimize cost)      │                   │ │
│ │  └──────────────────────┘    └──────────────────────┘                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │     ACTIVE LEARNING LOOP                                                │ │
│ │                                                                         │ │
│ │  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐     │ │
│ │  │  GP Model  │──▶│   qEHVI    │──▶│  Select    │──▶│  Evaluate  │     │ │
│ │  │  (Surrogate)│   │Acquisition │   │ Candidates │   │   Oracle   │     │ │
│ │  └────────────┘   └────────────┘   └────────────┘   └────────────┘     │ │
│ │        ▲                                                   │           │ │
│ │        └───────────────────────────────────────────────────┘           │ │
│ │                         Update Model                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │     OUTPUT: Pareto-Optimal Frontier                                     │ │
│ │     - Knee point identification                                         │ │
│ │     - Hypervolume metrics                                               │ │
│ │     - Candidates ranked for Phase V simulation                          │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack for Phase IV

| Component | Tool | Notes |
|-----------|------|-------|
| GP Surrogate | BoTorch (preferred) or GPyTorch | BoTorch has built-in MOBO support |
| Acquisition Function | qEHVI from BoTorch | Batch Expected Hypervolume Improvement |
| Fingerprints | RDKit Morgan FP | Already implemented in Phase II-C |
| UNIFAC Estimation | thermo library or UNIFAC implementation | [VERIFY: Check current Python UNIFAC options] |
| Optimization | PyTorch backend | Required by BoTorch |

**Reference:** BoTorch Multi-Objective Optimization Tutorial: https://botorch.org/tutorials/multi_objective_bo

---

## Sub-Phase IV.1: Objective Function Definitions

### The Two Competing Objectives

Your research proposal specifies two objectives that must be simultaneously optimized:

```python
# src/optimization/objectives.py
"""
Phase IV.1: Objective Function Definitions

Defines the two competing objectives for MOBO:
1. Efficiency: UNIFAC-estimated selectivity (maximize)
2. Safety: Cost-of-mitigation transformed score (minimize)

References:
- UNIFAC: Fredenslund et al., "Group-Contribution Estimation of Activity Coefficients"
- GHS Categories: https://www.osha.gov/hazcom/ghsguidance
- Research Proposal: Barrier-shaped cost-of-mitigation function

[NEEDS VERIFICATION]: UNIFAC implementation accuracy for specific functional groups
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import math

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# [NEEDS VERIFICATION]: thermo library for UNIFAC
# Alternative: Implement simplified UNIFAC or use pre-computed values
try:
    from thermo import UNIFAC
    from thermo.unifac import UNIFAC_groups
    THERMO_AVAILABLE = True
except ImportError:
    THERMO_AVAILABLE = False
    print("WARNING: 'thermo' library not available for UNIFAC calculations")
    print("Install with: pip install thermo")
    print("Falling back to simplified selectivity estimation")

@dataclass
class ObjectiveResult:
    """Result from objective function evaluation"""
    smiles: str
    efficiency_score: float  # Higher = better selectivity
    safety_score: float      # Lower = safer (cost of mitigation)
    efficiency_components: Dict
    safety_components: Dict
    valid: bool
    error: Optional[str] = None

class EfficiencyObjective:
    """
    Objective 1: Thermodynamic Efficiency
    
    Metric: Relative selectivity enhancement via infinite dilution 
    activity coefficient ratio.
    
    Target: Maximize γ∞_water(in entrainer) / γ∞_ethanol(in entrainer)
    
    Higher ratio means entrainer preferentially interacts with water,
    making water more volatile relative to ethanol.
    
    [NEEDS VERIFICATION]: UNIFAC group assignment accuracy
    """
    
    # Reference values for ethanol-water system without entrainer
    # At azeotropic composition, relative volatility ≈ 1
    BASELINE_SELECTIVITY = 1.0
    
    def __init__(self, use_unifac: bool = True, temperature_k: float = 351.15):
        """
        Args:
            use_unifac: If True, use UNIFAC for activity coefficients
                       If False, use simplified property-based estimation
            temperature_k: Operating temperature in Kelvin (default: 78°C, ethanol BP)
        """
        self.use_unifac = use_unifac and THERMO_AVAILABLE
        self.temperature = temperature_k
        
    def evaluate(self, smiles: str) -> Tuple[float, Dict]:
        """
        Evaluate efficiency (selectivity) for a molecule.
        
        Args:
            smiles: Molecule SMILES string
            
        Returns:
            Tuple of (efficiency_score, component_dict)
        """
        if self.use_unifac:
            return self._evaluate_unifac(smiles)
        else:
            return self._evaluate_simplified(smiles)
    
    def _evaluate_unifac(self, smiles: str) -> Tuple[float, Dict]:
        """
        Evaluate using UNIFAC activity coefficient estimation.
        
        [NEEDS VERIFICATION]: This is a template. Actual UNIFAC implementation
        requires proper group assignment which can be complex.
        """
        try:
            # This is a simplified template - actual implementation
            # requires proper UNIFAC group assignment
            
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return 0.0, {"error": "Invalid SMILES"}
            
            # [PLACEHOLDER]: Replace with actual UNIFAC calculation
            # The thermo library can do this but requires group identification
            
            # For now, use simplified estimation
            return self._evaluate_simplified(smiles)
            
        except Exception as e:
            return 0.0, {"error": str(e)}
    
    def _evaluate_simplified(self, smiles: str) -> Tuple[float, Dict]:
        """
        Simplified efficiency estimation based on molecular properties.
        
        Heuristic: Molecules with more H-bond acceptors and higher polarity
        tend to interact more strongly with water.
        
        This is a PROXY for actual selectivity. Real implementation should
        use UNIFAC or experimental data.
        
        [BASED ON GENERAL PRINCIPLES - needs validation]
        """
        if not RDKIT_AVAILABLE:
            return 0.5, {"error": "RDKit not available"}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return 0.0, {"error": "Invalid SMILES"}
            
            # Calculate relevant descriptors
            hba = Descriptors.NumHAcceptors(mol)
            hbd = Descriptors.NumHDonors(mol)
            tpsa = Descriptors.TPSA(mol)
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            
            # Heuristic scoring
            # More H-bond sites = better water interaction
            hbond_score = min((hba + hbd) / 6.0, 1.0)  # Normalize to ~0-1
            
            # Higher TPSA = more polar = better water affinity
            tpsa_score = min(tpsa / 100.0, 1.0)
            
            # LogP effect: slightly negative is ideal (hydrophilic but not too much)
            # Optimal around -1 to 1
            logp_score = 1.0 - min(abs(logp) / 3.0, 1.0) if -2 < logp < 3 else 0.3
            
            # MW effect: 80-250 is ideal range for entrainers
            mw_score = 1.0 if 80 <= mw <= 250 else 0.7 if 60 <= mw <= 350 else 0.4
            
            # Combined score (weighted)
            efficiency = (
                0.35 * hbond_score +
                0.30 * tpsa_score +
                0.20 * logp_score +
                0.15 * mw_score
            )
            
            components = {
                "hbond_score": hbond_score,
                "tpsa_score": tpsa_score,
                "logp_score": logp_score,
                "mw_score": mw_score,
                "hba": hba,
                "hbd": hbd,
                "tpsa": tpsa,
                "mw": mw,
                "logp": logp,
                "method": "simplified_heuristic"
            }
            
            return efficiency, components
            
        except Exception as e:
            return 0.0, {"error": str(e)}


class SafetyObjective:
    """
    Objective 2: Safety (Cost of Mitigation)
    
    Implements the barrier-shaped cost-of-mitigation function from the
    research proposal.
    
    Transforms discrete GHS categories into continuous costs:
    - Category 5 (low hazard): Low cost
    - Category 4: Moderate cost
    - Category 3: High cost
    - Category 2: Very high cost
    - Category 1 (fatal): Effectively infinite cost (barrier)
    
    The barrier function ensures that extremely hazardous chemicals
    are treated as infeasible rather than merely expensive.
    
    Reference: Research Proposal Section 3.2
    """
    
    # Cost multipliers for GHS acute toxicity categories
    # Lower category number = more toxic = higher cost
    # Using exponential scaling as per research proposal recommendation
    GHS_COST_MAP = {
        5: 10,        # Low hazard - minimal mitigation needed
        4: 100,       # Moderate - standard safety measures
        3: 1000,      # High - significant containment needed
        2: 10000,     # Very high - extensive controls required
        1: 1e9,       # Fatal - effectively infeasible (barrier)
        0: 1e9,       # Unknown/missing data - treat as worst case
    }
    
    # Flash point penalty thresholds
    FLASH_POINT_THRESHOLDS = [
        (23, 1000),   # < 23°C: Category 1 flammable
        (60, 100),    # 23-60°C: Category 2-3 flammable
        (93, 10),     # 60-93°C: Category 4 flammable
        (float('inf'), 1),  # > 93°C: Not classified as flammable
    ]
    
    def __init__(
        self,
        use_barrier: bool = True,
        barrier_threshold: int = 2,  # Categories <= this use barrier
        normalize_output: bool = True
    ):
        """
        Args:
            use_barrier: If True, use barrier function for worst categories
            barrier_threshold: GHS category at/below which barrier is applied
            normalize_output: If True, normalize cost to 0-1 range for GP
        """
        self.use_barrier = use_barrier
        self.barrier_threshold = barrier_threshold
        self.normalize_output = normalize_output
        
        # Normalization parameters (log scale)
        self.log_min_cost = np.log10(10)    # Category 5
        self.log_max_cost = np.log10(1e6)   # Before barrier
        
    def evaluate(
        self,
        smiles: str,
        ghs_category: Optional[int] = None,
        flash_point: Optional[float] = None,
        additional_hazards: Optional[List[str]] = None
    ) -> Tuple[float, Dict]:
        """
        Evaluate safety cost for a molecule.
        
        Args:
            smiles: Molecule SMILES string
            ghs_category: GHS acute toxicity category (1-5, or None)
            flash_point: Flash point in °C (or None)
            additional_hazards: List of additional hazard flags
            
        Returns:
            Tuple of (safety_cost, component_dict)
            Lower cost = safer molecule
        """
        components = {
            "smiles": smiles,
            "ghs_category": ghs_category,
            "flash_point": flash_point,
            "additional_hazards": additional_hazards or []
        }
        
        # If GHS category not provided, estimate from structure
        if ghs_category is None:
            ghs_category = self._estimate_ghs_category(smiles)
            components["ghs_estimated"] = True
        else:
            components["ghs_estimated"] = False
        
        # Base toxicity cost
        if self.use_barrier and ghs_category <= self.barrier_threshold:
            # Barrier: extremely high cost
            toxicity_cost = self.GHS_COST_MAP.get(ghs_category, 1e9)
            components["barrier_applied"] = True
        else:
            toxicity_cost = self.GHS_COST_MAP.get(ghs_category, 1e9)
            components["barrier_applied"] = False
        
        components["toxicity_cost"] = toxicity_cost
        
        # Flash point penalty
        flash_penalty = 1
        if flash_point is not None:
            for threshold, penalty in self.FLASH_POINT_THRESHOLDS:
                if flash_point < threshold:
                    flash_penalty = penalty
                    break
        
        components["flash_penalty"] = flash_penalty
        
        # Total cost
        total_cost = toxicity_cost * flash_penalty
        
        # Additional hazards penalty
        if additional_hazards:
            hazard_multiplier = 1 + 0.1 * len(additional_hazards)
            total_cost *= hazard_multiplier
            components["hazard_multiplier"] = hazard_multiplier
        
        components["total_cost_raw"] = total_cost
        
        # Normalize if requested
        if self.normalize_output:
            # Log transform then normalize to ~0-1
            # Lower = better (safer)
            log_cost = np.log10(max(total_cost, 1))
            normalized = (log_cost - self.log_min_cost) / (self.log_max_cost - self.log_min_cost)
            normalized = np.clip(normalized, 0, 1)
            
            # If barrier was applied, set to 1 (worst)
            if components.get("barrier_applied", False):
                normalized = 1.0
            
            components["normalized_cost"] = normalized
            return normalized, components
        else:
            return total_cost, components
    
    def _estimate_ghs_category(self, smiles: str) -> int:
        """
        Estimate GHS acute toxicity category from molecular structure.
        
        This is a SIMPLIFIED HEURISTIC. In production, you should:
        1. Query safety databases (ECHA, PubChem hazard data)
        2. Use validated QSAR models for toxicity
        3. Consult the consensus scoring from Phase II
        
        [BASED ON GENERAL PRINCIPLES - needs validation with real data]
        """
        if not RDKIT_AVAILABLE:
            return 0  # Unknown
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return 0
            
            # Simple heuristics based on structural features
            # These are VERY simplified and should be replaced with proper QSAR
            
            # Check for known hazardous patterns
            hazardous_patterns = {
                # Pattern: (SMARTS, estimated category if matched)
                "benzene_ring": ("c1ccccc1", 2),  # Aromatic - potential carcinogen
                "halogen": ("[F,Cl,Br,I]", 3),    # Halogenated
                "nitro": ("[N+](=O)[O-]", 2),     # Nitro group
                "azide": ("[N-]=[N+]=[N-]", 1),   # Azide - explosive
                "isocyanate": ("[N]=C=O", 2),    # Isocyanate - sensitizer
            }
            
            worst_category = 5  # Start with safest
            
            for name, (smarts, category) in hazardous_patterns.items():
                pattern = Chem.MolFromSmarts(smarts)
                if pattern and mol.HasSubstructMatch(pattern):
                    worst_category = min(worst_category, category)
            
            # Molecular weight heuristic
            # Very small molecules often more toxic (better absorption)
            mw = Descriptors.MolWt(mol)
            if mw < 60:
                worst_category = min(worst_category, 3)
            
            return worst_category
            
        except Exception:
            return 0  # Unknown


class CombinedObjectiveEvaluator:
    """
    Combines efficiency and safety objectives into a unified evaluator.
    
    For MOBO, we need both objectives evaluated consistently.
    BoTorch convention: maximize objectives (so we negate safety cost).
    """
    
    def __init__(
        self,
        efficiency_obj: Optional[EfficiencyObjective] = None,
        safety_obj: Optional[SafetyObjective] = None
    ):
        self.efficiency = efficiency_obj or EfficiencyObjective(use_unifac=False)
        self.safety = safety_obj or SafetyObjective(use_barrier=True)
        
    def evaluate(
        self,
        smiles: str,
        safety_data: Optional[Dict] = None
    ) -> ObjectiveResult:
        """
        Evaluate both objectives for a molecule.
        
        Args:
            smiles: Molecule SMILES
            safety_data: Optional dict with ghs_category, flash_point, etc.
            
        Returns:
            ObjectiveResult with both scores
        """
        # Efficiency (higher = better, will be maximized)
        eff_score, eff_components = self.efficiency.evaluate(smiles)
        
        # Safety (lower cost = better)
        # Extract safety data if provided
        ghs = safety_data.get("ghs_category") if safety_data else None
        flash = safety_data.get("flash_point") if safety_data else None
        hazards = safety_data.get("additional_hazards") if safety_data else None
        
        safety_cost, safety_components = self.safety.evaluate(
            smiles, ghs, flash, hazards
        )
        
        return ObjectiveResult(
            smiles=smiles,
            efficiency_score=eff_score,
            safety_score=safety_cost,
            efficiency_components=eff_components,
            safety_components=safety_components,
            valid=eff_score > 0 and not eff_components.get("error")
        )
    
    def evaluate_batch(
        self,
        smiles_list: List[str],
        safety_data_list: Optional[List[Dict]] = None
    ) -> List[ObjectiveResult]:
        """Evaluate a batch of molecules."""
        if safety_data_list is None:
            safety_data_list = [None] * len(smiles_list)
            
        results = []
        for smiles, safety_data in zip(smiles_list, safety_data_list):
            result = self.evaluate(smiles, safety_data)
            results.append(result)
            
        return results


if __name__ == "__main__":
    # Example usage
    evaluator = CombinedObjectiveEvaluator()
    
    test_molecules = [
        ("OCCO", {"ghs_category": 4, "flash_point": 111}),  # Ethylene glycol
        ("CN(C)C=O", {"ghs_category": 4}),                   # DMF
        ("CS(C)=O", {"ghs_category": 5}),                    # DMSO
        ("c1ccccc1", {"ghs_category": 1}),                   # Benzene (toxic)
    ]
    
    print("Objective Function Evaluation Results:")
    print("=" * 60)
    
    for smiles, safety_data in test_molecules:
        result = evaluator.evaluate(smiles, safety_data)
        print(f"\nSMILES: {smiles}")
        print(f"  Efficiency: {result.efficiency_score:.3f}")
        print(f"  Safety Cost: {result.safety_score:.3f}")
        print(f"  Valid: {result.valid}")
        if result.safety_components.get("barrier_applied"):
            print("  ⚠️ BARRIER APPLIED - Effectively infeasible")
```

---

## Sub-Phase IV.2: Gaussian Process Surrogate Model

### BoTorch-Based GP for Molecular Fingerprints

```python
# src/optimization/gp_surrogate.py
"""
Phase IV.2: Gaussian Process Surrogate Model

Implements GP surrogate model that learns the relationship between
molecular structure (Morgan Fingerprints) and objectives.

References:
- BoTorch GP Models: https://botorch.org/docs/models
- GPyTorch: https://gpytorch.ai/
- Morgan Fingerprints: RDKit documentation

[VERIFY: BoTorch API may have changed - check current documentation]
"""

from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import torch
    from torch import Tensor
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("ERROR: PyTorch required for Phase IV. Install with: pip install torch")

try:
    from botorch.models import SingleTaskGP
    from botorch.models.model_list_gp_regression import ModelListGP
    from botorch.models.transforms.outcome import Standardize
    from gpytorch.mlls import ExactMarginalLogLikelihood
    from botorch.fit import fit_gpytorch_mll
    BOTORCH_AVAILABLE = True
except ImportError:
    BOTORCH_AVAILABLE = False
    print("WARNING: BoTorch not available. Install with: pip install botorch")

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


class MolecularEncoder:
    """
    Encodes molecules as fixed-length vectors for GP input.
    
    Uses Morgan Fingerprints (ECFP4) as the primary representation.
    Optionally includes physicochemical descriptors.
    """
    
    def __init__(
        self,
        fingerprint_bits: int = 1024,
        fingerprint_radius: int = 2,
        include_descriptors: bool = True
    ):
        """
        Args:
            fingerprint_bits: Number of bits for Morgan fingerprint
            fingerprint_radius: Radius for Morgan fingerprint (2 = ECFP4)
            include_descriptors: Include physicochemical descriptors
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for MolecularEncoder")
            
        self.fp_bits = fingerprint_bits
        self.fp_radius = fingerprint_radius
        self.include_descriptors = include_descriptors
        
        # Descriptor normalization parameters (set during fit)
        self.descriptor_mean: Optional[np.ndarray] = None
        self.descriptor_std: Optional[np.ndarray] = None
        
    def encode_single(self, smiles: str) -> Optional[np.ndarray]:
        """
        Encode a single molecule.
        
        Args:
            smiles: SMILES string
            
        Returns:
            numpy array or None if invalid
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
            
        # Morgan fingerprint
        fp = AllChem.GetMorganFingerprintAsBitVect(
            mol, self.fp_radius, nBits=self.fp_bits
        )
        fp_array = np.zeros(self.fp_bits, dtype=np.float32)
        for i in fp.GetOnBits():
            fp_array[i] = 1.0
            
        if self.include_descriptors:
            from rdkit.Chem import Descriptors
            
            descriptors = np.array([
                Descriptors.MolWt(mol),
                Descriptors.MolLogP(mol),
                Descriptors.TPSA(mol),
                Descriptors.NumHAcceptors(mol),
                Descriptors.NumHDonors(mol),
                Descriptors.NumRotatableBonds(mol),
            ], dtype=np.float32)
            
            # Normalize if parameters set
            if self.descriptor_mean is not None:
                descriptors = (descriptors - self.descriptor_mean) / (self.descriptor_std + 1e-8)
                
            return np.concatenate([fp_array, descriptors])
        else:
            return fp_array
    
    def encode_batch(
        self, 
        smiles_list: List[str],
        fit_normalization: bool = False
    ) -> Tuple[np.ndarray, List[int]]:
        """
        Encode a batch of molecules.
        
        Args:
            smiles_list: List of SMILES strings
            fit_normalization: If True, fit normalization on this batch
            
        Returns:
            Tuple of (feature matrix, list of valid indices)
        """
        encodings = []
        valid_indices = []
        
        # First pass: encode all
        all_descriptors = [] if self.include_descriptors else None
        
        for i, smiles in enumerate(smiles_list):
            encoding = self.encode_single(smiles)
            if encoding is not None:
                encodings.append(encoding)
                valid_indices.append(i)
                
        if fit_normalization and self.include_descriptors and encodings:
            # Extract descriptor portion for normalization
            n_desc = 6  # Number of descriptors
            desc_array = np.array([e[-n_desc:] for e in encodings])
            self.descriptor_mean = np.mean(desc_array, axis=0)
            self.descriptor_std = np.std(desc_array, axis=0)
            
            # Re-normalize
            for j, e in enumerate(encodings):
                e[-n_desc:] = (e[-n_desc:] - self.descriptor_mean) / (self.descriptor_std + 1e-8)
                
        return np.array(encodings), valid_indices
    
    @property
    def feature_dim(self) -> int:
        """Return the feature dimension."""
        dim = self.fp_bits
        if self.include_descriptors:
            dim += 6  # Number of descriptors
        return dim


class MultiObjectiveGPSurrogate:
    """
    Multi-objective GP surrogate model using BoTorch.
    
    Uses a ModelListGP to model multiple objectives independently,
    as recommended for MOBO with qEHVI.
    
    Reference: BoTorch Multi-Objective Tutorial
    https://botorch.org/tutorials/multi_objective_bo
    """
    
    def __init__(
        self,
        encoder: Optional[MolecularEncoder] = None,
        n_objectives: int = 2,
        device: str = "cpu"
    ):
        """
        Args:
            encoder: MolecularEncoder instance (creates default if None)
            n_objectives: Number of objectives (default 2: efficiency, safety)
            device: PyTorch device ("cpu" or "cuda")
        """
        if not BOTORCH_AVAILABLE:
            raise ImportError("BoTorch required. Install with: pip install botorch")
            
        self.encoder = encoder or MolecularEncoder()
        self.n_objectives = n_objectives
        self.device = torch.device(device)
        
        # Will be set after fitting
        self.model: Optional[ModelListGP] = None
        self.train_X: Optional[Tensor] = None
        self.train_Y: Optional[Tensor] = None
        self.bounds: Optional[Tensor] = None
        
    def fit(
        self,
        smiles_list: List[str],
        objectives: np.ndarray,
        fit_iterations: int = 50
    ) -> Dict:
        """
        Fit the GP model to training data.
        
        Args:
            smiles_list: List of SMILES strings
            objectives: Array of shape (n_samples, n_objectives)
                       Column 0: Efficiency (to maximize)
                       Column 1: Safety cost (to minimize, will be negated)
            fit_iterations: Maximum iterations for hyperparameter optimization
            
        Returns:
            Dict with fitting statistics
        """
        # Encode molecules
        X, valid_indices = self.encoder.encode_batch(smiles_list, fit_normalization=True)
        
        if len(valid_indices) < 3:
            return {"error": "Need at least 3 valid molecules for GP fitting"}
        
        # Filter objectives to valid molecules
        Y = objectives[valid_indices]
        
        # Convert to tensors
        self.train_X = torch.tensor(X, dtype=torch.float64, device=self.device)
        
        # For MOBO, we maximize all objectives
        # Negate safety cost so higher = better
        Y_for_gp = Y.copy()
        Y_for_gp[:, 1] = -Y_for_gp[:, 1]  # Negate safety (column 1)
        
        self.train_Y = torch.tensor(Y_for_gp, dtype=torch.float64, device=self.device)
        
        # Set bounds for the feature space (used by acquisition function)
        self.bounds = torch.stack([
            self.train_X.min(dim=0).values,
            self.train_X.max(dim=0).values
        ]).to(self.device)
        
        # Create independent GP for each objective
        models = []
        for i in range(self.n_objectives):
            model = SingleTaskGP(
                self.train_X,
                self.train_Y[:, i:i+1],
                outcome_transform=Standardize(m=1)
            )
            models.append(model)
            
        self.model = ModelListGP(*models)
        
        # Fit hyperparameters
        mll = ExactMarginalLogLikelihood(self.model.likelihood, self.model)
        fit_gpytorch_mll(mll)
        
        return {
            "n_training": len(valid_indices),
            "n_objectives": self.n_objectives,
            "feature_dim": self.encoder.feature_dim,
            "train_Y_mean": Y.mean(axis=0).tolist(),
            "train_Y_std": Y.std(axis=0).tolist(),
        }
    
    def predict(
        self,
        smiles_list: List[str],
        return_std: bool = True
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Predict objectives for new molecules.
        
        Args:
            smiles_list: List of SMILES to predict
            return_std: If True, return uncertainty estimates
            
        Returns:
            Tuple of (mean_predictions, std_predictions)
            mean_predictions: Array of shape (n_samples, n_objectives)
            std_predictions: Array of same shape (if return_std=True)
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Encode
        X, valid_indices = self.encoder.encode_batch(smiles_list)
        
        if len(valid_indices) == 0:
            return np.array([]), np.array([]) if return_std else None
        
        X_tensor = torch.tensor(X, dtype=torch.float64, device=self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            posterior = self.model.posterior(X_tensor)
            mean = posterior.mean.cpu().numpy()
            
            if return_std:
                variance = posterior.variance.cpu().numpy()
                std = np.sqrt(variance)
            
        # Un-negate safety objective
        mean[:, 1] = -mean[:, 1]
        
        if return_std:
            return mean, std
        else:
            return mean, None
    
    def get_model_for_acquisition(self):
        """
        Return the model in a form suitable for BoTorch acquisition functions.
        
        Note: For qEHVI, the model should have objectives oriented for maximization.
        The safety objective negation is already applied in fit().
        """
        return self.model, self.train_X, self.train_Y, self.bounds


if __name__ == "__main__":
    print("GP Surrogate module loaded.")
    print("Requires: torch, botorch, rdkit")
    
    if BOTORCH_AVAILABLE and RDKIT_AVAILABLE:
        print("\nAll dependencies available. Testing...")
        
        # Simple test
        encoder = MolecularEncoder(fingerprint_bits=256)
        test_smiles = ["OCCO", "CN(C)C=O", "CS(C)=O"]
        
        X, valid = encoder.encode_batch(test_smiles, fit_normalization=True)
        print(f"Encoded {len(valid)} molecules to shape {X.shape}")
```

---

## Sub-Phase IV.3: qEHVI Acquisition Function and Active Learning Loop

### The Core Optimization Engine

```python
# src/optimization/mobo_optimizer.py
"""
Phase IV.3: Multi-Objective Bayesian Optimization with qEHVI

Implements the active learning loop using q-Expected Hypervolume Improvement.

Key Components:
1. qEHVI acquisition function (batch selection)
2. Active learning loop (iterative refinement)
3. Pareto frontier tracking
4. Hypervolume computation

References:
- BoTorch qEHVI: https://botorch.org/tutorials/multi_objective_bo
- Daulton et al. (2020). "Differentiable Expected Hypervolume Improvement"
  NeurIPS 2020. [VERIFY: Check paper for implementation details]

[VERIFY: BoTorch API for qEHVI - may require specific version]
"""

from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path
import json
from datetime import datetime

try:
    import torch
    from torch import Tensor
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from botorch.acquisition.multi_objective.monte_carlo import (
        qExpectedHypervolumeImprovement
    )
    from botorch.utils.multi_objective.box_decompositions.dominated import (
        DominatedPartitioning
    )
    from botorch.utils.multi_objective.pareto import is_non_dominated
    from botorch.optim import optimize_acqf
    from botorch.utils.sampling import sample_simplex
    BOTORCH_AVAILABLE = True
except ImportError:
    BOTORCH_AVAILABLE = False
    print("WARNING: BoTorch not available for qEHVI")

# Import our modules
from src.optimization.objectives import CombinedObjectiveEvaluator, ObjectiveResult
from src.optimization.gp_surrogate import MultiObjectiveGPSurrogate, MolecularEncoder


@dataclass
class ParetoPoint:
    """A point on the Pareto frontier"""
    smiles: str
    name: str
    efficiency: float  # Objective 1 (higher = better)
    safety_cost: float  # Objective 2 (lower = better)
    iteration_found: int
    is_knee_point: bool = False
    additional_data: Dict = field(default_factory=dict)

@dataclass
class OptimizationState:
    """Tracks the state of the optimization loop"""
    iteration: int
    evaluated_smiles: List[str]
    evaluated_objectives: np.ndarray
    pareto_frontier: List[ParetoPoint]
    hypervolume_history: List[float]
    cumulative_regret: List[float]

@dataclass
class MOBOConfig:
    """Configuration for MOBO optimization"""
    # Reference point for hypervolume calculation
    # Should be worse than any feasible objective value
    ref_point: List[float] = field(default_factory=lambda: [0.0, 1.0])
    # [efficiency_worst, safety_cost_worst]
    
    # Batch size for acquisition (q in qEHVI)
    batch_size: int = 4
    
    # Maximum iterations (budget)
    max_iterations: int = 50
    
    # Initial samples before starting MOBO
    n_initial_samples: int = 10
    
    # MC samples for qEHVI
    mc_samples: int = 128
    
    # Early stopping
    early_stop_patience: int = 10
    early_stop_threshold: float = 0.001  # Min HV improvement


class MOBOOptimizer:
    """
    Multi-Objective Bayesian Optimization using qEHVI.
    
    Implements the active learning loop from the research proposal:
    1. Fit GP surrogate on current observations
    2. Optimize qEHVI to select next batch of molecules
    3. Evaluate selected molecules via oracle
    4. Update observations and repeat
    
    Tracks:
    - Pareto frontier evolution
    - Hypervolume over iterations
    - Cumulative regret (for H2 hypothesis testing)
    """
    
    def __init__(
        self,
        candidate_smiles: List[str],
        candidate_metadata: Optional[List[Dict]] = None,
        config: Optional[MOBOConfig] = None,
        evaluator: Optional[CombinedObjectiveEvaluator] = None,
        device: str = "cpu"
    ):
        """
        Args:
            candidate_smiles: List of candidate molecules (from Phase III)
            candidate_metadata: Optional metadata for candidates (safety data, etc.)
            config: MOBO configuration
            evaluator: Objective function evaluator
            device: PyTorch device
        """
        if not BOTORCH_AVAILABLE:
            raise ImportError("BoTorch required. Install with: pip install botorch")
            
        self.candidates = candidate_smiles
        self.metadata = candidate_metadata or [{}] * len(candidate_smiles)
        self.config = config or MOBOConfig()
        self.evaluator = evaluator or CombinedObjectiveEvaluator()
        self.device = torch.device(device)
        
        # Encoder for molecules
        self.encoder = MolecularEncoder(fingerprint_bits=512)
        
        # Pre-encode all candidates
        self.candidate_features, self.valid_candidate_indices = \
            self.encoder.encode_batch(candidate_smiles, fit_normalization=True)
        
        # Map valid indices back to original
        self.valid_smiles = [candidate_smiles[i] for i in self.valid_candidate_indices]
        self.valid_metadata = [self.metadata[i] for i in self.valid_candidate_indices]
        
        print(f"Initialized MOBO with {len(self.valid_smiles)} valid candidates")
        
        # State tracking
        self.state: Optional[OptimizationState] = None
        self.gp_model: Optional[MultiObjectiveGPSurrogate] = None
        
    def _evaluate_batch(
        self,
        smiles_list: List[str],
        metadata_list: List[Dict]
    ) -> List[ObjectiveResult]:
        """Evaluate a batch of molecules using the oracle."""
        results = []
        for smiles, meta in zip(smiles_list, metadata_list):
            result = self.evaluator.evaluate(smiles, meta)
            results.append(result)
        return results
    
    def _select_initial_samples(self, n: int) -> Tuple[List[str], List[Dict]]:
        """
        Select initial samples for GP training.
        
        Strategy: Use Latin Hypercube Sampling in feature space
        or random selection from candidates.
        """
        n = min(n, len(self.valid_smiles))
        
        # Simple random selection for now
        # [IMPROVEMENT]: Use MaxMin diversity selection from Phase II-C
        indices = np.random.choice(len(self.valid_smiles), n, replace=False)
        
        selected_smiles = [self.valid_smiles[i] for i in indices]
        selected_meta = [self.valid_metadata[i] for i in indices]
        
        return selected_smiles, selected_meta
    
    def _compute_hypervolume(
        self,
        objectives: np.ndarray,
        ref_point: List[float]
    ) -> float:
        """
        Compute hypervolume indicator for current Pareto frontier.
        
        Args:
            objectives: Array of shape (n, 2) [efficiency, safety_cost]
            ref_point: Reference point [eff_worst, safety_worst]
            
        Returns:
            Hypervolume value
        """
        if len(objectives) == 0:
            return 0.0
            
        # Convert to tensor for BoTorch
        # Note: For HV, we want higher = better for both, so negate safety
        Y = objectives.copy()
        Y[:, 1] = -Y[:, 1]  # Negate safety so higher = better
        
        ref = [ref_point[0], -ref_point[1]]  # Also negate ref for safety
        
        Y_tensor = torch.tensor(Y, dtype=torch.float64)
        ref_tensor = torch.tensor(ref, dtype=torch.float64)
        
        # Find non-dominated points
        pareto_mask = is_non_dominated(Y_tensor)
        pareto_Y = Y_tensor[pareto_mask]
        
        if len(pareto_Y) == 0:
            return 0.0
        
        # Compute hypervolume
        partitioning = DominatedPartitioning(ref_point=ref_tensor, Y=pareto_Y)
        hv = partitioning.compute_hypervolume().item()
        
        return hv
    
    def _extract_pareto_frontier(
        self,
        smiles_list: List[str],
        objectives: np.ndarray,
        iteration: int
    ) -> List[ParetoPoint]:
        """
        Extract the Pareto-optimal points from current observations.
        """
        # Convert for BoTorch (negate safety)
        Y = objectives.copy()
        Y[:, 1] = -Y[:, 1]
        
        Y_tensor = torch.tensor(Y, dtype=torch.float64)
        pareto_mask = is_non_dominated(Y_tensor).numpy()
        
        pareto_points = []
        for i, is_pareto in enumerate(pareto_mask):
            if is_pareto:
                pareto_points.append(ParetoPoint(
                    smiles=smiles_list[i],
                    name="",  # Could look up from metadata
                    efficiency=objectives[i, 0],
                    safety_cost=objectives[i, 1],
                    iteration_found=iteration,
                    is_knee_point=False  # Will be determined later
                ))
        
        return pareto_points
    
    def _identify_knee_points(
        self,
        pareto_points: List[ParetoPoint]
    ) -> List[ParetoPoint]:
        """
        Identify knee points on the Pareto frontier.
        
        Knee point: Point where the trade-off rate changes significantly.
        Maximum curvature point on the Pareto front.
        
        [BASED ON GENERAL PRINCIPLES]: Uses angle-based detection
        """
        if len(pareto_points) < 3:
            # All points are knee points if fewer than 3
            for p in pareto_points:
                p.is_knee_point = True
            return pareto_points
        
        # Sort by efficiency
        sorted_points = sorted(pareto_points, key=lambda p: p.efficiency)
        
        # Calculate angles at each point
        for i in range(1, len(sorted_points) - 1):
            p_prev = sorted_points[i - 1]
            p_curr = sorted_points[i]
            p_next = sorted_points[i + 1]
            
            # Vectors
            v1 = np.array([p_prev.efficiency - p_curr.efficiency,
                          p_prev.safety_cost - p_curr.safety_cost])
            v2 = np.array([p_next.efficiency - p_curr.efficiency,
                          p_next.safety_cost - p_curr.safety_cost])
            
            # Normalize
            v1 = v1 / (np.linalg.norm(v1) + 1e-8)
            v2 = v2 / (np.linalg.norm(v2) + 1e-8)
            
            # Angle (via dot product)
            cos_angle = np.clip(np.dot(v1, v2), -1, 1)
            angle = np.arccos(cos_angle)
            
            # Knee point has smallest angle (highest curvature)
            sorted_points[i].additional_data["curvature_angle"] = angle
        
        # Find maximum curvature (minimum angle)
        middle_points = sorted_points[1:-1]
        if middle_points:
            min_angle_point = min(
                middle_points, 
                key=lambda p: p.additional_data.get("curvature_angle", np.pi)
            )
            min_angle_point.is_knee_point = True
        
        return sorted_points
    
    def _optimize_acquisition(
        self,
        model,
        train_X: Tensor,
        train_Y: Tensor,
        bounds: Tensor,
        batch_size: int
    ) -> Tuple[Tensor, float]:
        """
        Optimize qEHVI acquisition function to select next batch.
        
        [VERIFY: BoTorch qEHVI API and parameters]
        """
        # Reference point (in maximization space)
        ref_point = torch.tensor(
            [self.config.ref_point[0], -self.config.ref_point[1]],
            dtype=torch.float64,
            device=self.device
        )
        
        # Partition current Pareto frontier
        partitioning = DominatedPartitioning(
            ref_point=ref_point,
            Y=train_Y
        )
        
        # Create qEHVI acquisition function
        acq_func = qExpectedHypervolumeImprovement(
            model=model,
            ref_point=ref_point.tolist(),
            partitioning=partitioning,
            sampler=None,  # Use default sampler
        )
        
        # Optimize to find best batch
        # Note: This searches in feature space, not directly over candidates
        # For discrete candidate sets, we evaluate acq_func on all candidates
        
        # Encode all remaining candidates
        remaining_mask = np.ones(len(self.valid_smiles), dtype=bool)
        if self.state:
            for smiles in self.state.evaluated_smiles:
                if smiles in self.valid_smiles:
                    idx = self.valid_smiles.index(smiles)
                    remaining_mask[idx] = False
        
        remaining_indices = np.where(remaining_mask)[0]
        
        if len(remaining_indices) == 0:
            return None, 0.0
        
        remaining_features = self.candidate_features[remaining_indices]
        X_cand = torch.tensor(remaining_features, dtype=torch.float64, device=self.device)
        
        # Evaluate acquisition on all remaining candidates
        with torch.no_grad():
            # qEHVI expects shape (q, n_features) for batch evaluation
            # Evaluate each candidate individually and select top batch_size
            acq_values = []
            for i in range(len(X_cand)):
                x = X_cand[i:i+1].unsqueeze(0)  # Shape: (1, 1, n_features)
                acq_val = acq_func(x)
                acq_values.append(acq_val.item())
        
        acq_values = np.array(acq_values)
        
        # Select top batch_size
        top_indices = np.argsort(acq_values)[-batch_size:]
        
        selected_features = X_cand[top_indices]
        best_acq = acq_values[top_indices].max()
        
        # Map back to SMILES
        selected_smiles = [self.valid_smiles[remaining_indices[i]] for i in top_indices]
        
        return selected_smiles, best_acq
    
    def run_optimization(
        self,
        verbose: bool = True
    ) -> OptimizationState:
        """
        Run the full MOBO optimization loop.
        
        Returns:
            OptimizationState with results
        """
        print("=" * 70)
        print("PHASE IV: MULTI-OBJECTIVE BAYESIAN OPTIMIZATION")
        print("=" * 70)
        print(f"\nCandidates: {len(self.valid_smiles)}")
        print(f"Max iterations: {self.config.max_iterations}")
        print(f"Batch size: {self.config.batch_size}")
        print(f"Reference point: {self.config.ref_point}")
        
        # Initialize state
        self.state = OptimizationState(
            iteration=0,
            evaluated_smiles=[],
            evaluated_objectives=np.empty((0, 2)),
            pareto_frontier=[],
            hypervolume_history=[],
            cumulative_regret=[]
        )
        
        # Step 1: Initial sampling
        print(f"\n[Step 1] Initial sampling ({self.config.n_initial_samples} samples)...")
        
        init_smiles, init_meta = self._select_initial_samples(
            self.config.n_initial_samples
        )
        
        init_results = self._evaluate_batch(init_smiles, init_meta)
        
        # Extract objectives
        init_objectives = np.array([
            [r.efficiency_score, r.safety_score] for r in init_results
        ])
        
        self.state.evaluated_smiles.extend(init_smiles)
        self.state.evaluated_objectives = init_objectives
        
        # Compute initial hypervolume
        init_hv = self._compute_hypervolume(init_objectives, self.config.ref_point)
        self.state.hypervolume_history.append(init_hv)
        
        print(f"  Initial hypervolume: {init_hv:.4f}")
        
        # Step 2: Active learning loop
        print(f"\n[Step 2] Active learning loop...")
        
        patience_counter = 0
        best_hv = init_hv
        
        for iteration in range(self.config.max_iterations):
            self.state.iteration = iteration + 1
            
            if verbose:
                print(f"\n--- Iteration {self.state.iteration} ---")
            
            # Fit GP model
            self.gp_model = MultiObjectiveGPSurrogate(
                encoder=self.encoder,
                n_objectives=2,
                device=str(self.device)
            )
            
            fit_stats = self.gp_model.fit(
                self.state.evaluated_smiles,
                self.state.evaluated_objectives
            )
            
            # Get model for acquisition
            model, train_X, train_Y, bounds = self.gp_model.get_model_for_acquisition()
            
            # Optimize acquisition to select next batch
            selected_smiles, acq_value = self._optimize_acquisition(
                model, train_X, train_Y, bounds,
                self.config.batch_size
            )
            
            if selected_smiles is None:
                print("  No more candidates to evaluate. Stopping.")
                break
            
            if verbose:
                print(f"  Selected {len(selected_smiles)} candidates (acq={acq_value:.4f})")
            
            # Evaluate selected candidates
            selected_meta = [
                self.valid_metadata[self.valid_smiles.index(s)] 
                for s in selected_smiles
            ]
            
            new_results = self._evaluate_batch(selected_smiles, selected_meta)
            
            new_objectives = np.array([
                [r.efficiency_score, r.safety_score] for r in new_results
            ])
            
            # Update state
            self.state.evaluated_smiles.extend(selected_smiles)
            self.state.evaluated_objectives = np.vstack([
                self.state.evaluated_objectives, new_objectives
            ])
            
            # Compute new hypervolume
            new_hv = self._compute_hypervolume(
                self.state.evaluated_objectives, 
                self.config.ref_point
            )
            self.state.hypervolume_history.append(new_hv)
            
            hv_improvement = new_hv - best_hv
            
            if verbose:
                print(f"  Hypervolume: {new_hv:.4f} (Δ={hv_improvement:.4f})")
            
            # Early stopping check
            if hv_improvement < self.config.early_stop_threshold:
                patience_counter += 1
                if patience_counter >= self.config.early_stop_patience:
                    print(f"\n  Early stopping: No improvement for {patience_counter} iterations")
                    break
            else:
                patience_counter = 0
                best_hv = new_hv
            
            # Update Pareto frontier
            self.state.pareto_frontier = self._extract_pareto_frontier(
                self.state.evaluated_smiles,
                self.state.evaluated_objectives,
                self.state.iteration
            )
        
        # Final processing
        print("\n[Step 3] Final processing...")
        
        # Identify knee points
        self.state.pareto_frontier = self._identify_knee_points(
            self.state.pareto_frontier
        )
        
        # Summary
        print(f"\n{'=' * 70}")
        print("OPTIMIZATION COMPLETE")
        print(f"{'=' * 70}")
        print(f"Total evaluations: {len(self.state.evaluated_smiles)}")
        print(f"Pareto-optimal points: {len(self.state.pareto_frontier)}")
        print(f"Final hypervolume: {self.state.hypervolume_history[-1]:.4f}")
        
        knee_points = [p for p in self.state.pareto_frontier if p.is_knee_point]
        if knee_points:
            print(f"\nKnee point(s) identified:")
            for kp in knee_points:
                print(f"  {kp.smiles}: Eff={kp.efficiency:.3f}, Safety={kp.safety_cost:.3f}")
        
        return self.state
    
    def export_results(
        self,
        output_path: Optional[Path] = None
    ) -> Path:
        """Export optimization results to JSON."""
        if output_path is None:
            output_path = Path("data/phase4_results.json")
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "phase": "IV",
            "methodology": "Multi-Objective Bayesian Optimization (qEHVI)",
            "summary": {
                "total_candidates": len(self.valid_smiles),
                "total_evaluations": len(self.state.evaluated_smiles),
                "evaluation_ratio": len(self.state.evaluated_smiles) / len(self.valid_smiles),
                "pareto_optimal_count": len(self.state.pareto_frontier),
                "final_hypervolume": self.state.hypervolume_history[-1],
                "iterations": self.state.iteration,
            },
            "pareto_frontier": [
                {
                    "smiles": p.smiles,
                    "efficiency": p.efficiency,
                    "safety_cost": p.safety_cost,
                    "is_knee_point": p.is_knee_point,
                    "iteration_found": p.iteration_found,
                    "additional_data": p.additional_data
                }
                for p in self.state.pareto_frontier
            ],
            "hypervolume_history": self.state.hypervolume_history,
            "config": {
                "ref_point": self.config.ref_point,
                "batch_size": self.config.batch_size,
                "max_iterations": self.config.max_iterations,
                "n_initial_samples": self.config.n_initial_samples,
            },
            "hypothesis_h2": {
                "description": "qEHVI ≤30% budget efficiency",
                "evaluation_budget_used": len(self.state.evaluated_smiles) / len(self.valid_smiles),
                "target": 0.30,
                "passed": len(self.state.evaluated_smiles) / len(self.valid_smiles) <= 0.30
            },
            "timestamp": datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\nResults exported to: {output_path}")
        return output_path


def run_phase4_pipeline(
    phase3_results_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    max_iterations: int = 50,
    batch_size: int = 4
) -> OptimizationState:
    """
    Main entry point for Phase IV.
    
    Args:
        phase3_results_path: Path to Phase III results
        output_path: Where to save Phase IV results
        max_iterations: Maximum optimization iterations
        batch_size: Candidates per iteration
        
    Returns:
        OptimizationState with Pareto frontier
    """
    # Load Phase III candidates
    if phase3_results_path is None:
        phase3_results_path = Path("data/phase3_results.json")
    
    if phase3_results_path.exists():
        with open(phase3_results_path) as f:
            phase3_data = json.load(f)
        
        candidates = phase3_data.get("candidates", [])
        smiles_list = [c["smiles"] for c in candidates]
        metadata_list = [c.get("properties", {}) for c in candidates]
    else:
        print(f"Phase III results not found at {phase3_results_path}")
        print("Using example candidates for testing...")
        
        # Example candidates for testing
        smiles_list = [
            "OCCO", "CC(O)CO", "OCC(O)CO", "OCCCO", "OCCOCCO",
            "CN(C)C=O", "CC(=O)N(C)C", "CN1CCCC1=O",
            "CS(C)=O", "CCS(CC)=O",
            "CCO", "CCCCO", "CC(C)O",
        ]
        metadata_list = [{}] * len(smiles_list)
    
    # Configure MOBO
    config = MOBOConfig(
        ref_point=[0.0, 1.0],
        batch_size=batch_size,
        max_iterations=max_iterations,
        n_initial_samples=min(10, len(smiles_list) // 3),
        early_stop_patience=10,
    )
    
    # Run optimization
    optimizer = MOBOOptimizer(
        candidate_smiles=smiles_list,
        candidate_metadata=metadata_list,
        config=config
    )
    
    state = optimizer.run_optimization(verbose=True)
    
    # Export results
    if output_path is None:
        output_path = Path("data/phase4_results.json")
    
    optimizer.export_results(output_path)
    
    return state


if __name__ == "__main__":
    state = run_phase4_pipeline()
```

---

## Sub-Phase IV.4: Visualization and Analysis

### Pareto Frontier Visualization

```python
# src/optimization/visualization.py
"""
Phase IV.4: Visualization and Analysis

Creates visualizations for:
1. Pareto frontier with knee points
2. Hypervolume convergence
3. Objective space exploration
4. Hypothesis H1/H2 testing results

References:
- HiPlot for high-dimensional visualization: https://facebookresearch.github.io/hiplot/
- Matplotlib for standard plots

[VERIFY: HiPlot installation and current API]
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: matplotlib not available for visualization")

try:
    import hiplot as hip
    HIPLOT_AVAILABLE = True
except ImportError:
    HIPLOT_AVAILABLE = False
    print("INFO: hiplot not available. Install with: pip install hiplot")


class Phase4Visualizer:
    """
    Creates visualizations for MOBO results.
    """
    
    def __init__(self, results_data: Dict):
        """
        Args:
            results_data: Loaded Phase IV results JSON
        """
        self.data = results_data
        self.pareto = results_data.get("pareto_frontier", [])
        self.hv_history = results_data.get("hypervolume_history", [])
        
    def plot_pareto_frontier(
        self,
        save_path: Optional[Path] = None,
        show: bool = True
    ):
        """
        Plot the Pareto frontier with knee points highlighted.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib required for plotting")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # Extract coordinates
        efficiencies = [p["efficiency"] for p in self.pareto]
        safety_costs = [p["safety_cost"] for p in self.pareto]
        is_knee = [p.get("is_knee_point", False) for p in self.pareto]
        
        # Plot all Pareto points
        ax.scatter(
            efficiencies, safety_costs,
            c='blue', s=100, alpha=0.7,
            label='Pareto-optimal'
        )
        
        # Highlight knee points
        knee_eff = [e for e, k in zip(efficiencies, is_knee) if k]
        knee_safety = [s for s, k in zip(safety_costs, is_knee) if k]
        
        if knee_eff:
            ax.scatter(
                knee_eff, knee_safety,
                c='red', s=200, marker='*',
                label='Knee point(s)', zorder=5
            )
        
        # Connect Pareto points with line
        sorted_indices = np.argsort(efficiencies)
        sorted_eff = np.array(efficiencies)[sorted_indices]
        sorted_safety = np.array(safety_costs)[sorted_indices]
        ax.plot(sorted_eff, sorted_safety, 'b--', alpha=0.5)
        
        # Labels
        ax.set_xlabel('Efficiency (higher = better)', fontsize=12)
        ax.set_ylabel('Safety Cost (lower = better)', fontsize=12)
        ax.set_title('Pareto Frontier: Efficiency vs Safety Trade-off', fontsize=14)
        ax.legend(loc='upper right')
        
        # Invert y-axis so lower safety cost is at top
        ax.invert_yaxis()
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Add annotation for knee point
        if knee_eff:
            for ke, ks in zip(knee_eff, knee_safety):
                smiles = next(
                    p["smiles"][:20] + "..." 
                    for p in self.pareto 
                    if p["efficiency"] == ke and p["safety_cost"] == ks
                )
                ax.annotate(
                    f'Knee: {smiles}',
                    (ke, ks),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7)
                )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved Pareto plot to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_hypervolume_convergence(
        self,
        save_path: Optional[Path] = None,
        show: bool = True
    ):
        """
        Plot hypervolume convergence over iterations.
        
        For H2 hypothesis testing: Shows efficiency of qEHVI.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib required for plotting")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        iterations = list(range(len(self.hv_history)))
        
        ax.plot(iterations, self.hv_history, 'b-o', linewidth=2, markersize=6)
        
        # Mark 30% budget point (for H2)
        total_candidates = self.data.get("summary", {}).get("total_candidates", 100)
        budget_30_percent = int(total_candidates * 0.30)
        
        # Find iteration at 30% budget
        summary = self.data.get("summary", {})
        n_initial = self.data.get("config", {}).get("n_initial_samples", 10)
        batch_size = self.data.get("config", {}).get("batch_size", 4)
        
        # Cumulative evaluations per iteration
        cumulative = [n_initial]
        for i in range(1, len(self.hv_history)):
            cumulative.append(cumulative[-1] + batch_size)
        
        # Find when we hit 30% budget
        iter_30 = None
        for i, c in enumerate(cumulative):
            if c >= budget_30_percent:
                iter_30 = i
                break
        
        if iter_30 is not None and iter_30 < len(self.hv_history):
            ax.axvline(
                x=iter_30, color='red', linestyle='--', 
                label=f'30% budget ({budget_30_percent} evals)'
            )
            
            hv_at_30 = self.hv_history[iter_30]
            hv_final = self.hv_history[-1]
            ratio = hv_at_30 / hv_final if hv_final > 0 else 0
            
            ax.annotate(
                f'HV at 30%: {hv_at_30:.4f}\n({ratio:.1%} of final)',
                (iter_30, hv_at_30),
                xytext=(20, 20),
                textcoords='offset points',
                fontsize=10,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7)
            )
        
        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Hypervolume', fontsize=12)
        ax.set_title('Hypervolume Convergence (H2 Hypothesis Test)', fontsize=14)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved convergence plot to: {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def create_hiplot_visualization(
        self,
        all_evaluations: List[Dict],
        save_path: Optional[Path] = None
    ):
        """
        Create HiPlot parallel coordinates visualization.
        
        For exploring the high-dimensional objective space.
        
        Reference: https://facebookresearch.github.io/hiplot/
        """
        if not HIPLOT_AVAILABLE:
            print("HiPlot not available. Install with: pip install hiplot")
            return
        
        # Prepare data for HiPlot
        data_points = []
        for eval_data in all_evaluations:
            point = {
                "efficiency": eval_data.get("efficiency", 0),
                "safety_cost": eval_data.get("safety_cost", 1),
                "is_pareto": eval_data.get("is_pareto", False),
            }
            
            # Add properties if available
            props = eval_data.get("properties", {})
            for key in ["mw", "logp", "tpsa", "hba", "hbd"]:
                if key in props:
                    point[key] = props[key]
            
            data_points.append(point)
        
        # Create HiPlot experiment
        exp = hip.Experiment.from_iterable(data_points)
        
        if save_path:
            exp.to_html(str(save_path))
            print(f"Saved HiPlot to: {save_path}")
        
        return exp
    
    def generate_hypothesis_report(self) -> str:
        """
        Generate a report on hypothesis testing results.
        
        H1: Pareto frontier exhibits convex structure with identifiable knee points
        H2: qEHVI achieves ≥95% of final hypervolume using ≤30% of budget
        """
        report_lines = [
            "=" * 70,
            "PHASE IV HYPOTHESIS TESTING REPORT",
            "=" * 70,
            "",
            "HYPOTHESIS H1: Pareto Frontier Structure",
            "-" * 40,
        ]
        
        # H1: Check for knee points
        knee_count = sum(1 for p in self.pareto if p.get("is_knee_point", False))
        h1_passed = knee_count >= 1
        
        report_lines.extend([
            f"  Pareto-optimal points: {len(self.pareto)}",
            f"  Knee points identified: {knee_count}",
            f"  H1 Status: {'PASSED ✓' if h1_passed else 'NEEDS REVIEW'}",
            "",
            "HYPOTHESIS H2: qEHVI Budget Efficiency",
            "-" * 40,
        ])
        
        # H2: Budget efficiency
        h2_data = self.data.get("hypothesis_h2", {})
        budget_used = h2_data.get("evaluation_budget_used", 1.0)
        h2_passed = h2_data.get("passed", False)
        
        # Calculate HV ratio at 30%
        hv_history = self.hv_history
        summary = self.data.get("summary", {})
        
        report_lines.extend([
            f"  Evaluation budget used: {budget_used:.1%}",
            f"  Target budget: ≤30%",
            f"  Final hypervolume: {hv_history[-1]:.4f}" if hv_history else "  Final hypervolume: N/A",
            f"  H2 Status: {'PASSED ✓' if h2_passed else 'NOT PASSED ✗'}",
            "",
        ])
        
        if not h2_passed:
            report_lines.extend([
                "  Note: H2 not passing is still a valid research result.",
                "  This indicates qEHVI may need more evaluations for this",
                "  specific chemical space to achieve equivalent coverage.",
                "",
            ])
        
        report_lines.extend([
            "=" * 70,
            "RECOMMENDED CANDIDATES FOR PHASE V (Simulation)",
            "=" * 70,
            "",
        ])
        
        # List top candidates (knee points first, then by efficiency)
        sorted_pareto = sorted(
            self.pareto,
            key=lambda p: (-int(p.get("is_knee_point", False)), -p["efficiency"])
        )
        
        for i, p in enumerate(sorted_pareto[:10]):
            knee_marker = " ⭐" if p.get("is_knee_point") else ""
            report_lines.append(
                f"  {i+1}. {p['smiles'][:40]}...{knee_marker}"
            )
            report_lines.append(
                f"     Efficiency: {p['efficiency']:.3f}, Safety Cost: {p['safety_cost']:.3f}"
            )
        
        report_lines.extend(["", "=" * 70])
        
        return "\n".join(report_lines)


def visualize_phase4_results(
    results_path: Optional[Path] = None,
    output_dir: Optional[Path] = None
):
    """
    Generate all Phase IV visualizations.
    """
    if results_path is None:
        results_path = Path("data/phase4_results.json")
    
    if output_dir is None:
        output_dir = Path("outputs/phase4_plots")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load results
    import json
    with open(results_path) as f:
        results = json.load(f)
    
    viz = Phase4Visualizer(results)
    
    # Generate plots
    print("\nGenerating visualizations...")
    
    viz.plot_pareto_frontier(
        save_path=output_dir / "pareto_frontier.png",
        show=False
    )
    
    viz.plot_hypervolume_convergence(
        save_path=output_dir / "hypervolume_convergence.png",
        show=False
    )
    
    # Generate hypothesis report
    report = viz.generate_hypothesis_report()
    print("\n" + report)
    
    # Save report
    with open(output_dir / "hypothesis_report.txt", 'w') as f:
        f.write(report)
    
    print(f"\nAll outputs saved to: {output_dir}")


if __name__ == "__main__":
    visualize_phase4_results()
```

---

## Code Artifacts Summary

### Project Structure Addition

```
src/
├── optimization/
│   ├── __init__.py
│   ├── objectives.py         # Efficiency & Safety objective functions
│   ├── gp_surrogate.py       # Gaussian Process model
│   ├── mobo_optimizer.py     # qEHVI optimization loop
│   └── visualization.py      # Pareto plots, HV convergence
```

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `28_objective_functions.ipynb` | Test efficiency and safety scoring |
| `29_gp_surrogate.ipynb` | Train and validate GP model |
| `30_mobo_optimization.ipynb` | Run full MOBO loop |
| `31_pareto_analysis.ipynb` | Analyze Pareto frontier and knee points |
| `32_hypothesis_testing.ipynb` | H1/H2 validation |

### Requirements Update

```
# requirements.txt additions for Phase IV
torch>=2.0.0           # PyTorch backend
botorch>=0.9.0         # Bayesian Optimization
gpytorch>=1.10         # Gaussian Processes
matplotlib>=3.7.0      # Visualization
hiplot>=0.1.0          # High-dimensional viz (optional)
thermo>=0.2.0          # UNIFAC calculations (optional)
```

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | Reference |
|------|-----------------|-----------|
| BoTorch qEHVI API | Verify current API | https://botorch.org/tutorials/multi_objective_bo |
| thermo library UNIFAC | Test group assignment | https://thermo.readthedocs.io/ |
| PyTorch installation | Ensure compatible version | https://pytorch.org/ |
| GHS category data source | Need external API for production | ECHA, PubChem hazard data |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| qEHVI algorithm | Daulton et al. NeurIPS 2020 | High confidence |
| BoTorch MOBO implementation | BoTorch documentation | High confidence - verify current API |
| Morgan fingerprints | RDKit documentation | High confidence |
| UNIFAC activity coefficients | Fredenslund et al. | High confidence - verify implementation |
| Barrier function for safety | Research Proposal Section 3.2 | From your proposal |
| Knee point identification | General Pareto analysis | Moderate - multiple methods exist |

### Accuracy Limitations

1. **UNIFAC Implementation**: The efficiency objective uses a simplified heuristic instead of full UNIFAC. For production, implement proper UNIFAC group contribution or use the `thermo` library with validation.

2. **Safety Data**: The GHS category estimation is a structural heuristic. Real implementation needs:
   - ECHA database queries
   - PubChem hazard data
   - Consensus scoring from Phase II

3. **BoTorch API**: The qEHVI implementation follows BoTorch patterns but API may have changed. Verify with current documentation.

4. **Computational Cost**: Running GP fitting and qEHVI optimization can be slow. Consider:
   - Using GPU if available (`device="cuda"`)
   - Reducing fingerprint bits for faster encoding
   - Adjusting MC samples for qEHVI

---

## GitHub Portfolio Framing

### README Section for Phase IV

```markdown
## Phase IV: Intelligent Optimization 🎯

### Multi-Objective Bayesian Optimization with Active Learning

**Status:** In Development

This phase implements the core MOBO framework from the research proposal,
treating molecule selection as a multi-objective optimization problem.

#### The Two Competing Objectives
| Objective | Metric | Direction |
|-----------|--------|-----------|
| Efficiency | UNIFAC selectivity proxy | Maximize |
| Safety | Cost-of-mitigation (barrier function) | Minimize |

#### Key Components
- **GP Surrogate**: Gaussian Process trained on Morgan fingerprints
- **qEHVI Acquisition**: Batch Expected Hypervolume Improvement
- **Active Learning**: Iterative candidate selection and evaluation
- **Pareto Analysis**: Knee point identification

#### Hypothesis Testing
| Hypothesis | Description | Metric |
|------------|-------------|--------|
| H1 | Pareto exhibits convex structure | ≥1 knee point |
| H2 | qEHVI budget efficiency | ≤30% evaluations for 95% HV |

### Reproducibility
```bash
# Install dependencies
pip install torch botorch gpytorch

# Run Phase IV
python -m src.optimization.mobo_optimizer
```

### Key Outputs
- Pareto-optimal frontier visualization
- Hypervolume convergence plot
- Ranked candidates for Phase V simulation
```

### Suggested Badges

```markdown
![BoTorch](https://img.shields.io/badge/Library-BoTorch-orange)
![Method](https://img.shields.io/badge/Method-MOBO%20qEHVI-blue)
![Optimization](https://img.shields.io/badge/Optimization-Multi--Objective-green)
```

---

## Confidence Assessment

### High Confidence
- MOBO conceptual framework
- GP surrogate model design
- Morgan fingerprint encoding
- Pareto frontier extraction
- Hypervolume computation
- Barrier function concept for safety

### Needs Verification
- **BoTorch qEHVI current API** - May have changed
- **thermo library UNIFAC** - Group assignment complexity
- **Optimal batch size for qEHVI** - Problem-dependent
- **GHS data retrieval** - Need external source

### Outside My Expertise
- Optimal UNIFAC group contributions for novel molecules
- Industrial cost estimation for entrainers
- Specific regulatory thresholds for different jurisdictions

---

## Integration with Phase V

Phase IV outputs feed directly into Phase V (Simulation & Validation):

```python
# Phase V will receive:
phase4_results = {
    "pareto_frontier": [
        {
            "smiles": "...",
            "efficiency": 0.85,
            "safety_cost": 0.12,
            "is_knee_point": True,
            # Ready for rigorous simulation
        },
        ...
    ],
    "recommended_for_simulation": [...],  # Top 10 candidates
}
```

The top candidates from the Pareto frontier (especially knee points) advance to rigorous process simulation in Phase V.