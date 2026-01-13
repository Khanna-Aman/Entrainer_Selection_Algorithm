# 🎯 Phase II-C Implementation: Cheminformatics & Diversity Clustering - Engine C

## Understanding Check

From the provided documents, I understand that:

1. **Engine C's Role**: This is the third parallel analytical engine in Phase II's Multi-Vector Initial Selection. Unlike Engine A (literature-grounded Graph-RAG) and Engine B (TRIZ-based innovation heuristics), Engine C takes a **purely algorithmic, data-driven approach** using established cheminformatics principles.

2. **Input**: The molecular search space (clusters defined in Phase I, approximately 500 clusters representing the "hot spots" from the domain mapping phase)

3. **Process**: 
   - Use RDKit for descriptor calculation
   - Convert molecules into numerical vectors
   - Apply diversity clustering to ensure mathematical diversity
   - Avoid selecting molecules that are merely structural variations of each other

4. **Output**: 25-50 molecules that are **structurally diverse** and complement the selections from Engines A and B

5. **Key Differentiation**: While Engines A and B use AI/heuristic reasoning, Engine C provides a rigorous, reproducible, algorithmic baseline that ensures the final selection covers the structural space without redundancy.

---

## Recommended Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│          ENGINE C: CHEMINFORMATICS & DIVERSITY CLUSTERING        │
├─────────────────────────────────────────────────────────────────────────┤
│                                       │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │           MOLECULE RETRIEVAL                │ │
│ │ - Load Phase I cluster definitions              │ │
│ │ - Query PubChem/databases for molecules in each cluster     │ │
│ │ - Apply initial property filters (MW, BP, safety flags)     │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                   │                   │
│                   ▼                   │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │           DESCRIPTOR CALCULATION (RDKit)          │ │
│ │ - Morgan Fingerprints (ECFP4) for structural similarity     │ │
│ │ - Physicochemical descriptors (MW, LogP, TPSA, HBD, HBA)    │ │
│ │ - Custom entrainer-relevant descriptors           │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                   │                   │
│                   ▼                   │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │           DIVERSITY ANALYSIS                │ │
│ │ - Compute pairwise Tanimoto similarity matrix         │ │
│ │ - Identify structural clusters via hierarchical clustering   │ │
│ │ - Visualize chemical space (t-SNE/UMAP)            │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                   │                   │
│                   ▼                   │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │           DIVERSITY SELECTION                │ │
│ │ - MaxMin picker for maximum diversity             │ │
│ │ - Ensure coverage across Phase I mechanism clusters       │ │
│ │ - Property-weighted selection (optional)           │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                   │                   │
│                   ▼                   │
│ ┌───────────────────────────────────────────────────────────────────┐ │
│ │           OUTPUT: 25-50 Diverse Molecules          │ │
│ │ - SMILES, names, calculated properties            │ │
│ │ - Diversity metrics and cluster assignments          │ │
│ │ - Overlap flags with Engines A/B               │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Sub-Phase II-C.1: Molecule Retrieval and Initial Filtering

### Connecting to Phase I Clusters

Engine C should leverage the cluster definitions from Phase I. We'll query the molecular databases for compounds matching each cluster's SMARTS pattern and property ranges.

```python
# src/cheminformatics/molecule_retrieval.py
"""
Phase II-C.1: Molecule Retrieval for Diversity Clustering

This module retrieves molecules from the Phase I cluster definitions
and applies initial property-based filters.

References:
- RDKit Documentation: https://www.rdkit.org/docs/
- PubChem PUG REST: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
"""

import requests
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import json

# RDKit imports
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("WARNING: RDKit not available. Install with: pip install rdkit")

@dataclass
class MoleculeCandidate:
    """A molecule candidate for diversity analysis"""
    smiles: str
    name: str
    cid: Optional[int] = None  # PubChem CID
    cas: Optional[str] = None
    cluster_id: str = ""
    molecular_weight: Optional[float] = None
    logp: Optional[float] = None
    tpsa: Optional[float] = None
    hbd: Optional[int] = None  # H-bond donors
    hba: Optional[int] = None  # H-bond acceptors
    rotatable_bonds: Optional[int] = None
    source: str = "pubchem"
    
    def to_dict(self) -> dict:
        return {
            "smiles": self.smiles,
            "name": self.name,
            "cid": self.cid,
            "cas": self.cas,
            "cluster_id": self.cluster_id,
            "molecular_weight": self.molecular_weight,
            "logp": self.logp,
            "tpsa": self.tpsa,
            "hbd": self.hbd,
            "hba": self.hba,
            "rotatable_bonds": self.rotatable_bonds,
            "source": self.source
        }

@dataclass
class PropertyFilter:
    """Filter criteria for initial molecule screening"""
    min_mw: float = 50.0
    max_mw: float = 500.0
    min_bp: Optional[float] = 100.0  # Boiling point > ethanol
    max_bp: Optional[float] = 300.0
    min_hba: int = 1  # At least one H-bond acceptor
    max_logp: float = 3.0  # Not too lipophilic
    exclude_elements: Set[str] = field(default_factory=lambda: {"F", "Cl", "Br", "I"})
    # Exclude halogens for safety (can be relaxed)

class MoleculeRetriever:
    """
    Retrieves molecules from databases based on Phase I cluster definitions.
    
    Primary source: PubChem (free, comprehensive)
    Secondary: ChEMBL (if needed for additional data)
    """
    
    PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def __init__(self, rate_limit_delay: float = 0.25):
        """
        Args:
            rate_limit_delay: Seconds between API requests
                PubChem allows ~5 requests/second without API key
                Reference: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
        """
        self.rate_limit_delay = rate_limit_delay
        self.request_count = 0
        
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.rate_limit_delay)
        self.request_count += 1
        
    def search_by_smarts(
        self, 
        smarts: str, 
        max_results: int = 100
    ) -> List[int]:
        """
        Search PubChem for compounds matching a SMARTS pattern.
        
        Note: PubChem substructure search can be slow for complex patterns.
        
        Args:
            smarts: SMARTS pattern to search
            max_results: Maximum CIDs to return
            
        Returns:
            List of PubChem CIDs
        """
        self._rate_limit()
        
        # Use PubChem's substructure search
        # Reference: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest#section=Substructure
        url = f"{self.PUBCHEM_BASE}/compound/fastsubstructure/smarts/{smarts}/cids/JSON"
        
        params = {"MaxRecords": max_results}
        
        try:
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                cids = data.get("IdentifierList", {}).get("CID", [])
                return cids[:max_results]
            elif response.status_code == 404:
                return []  # No matches
            else:
                print(f"SMARTS search error: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"SMARTS search timeout for: {smarts[:50]}...")
            return []
        except Exception as e:
            print(f"SMARTS search error: {e}")
            return []
    
    def get_compound_properties(
        self, 
        cids: List[int],
        batch_size: int = 100
    ) -> List[Dict]:
        """
        Fetch properties for a list of PubChem CIDs.
        
        Args:
            cids: List of PubChem Compound IDs
            batch_size: How many CIDs per request (max 100 recommended)
            
        Returns:
            List of property dictionaries
        """
        all_properties = []
        
        # Properties to request
        # Reference: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest#section=Compound-Property-Tables
        prop_list = [
            "MolecularWeight",
            "XLogP",
            "TPSA",
            "HBondDonorCount", 
            "HBondAcceptorCount",
            "RotatableBondCount",
            "CanonicalSMILES",
            "IUPACName"
        ]
        
        for i in range(0, len(cids), batch_size):
            batch = cids[i:i + batch_size]
            cid_str = ",".join(map(str, batch))
            
            self._rate_limit()
            
            url = f"{self.PUBCHEM_BASE}/compound/cid/{cid_str}/property/{','.join(prop_list)}/JSON"
            
            try:
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    properties = data.get("PropertyTable", {}).get("Properties", [])
                    all_properties.extend(properties)
                else:
                    print(f"Property fetch error: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"Property fetch error: {e}")
                
        return all_properties
    
    def retrieve_from_cluster(
        self,
        cluster: Dict,
        property_filter: PropertyFilter,
        max_molecules: int = 50
    ) -> List[MoleculeCandidate]:
        """
        Retrieve molecules matching a Phase I cluster definition.
        
        Args:
            cluster: Cluster definition with keys: cluster_id, smarts_pattern, mw_range
            property_filter: Filter criteria
            max_molecules: Maximum molecules to retrieve per cluster
            
        Returns:
            List of MoleculeCandidate objects
        """
        cluster_id = cluster.get("cluster_id", "unknown")
        smarts = cluster.get("smarts_pattern", "")
        
        if not smarts:
            print(f"Cluster {cluster_id} has no SMARTS pattern")
            return []
            
        print(f"Searching cluster: {cluster_id}...")
        
        # Search for matching compounds
        cids = self.search_by_smarts(smarts, max_results=max_molecules * 2)
        
        if not cids:
            print(f"  No compounds found for {cluster_id}")
            return []
            
        print(f"  Found {len(cids)} CIDs, fetching properties...")
        
        # Get properties
        properties = self.get_compound_properties(cids)
        
        # Convert to candidates and filter
        candidates = []
        
        for prop in properties:
            try:
                smiles = prop.get("CanonicalSMILES", "")
                mw = prop.get("MolecularWeight", 0)
                logp = prop.get("XLogP")
                
                # Apply filters
                if mw < property_filter.min_mw or mw > property_filter.max_mw:
                    continue
                if logp is not None and logp > property_filter.max_logp:
                    continue
                    
                hba = prop.get("HBondAcceptorCount", 0)
                if hba < property_filter.min_hba:
                    continue
                
                # Check for excluded elements (simplified)
                if property_filter.exclude_elements:
                    if RDKIT_AVAILABLE:
                        mol = Chem.MolFromSmiles(smiles)
                        if mol:
                            atoms = {atom.GetSymbol() for atom in mol.GetAtoms()}
                            if atoms & property_filter.exclude_elements:
                                continue
                
                candidate = MoleculeCandidate(
                    smiles=smiles,
                    name=prop.get("IUPACName", ""),
                    cid=prop.get("CID"),
                    cluster_id=cluster_id,
                    molecular_weight=mw,
                    logp=logp,
                    tpsa=prop.get("TPSA"),
                    hbd=prop.get("HBondDonorCount"),
                    hba=hba,
                    rotatable_bonds=prop.get("RotatableBondCount")
                )
                candidates.append(candidate)
                
                if len(candidates) >= max_molecules:
                    break
                    
            except Exception as e:
                continue
                
        print(f"  Retained {len(candidates)} candidates after filtering")
        return candidates
    
    def retrieve_from_all_clusters(
        self,
        clusters: List[Dict],
        property_filter: Optional[PropertyFilter] = None,
        max_per_cluster: int = 30,
        max_total: int = 1000
    ) -> List[MoleculeCandidate]:
        """
        Retrieve molecules from all Phase I clusters.
        
        Args:
            clusters: List of cluster definitions from Phase I
            property_filter: Filter criteria (uses defaults if None)
            max_per_cluster: Max molecules per cluster
            max_total: Total maximum molecules
            
        Returns:
            Combined list of candidates
        """
        if property_filter is None:
            property_filter = PropertyFilter()
            
        all_candidates = []
        seen_smiles = set()
        
        for cluster in clusters:
            candidates = self.retrieve_from_cluster(
                cluster, 
                property_filter, 
                max_per_cluster
            )
            
            # Deduplicate
            for candidate in candidates:
                if candidate.smiles not in seen_smiles:
                    all_candidates.append(candidate)
                    seen_smiles.add(candidate.smiles)
                    
            if len(all_candidates) >= max_total:
                break
                
        print(f"\nTotal unique candidates: {len(all_candidates)}")
        return all_candidates


def load_phase1_clusters(clusters_path: Path) -> List[Dict]:
    """
    Load cluster definitions from Phase I output.
    
    Expected format (from Phase I):
    [
        {
            "cluster_id": "HB_GLYCOL_S",
            "smarts_pattern": "[OX2H][CX4][CX4][OX2H]",
            "mw_range": [50, 150],
            "mechanism": "HYDROGEN_BONDING",
            "priority_score": 1.5
        },
        ...
    ]
    """
    if not clusters_path.exists():
        print(f"Clusters file not found: {clusters_path}")
        return []
        
    with open(clusters_path) as f:
        clusters = json.load(f)
        
    return clusters


if __name__ == "__main__":
    # Example usage
    retriever = MoleculeRetriever()
    
    # Example cluster (from Phase I)
    example_clusters = [
        {
            "cluster_id": "HB_GLYCOL_S",
            "smarts_pattern": "[OX2H][CX4][CX4][OX2H]",
            "mw_range": [50, 150]
        },
        {
            "cluster_id": "HB_AMIDE_S", 
            "smarts_pattern": "[NX3]([#6])([#6])[CX3](=[OX1])[#6]",
            "mw_range": [50, 150]
        }
    ]
    
    # Retrieve with default filters
    candidates = retriever.retrieve_from_all_clusters(
        example_clusters,
        max_per_cluster=20,
        max_total=100
    )
    
    print(f"\nRetrieved {len(candidates)} candidates")
    for c in candidates[:5]:
        print(f"  {c.name}: {c.smiles[:30]}... (MW={c.molecular_weight})")
```

---

## Sub-Phase II-C.2: Descriptor Calculation with RDKit

### Molecular Fingerprints and Descriptors

For diversity analysis, we need to convert molecules into numerical vectors. RDKit provides several options:

| Representation | Use Case | Notes |
|----------------|----------|-------|
| Morgan Fingerprints (ECFP) | Structural similarity | Standard for cheminformatics, radius 2 = ECFP4 |
| RDKit Fingerprints | General similarity | RDKit's default topological fingerprint |
| MACCS Keys | Substructure presence | 166 predefined structural keys |
| Physicochemical Descriptors | Property-based similarity | MW, LogP, TPSA, etc. |

**Reference:** RDKit Fingerprints documentation: https://www.rdkit.org/docs/GettingStartedInPython.html#fingerprinting-and-molecular-similarity

```python
# src/cheminformatics/descriptor_calculator.py
"""
Phase II-C.2: Molecular Descriptor Calculation

This module calculates molecular fingerprints and descriptors
for diversity analysis using RDKit.

References:
- RDKit Fingerprints: https://www.rdkit.org/docs/GettingStartedInPython.html#fingerprinting-and-molecular-similarity
- RDKit Descriptors: https://www.rdkit.org/docs/GettingStartedInPython.html#list-of-available-descriptors
"""

from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
    from rdkit.Chem import MACCSkeys
    from rdkit import DataStructs
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("ERROR: RDKit is required for Engine C. Install with: pip install rdkit")

@dataclass
class MolecularDescriptors:
    """Container for calculated molecular descriptors"""
    smiles: str
    morgan_fp: Optional[np.ndarray] = None  # Morgan fingerprint as numpy array
    maccs_fp: Optional[np.ndarray] = None   # MACCS keys as numpy array
    physicochemical: Optional[Dict[str, float]] = None
    valid: bool = True
    error: Optional[str] = None

class DescriptorCalculator:
    """
    Calculates molecular descriptors for diversity analysis.
    
    Descriptor Sets:
    1. Morgan Fingerprints (ECFP4): Circular fingerprints for structural similarity
    2. MACCS Keys: 166 structural keys
    3. Physicochemical: MW, LogP, TPSA, HBD, HBA, RotBonds, etc.
    4. Entrainer-specific: Custom descriptors relevant to separation
    """
    
    # Physicochemical descriptors relevant to entrainer selection
    # Reference: Perry's Handbook, separation science literature
    PHYSICOCHEMICAL_DESCRIPTORS = [
        ("MolWt", Descriptors.MolWt),
        ("LogP", Descriptors.MolLogP),
        ("TPSA", Descriptors.TPSA),
        ("HBondDonors", Descriptors.NumHDonors),
        ("HBondAcceptors", Descriptors.NumHAcceptors),
        ("RotatableBonds", Descriptors.NumRotatableBonds),
        ("HeavyAtomCount", Descriptors.HeavyAtomCount),
        ("RingCount", Descriptors.RingCount),
        ("AromaticRings", Descriptors.NumAromaticRings),
        ("FractionCSP3", Descriptors.FractionCSP3),  # Fraction sp3 carbons
    ]
    
    # Additional descriptors for entrainer analysis
    # These capture H-bonding capacity which is critical for water affinity
    ENTRAINER_DESCRIPTORS = [
        ("NumHeteroatoms", lambda m: rdMolDescriptors.CalcNumHeteroatoms(m)),
        ("NumAmideBonds", lambda m: rdMolDescriptors.CalcNumAmideBonds(m)),
        # Ratio of H-bond acceptors to MW (normalized H-bonding capacity)
        ("HBA_per_MW", lambda m: Descriptors.NumHAcceptors(m) / max(Descriptors.MolWt(m), 1)),
        # Ratio of polar surface area to total surface area
        ("TPSA_per_MW", lambda m: Descriptors.TPSA(m) / max(Descriptors.MolWt(m), 1)),
    ]
    
    def __init__(
        self,
        morgan_radius: int = 2,
        morgan_bits: int = 2048,
        include_entrainer_descriptors: bool = True
    ):
        """
        Args:
            morgan_radius: Radius for Morgan fingerprints (2 = ECFP4)
            morgan_bits: Number of bits for Morgan fingerprint
            include_entrainer_descriptors: Include custom entrainer-relevant descriptors
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit is required for DescriptorCalculator")
            
        self.morgan_radius = morgan_radius
        self.morgan_bits = morgan_bits
        self.include_entrainer_descriptors = include_entrainer_descriptors
        
    def calculate_morgan_fingerprint(
        self, 
        mol: Chem.Mol
    ) -> np.ndarray:
        """
        Calculate Morgan (ECFP) fingerprint.
        
        Args:
            mol: RDKit Mol object
            
        Returns:
            numpy array of fingerprint bits
        """
        fp = AllChem.GetMorganFingerprintAsBitVect(
            mol, 
            self.morgan_radius, 
            nBits=self.morgan_bits
        )
        
        # Convert to numpy array
        arr = np.zeros((self.morgan_bits,), dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    
    def calculate_maccs_keys(
        self, 
        mol: Chem.Mol
    ) -> np.ndarray:
        """
        Calculate MACCS keys fingerprint (166 bits).
        
        Args:
            mol: RDKit Mol object
            
        Returns:
            numpy array of 166 bits
        """
        fp = MACCSkeys.GenMACCSKeys(mol)
        arr = np.zeros((167,), dtype=np.int8)  # MACCS is 167 bits (0-166)
        DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    
    def calculate_physicochemical(
        self, 
        mol: Chem.Mol
    ) -> Dict[str, float]:
        """
        Calculate physicochemical descriptors.
        
        Args:
            mol: RDKit Mol object
            
        Returns:
            Dictionary of descriptor values
        """
        descriptors = {}
        
        for name, func in self.PHYSICOCHEMICAL_DESCRIPTORS:
            try:
                descriptors[name] = func(mol)
            except Exception:
                descriptors[name] = np.nan
                
        if self.include_entrainer_descriptors:
            for name, func in self.ENTRAINER_DESCRIPTORS:
                try:
                    descriptors[name] = func(mol)
                except Exception:
                    descriptors[name] = np.nan
                    
        return descriptors
    
    def calculate_all(
        self, 
        smiles: str
    ) -> MolecularDescriptors:
        """
        Calculate all descriptors for a molecule.
        
        Args:
            smiles: SMILES string
            
        Returns:
            MolecularDescriptors object with all calculated values
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            
            if mol is None:
                return MolecularDescriptors(
                    smiles=smiles,
                    valid=False,
                    error="Invalid SMILES - RDKit could not parse"
                )
            
            return MolecularDescriptors(
                smiles=smiles,
                morgan_fp=self.calculate_morgan_fingerprint(mol),
                maccs_fp=self.calculate_maccs_keys(mol),
                physicochemical=self.calculate_physicochemical(mol),
                valid=True
            )
            
        except Exception as e:
            return MolecularDescriptors(
                smiles=smiles,
                valid=False,
                error=str(e)
            )
    
    def calculate_batch(
        self, 
        smiles_list: List[str],
        show_progress: bool = True
    ) -> List[MolecularDescriptors]:
        """
        Calculate descriptors for a batch of molecules.
        
        Args:
            smiles_list: List of SMILES strings
            show_progress: Print progress updates
            
        Returns:
            List of MolecularDescriptors
        """
        results = []
        n_total = len(smiles_list)
        n_valid = 0
        
        for i, smiles in enumerate(smiles_list):
            desc = self.calculate_all(smiles)
            results.append(desc)
            
            if desc.valid:
                n_valid += 1
                
            if show_progress and (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{n_total} molecules ({n_valid} valid)")
                
        if show_progress:
            print(f"  Complete: {n_valid}/{n_total} valid molecules")
            
        return results
    
    def get_fingerprint_matrix(
        self,
        descriptors: List[MolecularDescriptors],
        fingerprint_type: str = "morgan"
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Create a matrix of fingerprints for similarity analysis.
        
        Args:
            descriptors: List of MolecularDescriptors
            fingerprint_type: "morgan" or "maccs"
            
        Returns:
            Tuple of (fingerprint matrix, list of valid SMILES)
        """
        valid_fps = []
        valid_smiles = []
        
        for desc in descriptors:
            if not desc.valid:
                continue
                
            if fingerprint_type == "morgan" and desc.morgan_fp is not None:
                valid_fps.append(desc.morgan_fp)
                valid_smiles.append(desc.smiles)
            elif fingerprint_type == "maccs" and desc.maccs_fp is not None:
                valid_fps.append(desc.maccs_fp)
                valid_smiles.append(desc.smiles)
                
        if not valid_fps:
            return np.array([]), []
            
        return np.array(valid_fps), valid_smiles
    
    def get_physicochemical_matrix(
        self,
        descriptors: List[MolecularDescriptors],
        normalize: bool = True
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Create a matrix of physicochemical descriptors.
        
        Args:
            descriptors: List of MolecularDescriptors
            normalize: Apply z-score normalization
            
        Returns:
            Tuple of (descriptor matrix, SMILES list, descriptor names)
        """
        valid_descs = []
        valid_smiles = []
        
        for desc in descriptors:
            if not desc.valid or desc.physicochemical is None:
                continue
                
            values = list(desc.physicochemical.values())
            if not any(np.isnan(values)):
                valid_descs.append(values)
                valid_smiles.append(desc.smiles)
                
        if not valid_descs:
            return np.array([]), [], []
            
        matrix = np.array(valid_descs)
        
        # Get descriptor names from first valid entry
        desc_names = list(descriptors[0].physicochemical.keys()) if descriptors else []
        
        if normalize and matrix.shape[0] > 1:
            # Z-score normalization
            mean = np.mean(matrix, axis=0)
            std = np.std(matrix, axis=0)
            std[std == 0] = 1  # Avoid division by zero
            matrix = (matrix - mean) / std
            
        return matrix, valid_smiles, desc_names


def calculate_tanimoto_similarity(
    fp1: np.ndarray, 
    fp2: np.ndarray
) -> float:
    """
    Calculate Tanimoto similarity between two fingerprints.
    
    Tanimoto = |A ∩ B| / |A ∪ B|
    
    For bit vectors: |A ∩ B| / (|A| + |B| - |A ∩ B|)
    
    Reference: Standard cheminformatics similarity metric
    """
    intersection = np.sum(np.logical_and(fp1, fp2))
    union = np.sum(np.logical_or(fp1, fp2))
    
    if union == 0:
        return 0.0
        
    return intersection / union


def calculate_similarity_matrix(
    fps: np.ndarray
) -> np.ndarray:
    """
    Calculate pairwise Tanimoto similarity matrix.
    
    Args:
        fps: Matrix of fingerprints (n_molecules x n_bits)
        
    Returns:
        n_molecules x n_molecules similarity matrix
    """
    n = fps.shape[0]
    sim_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            sim = calculate_tanimoto_similarity(fps[i], fps[j])
            sim_matrix[i, j] = sim
            sim_matrix[j, i] = sim
            
    return sim_matrix


if __name__ == "__main__":
    # Example usage
    if not RDKIT_AVAILABLE:
        print("RDKit required for this module")
        exit(1)
        
    calculator = DescriptorCalculator()
    
    # Test molecules (benchmark from Phase I)
    test_smiles = [
        "OCCO",      # Ethylene glycol
        "CC(O)CO",   # Propylene glycol
        "OCCCO",     # 1,3-propanediol
        "CN(C)C=O",  # DMF
        "CN1CCCC1=O", # NMP
        "CS(C)=O",   # DMSO
    ]
    
    print("Calculating descriptors...")
    results = calculator.calculate_batch(test_smiles)
    
    print("\nPhysicochemical descriptors:")
    for desc in results:
        if desc.valid:
            print(f"\n{desc.smiles}:")
            for name, value in desc.physicochemical.items():
                print(f"  {name}: {value:.2f}" if isinstance(value, float) else f"  {name}: {value}")
    
    # Get fingerprint matrix and calculate similarity
    fp_matrix, smiles_list = calculator.get_fingerprint_matrix(results, "morgan")
    
    print("\nTanimoto similarity matrix:")
    sim_matrix = calculate_similarity_matrix(fp_matrix)
    
    print("     ", "  ".join([s[:6] for s in smiles_list]))
    for i, s in enumerate(smiles_list):
        row = "  ".join([f"{sim_matrix[i,j]:.2f}" for j in range(len(smiles_list))])
        print(f"{s[:6]}  {row}")
```

---

## Sub-Phase II-C.3: Diversity Clustering and Visualization

### Clustering Approaches

For molecular diversity analysis, we use:

1. **Hierarchical Clustering**: Groups molecules into a tree structure based on similarity
2. **k-Medoids Clustering**: Partitions molecules into k clusters with representative molecules
3. **Butina Clustering**: Taylor-Butina clustering specifically designed for molecules

**Reference:** 
- Butina, D. (1999). "Unsupervised Database Clustering Based on Daylight's Fingerprint and Tanimoto Similarity" J. Chem. Inf. Comput. Sci. [DOI: 10.1021/ci9803381]

```python
# src/cheminformatics/diversity_clustering.py
"""
Phase II-C.3: Diversity Clustering for Molecule Selection

This module implements clustering algorithms to analyze and ensure
structural diversity in the molecule selection.

References:
- Butina Clustering: DOI 10.1021/ci9803381
- RDKit Clustering: https://www.rdkit.org/docs/GettingStartedInPython.html
- scikit-learn: https://scikit-learn.org/stable/modules/clustering.html
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import DataStructs
    from rdkit.ML.Cluster import Butina
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

try:
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: scikit-learn not available for advanced clustering")

@dataclass
class ClusterResult:
    """Result from clustering analysis"""
    n_clusters: int
    cluster_assignments: List[int]  # Cluster ID for each molecule
    cluster_sizes: Dict[int, int]   # Size of each cluster
    centroids_indices: List[int]    # Index of centroid/representative per cluster
    smiles_list: List[str]          # Original SMILES for reference

@dataclass 
class DiversityMetrics:
    """Metrics describing the diversity of a molecule set"""
    n_molecules: int
    n_clusters: int
    mean_intra_cluster_similarity: float
    mean_inter_cluster_similarity: float
    diversity_index: float  # 1 - mean_similarity
    coverage_score: float   # How well clusters are represented

class DiversityClustering:
    """
    Performs diversity analysis and clustering on molecules.
    
    Provides:
    1. Butina clustering (RDKit native)
    2. Hierarchical clustering (scikit-learn)
    3. Diversity metrics calculation
    4. Visualization preparation (t-SNE/PCA coordinates)
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Args:
            similarity_threshold: Tanimoto threshold for Butina clustering
                Molecules with similarity > threshold are in same cluster
                Lower = fewer, larger clusters; Higher = more, smaller clusters
                0.7 is a common starting point for diverse selection
        """
        self.similarity_threshold = similarity_threshold
        
    def butina_clustering(
        self,
        smiles_list: List[str],
        fingerprint_type: str = "morgan"
    ) -> ClusterResult:
        """
        Perform Butina (Taylor-Butina) clustering.
        
        This is a leader-based algorithm well-suited for chemical diversity:
        1. Calculate pairwise distances (1 - Tanimoto)
        2. Cluster molecules within distance threshold
        3. Larger clusters form first (most common scaffolds)
        
        Reference: Butina, D. J. Chem. Inf. Comput. Sci. 1999, 39, 747-750
        
        Args:
            smiles_list: List of SMILES strings
            fingerprint_type: "morgan" or "maccs"
            
        Returns:
            ClusterResult with cluster assignments
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for Butina clustering")
            
        # Generate fingerprints
        fps = []
        valid_smiles = []
        valid_indices = []
        
        for i, smiles in enumerate(smiles_list):
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
                
            if fingerprint_type == "morgan":
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            else:
                from rdkit.Chem import MACCSkeys
                fp = MACCSkeys.GenMACCSKeys(mol)
                
            fps.append(fp)
            valid_smiles.append(smiles)
            valid_indices.append(i)
            
        if len(fps) < 2:
            return ClusterResult(
                n_clusters=len(fps),
                cluster_assignments=[0] * len(fps),
                cluster_sizes={0: len(fps)},
                centroids_indices=[0] if fps else [],
                smiles_list=valid_smiles
            )
        
        # Calculate distance matrix (upper triangle)
        n_mols = len(fps)
        dists = []
        
        for i in range(1, n_mols):
            sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
            dists.extend([1 - x for x in sims])
            
        # Butina clustering
        # distThresh = 1 - similarity_threshold
        dist_thresh = 1 - self.similarity_threshold
        clusters = Butina.ClusterData(dists, n_mols, dist_thresh, isDistData=True)
        
        # Convert to assignments
        cluster_assignments = [0] * n_mols
        cluster_sizes = {}
        centroids = []
        
        for cluster_id, members in enumerate(clusters):
            cluster_sizes[cluster_id] = len(members)
            centroids.append(members[0])  # First member is the centroid in Butina
            
            for member in members:
                cluster_assignments[member] = cluster_id
                
        return ClusterResult(
            n_clusters=len(clusters),
            cluster_assignments=cluster_assignments,
            cluster_sizes=cluster_sizes,
            centroids_indices=centroids,
            smiles_list=valid_smiles
        )
    
    def hierarchical_clustering(
        self,
        similarity_matrix: np.ndarray,
        smiles_list: List[str],
        n_clusters: Optional[int] = None,
        distance_threshold: Optional[float] = None
    ) -> ClusterResult:
        """
        Perform hierarchical (agglomerative) clustering.
        
        Args:
            similarity_matrix: Pairwise Tanimoto similarity matrix
            smiles_list: SMILES corresponding to matrix rows
            n_clusters: Number of clusters (if None, uses distance_threshold)
            distance_threshold: Distance for cutting dendrogram
            
        Returns:
            ClusterResult with cluster assignments
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for hierarchical clustering")
            
        # Convert similarity to distance
        distance_matrix = 1 - similarity_matrix
        
        # Perform clustering
        if n_clusters is not None:
            clusterer = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric='precomputed',
                linkage='average'
            )
        else:
            dist_thresh = distance_threshold or (1 - self.similarity_threshold)
            clusterer = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=dist_thresh,
                metric='precomputed',
                linkage='average'
            )
            
        labels = clusterer.fit_predict(distance_matrix)
        
        # Find centroids (molecule closest to cluster center)
        unique_labels = sorted(set(labels))
        cluster_sizes = {}
        centroids = []
        
        for label in unique_labels:
            members = np.where(labels == label)[0]
            cluster_sizes[label] = len(members)
            
            # Find molecule with highest average similarity to cluster
            if len(members) == 1:
                centroids.append(members[0])
            else:
                cluster_sim = similarity_matrix[np.ix_(members, members)]
                avg_sim = np.mean(cluster_sim, axis=1)
                centroid_idx = members[np.argmax(avg_sim)]
                centroids.append(centroid_idx)
                
        return ClusterResult(
            n_clusters=len(unique_labels),
            cluster_assignments=labels.tolist(),
            cluster_sizes=cluster_sizes,
            centroids_indices=centroids,
            smiles_list=smiles_list
        )
    
    def calculate_diversity_metrics(
        self,
        similarity_matrix: np.ndarray,
        cluster_result: ClusterResult
    ) -> DiversityMetrics:
        """
        Calculate diversity metrics for the clustered set.
        
        Args:
            similarity_matrix: Pairwise Tanimoto similarity matrix
            cluster_result: Result from clustering
            
        Returns:
            DiversityMetrics with diversity statistics
        """
        n = similarity_matrix.shape[0]
        
        if n < 2:
            return DiversityMetrics(
                n_molecules=n,
                n_clusters=cluster_result.n_clusters,
                mean_intra_cluster_similarity=1.0,
                mean_inter_cluster_similarity=0.0,
                diversity_index=0.0,
                coverage_score=1.0
            )
        
        labels = np.array(cluster_result.cluster_assignments)
        
        # Intra-cluster similarity (within clusters)
        intra_sims = []
        for cluster_id in range(cluster_result.n_clusters):
            members = np.where(labels == cluster_id)[0]
            if len(members) > 1:
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        intra_sims.append(similarity_matrix[members[i], members[j]])
                        
        mean_intra = np.mean(intra_sims) if intra_sims else 1.0
        
        # Inter-cluster similarity (between clusters)
        inter_sims = []
        for c1 in range(cluster_result.n_clusters):
            for c2 in range(c1 + 1, cluster_result.n_clusters):
                members1 = np.where(labels == c1)[0]
                members2 = np.where(labels == c2)[0]
                
                for m1 in members1:
                    for m2 in members2:
                        inter_sims.append(similarity_matrix[m1, m2])
                        
        mean_inter = np.mean(inter_sims) if inter_sims else 0.0
        
        # Overall diversity (1 - average pairwise similarity)
        upper_tri = similarity_matrix[np.triu_indices(n, k=1)]
        diversity_index = 1 - np.mean(upper_tri)
        
        # Coverage: ratio of clusters with ≥2 members (well-represented scaffolds)
        covered = sum(1 for s in cluster_result.cluster_sizes.values() if s >= 2)
        coverage_score = covered / max(cluster_result.n_clusters, 1)
        
        return DiversityMetrics(
            n_molecules=n,
            n_clusters=cluster_result.n_clusters,
            mean_intra_cluster_similarity=mean_intra,
            mean_inter_cluster_similarity=mean_inter,
            diversity_index=diversity_index,
            coverage_score=coverage_score
        )
    
    def prepare_visualization(
        self,
        fingerprint_matrix: np.ndarray,
        method: str = "tsne",
        n_components: int = 2
    ) -> np.ndarray:
        """
        Prepare 2D/3D coordinates for visualization.
        
        Args:
            fingerprint_matrix: n_molecules x n_bits matrix
            method: "tsne" or "pca"
            n_components: 2 or 3 dimensions
            
        Returns:
            n_molecules x n_components coordinate matrix
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for visualization")
            
        if fingerprint_matrix.shape[0] < 2:
            return fingerprint_matrix[:, :n_components]
            
        if method == "tsne":
            # t-SNE for non-linear dimensionality reduction
            # Good for visualizing clusters
            perplexity = min(30, fingerprint_matrix.shape[0] - 1)
            tsne = TSNE(
                n_components=n_components,
                perplexity=perplexity,
                random_state=42,
                metric='jaccard'  # Appropriate for binary fingerprints
            )
            coords = tsne.fit_transform(fingerprint_matrix)
        else:
            # PCA for linear reduction
            pca = PCA(n_components=n_components)
            coords = pca.fit_transform(fingerprint_matrix)
            
        return coords


if __name__ == "__main__":
    # Example usage
    if not RDKIT_AVAILABLE:
        print("RDKit required")
        exit(1)
        
    # Test molecules - expanded set for clustering
    test_smiles = [
        # Glycols
        "OCCO",       # Ethylene glycol
        "CC(O)CO",    # 1,2-propanediol
        "OCC(O)CO",   # Glycerol
        "OCCCO",      # 1,3-propanediol
        "OCCOCCO",    # Diethylene glycol
        # Amides
        "CN(C)C=O",   # DMF
        "CC(=O)N(C)C", # DMAc
        "CN1CCCC1=O", # NMP
        # Sulfoxides
        "CS(C)=O",    # DMSO
        "CCS(CC)=O",  # Diethyl sulfoxide
    ]
    
    clustering = DiversityClustering(similarity_threshold=0.5)
    
    print("Performing Butina clustering...")
    result = clustering.butina_clustering(test_smiles)
    
    print(f"\nNumber of clusters: {result.n_clusters}")
    print(f"Cluster sizes: {result.cluster_sizes}")
    
    print("\nCluster assignments:")
    for i, (smiles, cluster) in enumerate(zip(result.smiles_list, result.cluster_assignments)):
        is_centroid = i in result.centroids_indices
        centroid_marker = " [CENTROID]" if is_centroid else ""
        print(f"  Cluster {cluster}: {smiles}{centroid_marker}")
```

---

## Sub-Phase II-C.4: Maximum Diversity Selection

### MaxMin Picker Algorithm

The MaxMin algorithm iteratively selects molecules to maximize the minimum distance to already-selected molecules. This ensures maximum spread across chemical space.

**Reference:** Ashton, M. et al. (2002). "Identification of Diverse Database Subsets using Property-Based and Fragment-Based Molecular Descriptions" Quant. Struct.-Act. Relat. [DOI: 10.1002/1521-3838(200208)21:3<241::AID-QSAR241>3.0.CO;2-P]

```python
# src/cheminformatics/diversity_selection.py
"""
Phase II-C.4: Maximum Diversity Selection

This module implements algorithms for selecting maximally diverse
subsets of molecules.

References:
- MaxMin Picker: Ashton et al. QSAR 2002
- RDKit diversity picker: https://www.rdkit.org/docs/source/rdkit.SimDivFilters.rdSimDivPicker.html
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import DataStructs
    from rdkit.SimDivFilters import rdSimDivPicker
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

@dataclass
class DiverseSelection:
    """Result from diversity selection"""
    selected_indices: List[int]
    selected_smiles: List[str]
    selection_order: List[int]  # Order in which molecules were selected
    coverage_by_cluster: Dict[int, int]  # How many from each cluster
    diversity_score: float

class DiversitySelector:
    """
    Selects a maximally diverse subset of molecules.
    
    Methods:
    1. MaxMin: Iteratively pick molecule most distant from current selection
    2. Leader: Fast approximation using sphere exclusion
    3. Cluster-weighted: Ensure representation from all clusters
    """
    
    def __init__(self):
        pass
        
    def maxmin_selection(
        self,
        smiles_list: List[str],
        n_select: int,
        seed_smiles: Optional[str] = None
    ) -> DiverseSelection:
        """
        Select n molecules using MaxMin algorithm.
        
        Algorithm:
        1. Start with seed (or first molecule)
        2. Calculate distance from all molecules to current selection
        3. Pick molecule with maximum minimum distance
        4. Repeat until n molecules selected
        
        Args:
            smiles_list: List of SMILES to select from
            n_select: Number of molecules to select
            seed_smiles: Optional starting molecule
            
        Returns:
            DiverseSelection with selected molecules
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required for MaxMin selection")
            
        # Generate fingerprints
        fps = []
        valid_smiles = []
        valid_indices = []
        
        for i, smiles in enumerate(smiles_list):
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            fps.append(fp)
            valid_smiles.append(smiles)
            valid_indices.append(i)
            
        n_mols = len(fps)
        if n_mols == 0:
            return DiverseSelection([], [], [], {}, 0.0)
            
        n_select = min(n_select, n_mols)
        
        # Use RDKit's MaxMin picker
        picker = rdSimDivPicker.MaxMinPicker()
        
        # Create distance function
        def dist_fn(i, j):
            return 1 - DataStructs.TanimotoSimilarity(fps[i], fps[j])
            
        # If seed specified, find its index
        first_pick = 0
        if seed_smiles:
            try:
                first_pick = valid_smiles.index(seed_smiles)
            except ValueError:
                pass
                
        # Run picker
        picked_indices = list(picker.LazyBitVectorPick(
            fps, 
            n_mols, 
            n_select,
            firstPicks=[first_pick]
        ))
        
        # Calculate diversity score (average minimum distance)
        min_dists = []
        for i, idx in enumerate(picked_indices[1:], 1):
            dists_to_picked = [dist_fn(idx, picked_indices[j]) for j in range(i)]
            min_dists.append(min(dists_to_picked))
        diversity_score = np.mean(min_dists) if min_dists else 0.0
        
        return DiverseSelection(
            selected_indices=picked_indices,
            selected_smiles=[valid_smiles[i] for i in picked_indices],
            selection_order=picked_indices,
            coverage_by_cluster={},  # Will be filled by caller if needed
            diversity_score=diversity_score
        )
    
    def cluster_weighted_selection(
        self,
        smiles_list: List[str],
        cluster_assignments: List[int],
        n_select: int,
        min_per_cluster: int = 1
    ) -> DiverseSelection:
        """
        Select molecules ensuring representation from all clusters.
        
        Strategy:
        1. Ensure at least min_per_cluster from each cluster
        2. Fill remaining slots with MaxMin across all molecules
        
        Args:
            smiles_list: List of SMILES
            cluster_assignments: Cluster ID for each molecule
            n_select: Total number to select
            min_per_cluster: Minimum molecules from each cluster
            
        Returns:
            DiverseSelection with cluster-balanced selection
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit required")
            
        n_mols = len(smiles_list)
        n_select = min(n_select, n_mols)
        
        # Group molecules by cluster
        clusters: Dict[int, List[int]] = {}
        for i, cluster_id in enumerate(cluster_assignments):
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(i)
            
        # Calculate fingerprints
        fps = []
        for smiles in smiles_list:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                fps.append(AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048))
            else:
                fps.append(None)
        
        selected_indices = []
        coverage = {c: 0 for c in clusters}
        
        # Phase 1: Select min_per_cluster from each cluster (most central)
        for cluster_id, members in clusters.items():
            valid_members = [m for m in members if fps[m] is not None]
            
            if not valid_members:
                continue
                
            # Select most central (highest avg similarity within cluster)
            if len(valid_members) == 1:
                selected_indices.append(valid_members[0])
                coverage[cluster_id] = 1
            else:
                # Find centroid
                best_idx = valid_members[0]
                best_sim = -1
                
                for i in valid_members:
                    sims = [DataStructs.TanimotoSimilarity(fps[i], fps[j]) 
                           for j in valid_members if j != i and fps[j] is not None]
                    avg_sim = np.mean(sims) if sims else 0
                    if avg_sim > best_sim:
                        best_sim = avg_sim
                        best_idx = i
                        
                selected_indices.append(best_idx)
                coverage[cluster_id] = 1
                
            if len(selected_indices) >= n_select:
                break
        
        # Phase 2: Fill remaining with MaxMin from unselected
        remaining_slots = n_select - len(selected_indices)
        
        if remaining_slots > 0:
            unselected = [i for i in range(n_mols) 
                         if i not in selected_indices and fps[i] is not None]
            
            if unselected:
                # MaxMin on remaining
                for _ in range(remaining_slots):
                    if not unselected:
                        break
                        
                    # Find molecule most distant from selection
                    best_idx = unselected[0]
                    best_min_dist = -1
                    
                    for idx in unselected:
                        dists = [1 - DataStructs.TanimotoSimilarity(fps[idx], fps[s])
                                for s in selected_indices if fps[s] is not None]
                        min_dist = min(dists) if dists else 0
                        
                        if min_dist > best_min_dist:
                            best_min_dist = min_dist
                            best_idx = idx
                            
                    selected_indices.append(best_idx)
                    unselected.remove(best_idx)
                    coverage[cluster_assignments[best_idx]] = \
                        coverage.get(cluster_assignments[best_idx], 0) + 1
        
        # Calculate diversity
        diversity_score = self._calculate_diversity(fps, selected_indices)
        
        return DiverseSelection(
            selected_indices=selected_indices,
            selected_smiles=[smiles_list[i] for i in selected_indices],
            selection_order=selected_indices,
            coverage_by_cluster=coverage,
            diversity_score=diversity_score
        )
    
    def mechanism_balanced_selection(
        self,
        smiles_list: List[str],
        cluster_assignments: List[int],
        mechanism_assignments: List[str],
        n_select: int,
        mechanism_weights: Optional[Dict[str, float]] = None
    ) -> DiverseSelection:
        """
        Select molecules balanced across separation mechanisms.
        
        This ensures the selection covers different separation approaches
        defined in Phase I (H-bonding, polarity shift, etc.)
        
        Args:
            smiles_list: List of SMILES
            cluster_assignments: Cluster ID for each molecule
            mechanism_assignments: Mechanism type for each molecule
            n_select: Total number to select
            mechanism_weights: Optional weights per mechanism (default: equal)
            
        Returns:
            DiverseSelection balanced by mechanism
        """
        # Group by mechanism
        mechanisms: Dict[str, List[int]] = {}
        for i, mech in enumerate(mechanism_assignments):
            if mech not in mechanisms:
                mechanisms[mech] = []
            mechanisms[mech].append(i)
            
        # Default: equal weight
        if mechanism_weights is None:
            mechanism_weights = {m: 1.0 for m in mechanisms}
            
        # Normalize weights
        total_weight = sum(mechanism_weights.get(m, 1.0) for m in mechanisms)
        
        # Allocate selections per mechanism
        allocations = {}
        remaining = n_select
        
        for mech in mechanisms:
            weight = mechanism_weights.get(mech, 1.0) / total_weight
            allocation = max(1, int(n_select * weight))  # At least 1
            allocations[mech] = min(allocation, len(mechanisms[mech]), remaining)
            remaining -= allocations[mech]
            
        # Select from each mechanism using cluster-weighted selection
        selected_indices = []
        coverage = {}
        
        for mech, indices in mechanisms.items():
            n_from_mech = allocations.get(mech, 0)
            if n_from_mech == 0:
                continue
                
            mech_smiles = [smiles_list[i] for i in indices]
            mech_clusters = [cluster_assignments[i] for i in indices]
            
            # Use cluster-weighted within mechanism
            mech_selection = self.cluster_weighted_selection(
                mech_smiles,
                mech_clusters,
                n_from_mech,
                min_per_cluster=1
            )
            
            # Map back to original indices
            for local_idx in mech_selection.selected_indices:
                global_idx = indices[local_idx]
                selected_indices.append(global_idx)
                cluster_id = cluster_assignments[global_idx]
                coverage[cluster_id] = coverage.get(cluster_id, 0) + 1
        
        # Calculate fingerprints for diversity
        fps = []
        for smiles in smiles_list:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                fps.append(AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048))
            else:
                fps.append(None)
                
        diversity_score = self._calculate_diversity(fps, selected_indices)
        
        return DiverseSelection(
            selected_indices=selected_indices,
            selected_smiles=[smiles_list[i] for i in selected_indices],
            selection_order=selected_indices,
            coverage_by_cluster=coverage,
            diversity_score=diversity_score
        )
    
    def _calculate_diversity(
        self, 
        fps: List,
        selected_indices: List[int]
    ) -> float:
        """Calculate diversity score as 1 - mean pairwise similarity"""
        if len(selected_indices) < 2:
            return 0.0
            
        sims = []
        for i in range(len(selected_indices)):
            for j in range(i + 1, len(selected_indices)):
                idx_i = selected_indices[i]
                idx_j = selected_indices[j]
                
                if fps[idx_i] is not None and fps[idx_j] is not None:
                    sim = DataStructs.TanimotoSimilarity(fps[idx_i], fps[idx_j])
                    sims.append(sim)
                    
        return 1 - np.mean(sims) if sims else 0.0


if __name__ == "__main__":
    # Example usage
    if not RDKIT_AVAILABLE:
        print("RDKit required")
        exit(1)
        
    # Test molecules with assigned clusters/mechanisms
    test_data = [
        ("OCCO", 0, "HB"),        # Ethylene glycol
        ("CC(O)CO", 0, "HB"),     # Propylene glycol
        ("OCC(O)CO", 0, "HB"),    # Glycerol
        ("OCCCO", 0, "HB"),       # 1,3-propanediol
        ("OCCOCCO", 0, "HB"),     # Diethylene glycol
        ("CN(C)C=O", 1, "HB"),    # DMF
        ("CC(=O)N(C)C", 1, "HB"), # DMAc
        ("CN1CCCC1=O", 1, "HB"),  # NMP
        ("CS(C)=O", 2, "PS"),     # DMSO
        ("CCS(CC)=O", 2, "PS"),   # Diethyl sulfoxide
    ]
    
    smiles_list = [d[0] for d in test_data]
    clusters = [d[1] for d in test_data]
    mechanisms = [d[2] for d in test_data]
    
    selector = DiversitySelector()
    
    print("MaxMin selection (5 molecules):")
    result = selector.maxmin_selection(smiles_list, n_select=5)
    print(f"Selected: {result.selected_smiles}")
    print(f"Diversity score: {result.diversity_score:.3f}")
    
    print("\nCluster-weighted selection (5 molecules):")
    result = selector.cluster_weighted_selection(smiles_list, clusters, n_select=5)
    print(f"Selected: {result.selected_smiles}")
    print(f"Coverage: {result.coverage_by_cluster}")
    print(f"Diversity score: {result.diversity_score:.3f}")
```

---

## Sub-Phase II-C.5: Engine C Orchestrator

### Complete Pipeline Integration

```python
# src/cheminformatics/engine_c_orchestrator.py
"""
Phase II-C.5: Engine C Orchestrator

This integrates all cheminformatics components into a complete
Engine C pipeline for diversity-based molecule selection.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
import numpy as np

# Import Engine C components
from src.cheminformatics.molecule_retrieval import (
    MoleculeRetriever, 
    MoleculeCandidate, 
    PropertyFilter,
    load_phase1_clusters
)
from src.cheminformatics.descriptor_calculator import (
    DescriptorCalculator,
    MolecularDescriptors,
    calculate_similarity_matrix
)
from src.cheminformatics.diversity_clustering import (
    DiversityClustering,
    ClusterResult,
    DiversityMetrics
)
from src.cheminformatics.diversity_selection import (
    DiversitySelector,
    DiverseSelection
)

@dataclass
class EngineCResult:
    """Final output from Engine C"""
    selected_molecules: List[Dict]
    total_candidates_screened: int
    n_valid_molecules: int
    n_clusters_found: int
    diversity_metrics: Dict
    engine_a_overlaps: List[str]
    engine_b_overlaps: List[str]
    selection_method: str
    timestamp: str

class EngineCOrchestrator:
    """
    Orchestrates the complete Engine C pipeline.
    
    Pipeline:
    1. Load Phase I clusters
    2. Retrieve molecules from databases
    3. Calculate molecular descriptors
    4. Perform diversity clustering
    5. Select diverse subset
    6. Check overlaps with Engines A/B
    7. Export results
    """
    
    def __init__(
        self,
        phase1_clusters_path: Optional[Path] = None,
        engine_a_results_path: Optional[Path] = None,
        engine_b_results_path: Optional[Path] = None,
        property_filter: Optional[PropertyFilter] = None
    ):
        """
        Args:
            phase1_clusters_path: Path to Phase I cluster definitions JSON
            engine_a_results_path: Path to Engine A results for overlap detection
            engine_b_results_path: Path to Engine B results for overlap detection
            property_filter: Filter criteria for initial screening
        """
        self.phase1_clusters_path = phase1_clusters_path
        self.property_filter = property_filter or PropertyFilter()
        
        # Load Engine A/B results for overlap detection
        self.engine_a_molecules: Set[str] = set()
        self.engine_b_molecules: Set[str] = set()
        
        if engine_a_results_path and engine_a_results_path.exists():
            with open(engine_a_results_path) as f:
                data = json.load(f)
                for mol in data.get('molecules', []):
                    self.engine_a_molecules.add(mol.get('smiles', ''))
                    
        if engine_b_results_path and engine_b_results_path.exists():
            with open(engine_b_results_path) as f:
                data = json.load(f)
                for mol in data.get('selected_molecules', []):
                    self.engine_b_molecules.add(mol.get('smiles', ''))
        
        # Initialize components
        self.retriever = MoleculeRetriever()
        self.descriptor_calc = DescriptorCalculator()
        self.clustering = DiversityClustering(similarity_threshold=0.6)
        self.selector = DiversitySelector()
        
    def run_pipeline(
        self,
        target_molecules: int = 50,
        max_candidates: int = 1000,
        selection_method: str = "mechanism_balanced",
        include_benchmark: bool = True
    ) -> EngineCResult:
        """
        Run the complete Engine C pipeline.
        
        Args:
            target_molecules: Number of molecules to select (25-50)
            max_candidates: Maximum candidates to retrieve
            selection_method: "maxmin", "cluster_weighted", or "mechanism_balanced"
            include_benchmark: Include benchmark compounds in candidates
            
        Returns:
            EngineCResult with selected diverse molecules
        """
        print("=" * 60)
        print("ENGINE C: CHEMINFORMATICS & DIVERSITY CLUSTERING")
        print("=" * 60)
        
        # Step 1: Load Phase I clusters
        print("\n[Step 1] Loading Phase I cluster definitions...")
        clusters = self._load_clusters()
        print(f"  Loaded {len(clusters)} cluster definitions")
        
        # Step 2: Retrieve molecules
        print("\n[Step 2] Retrieving molecules from databases...")
        candidates = self._retrieve_molecules(clusters, max_candidates)
        
        if include_benchmark:
            candidates = self._add_benchmark_compounds(candidates)
            
        print(f"  Total candidates: {len(candidates)}")
        
        # Step 3: Calculate descriptors
        print("\n[Step 3] Calculating molecular descriptors...")
        descriptors = self._calculate_descriptors(candidates)
        valid_descriptors = [d for d in descriptors if d.valid]
        print(f"  Valid molecules: {len(valid_descriptors)}/{len(descriptors)}")
        
        # Step 4: Perform clustering
        print("\n[Step 4] Performing diversity clustering...")
        smiles_list = [d.smiles for d in valid_descriptors]
        cluster_ids = [self._get_cluster_for_smiles(d.smiles, candidates) 
                       for d in valid_descriptors]
        mechanisms = [self._get_mechanism_for_smiles(d.smiles, candidates) 
                      for d in valid_descriptors]
        
        cluster_result = self.clustering.butina_clustering(smiles_list)
        print(f"  Found {cluster_result.n_clusters} structural clusters")
        
        # Calculate similarity matrix for metrics
        fp_matrix, _ = self.descriptor_calc.get_fingerprint_matrix(
            valid_descriptors, "morgan"
        )
        sim_matrix = calculate_similarity_matrix(fp_matrix)
        
        diversity_metrics = self.clustering.calculate_diversity_metrics(
            sim_matrix, cluster_result
        )
        print(f"  Diversity index: {diversity_metrics.diversity_index:.3f}")
        
        # Step 5: Select diverse subset
        print(f"\n[Step 5] Selecting {target_molecules} diverse molecules...")
        print(f"  Method: {selection_method}")
        
        selection = self._perform_selection(
            smiles_list,
            cluster_result.cluster_assignments,
            cluster_ids,
            mechanisms,
            target_molecules,
            selection_method
        )
        
        print(f"  Selected {len(selection.selected_smiles)} molecules")
        print(f"  Selection diversity score: {selection.diversity_score:.3f}")
        
        # Step 6: Check overlaps
        print("\n[Step 6] Checking overlaps with Engines A and B...")
        engine_a_overlaps = []
        engine_b_overlaps = []
        
        for smiles in selection.selected_smiles:
            if smiles in self.engine_a_molecules:
                engine_a_overlaps.append(smiles)
            if smiles in self.engine_b_molecules:
                engine_b_overlaps.append(smiles)
                
        print(f"  Engine A overlaps: {len(engine_a_overlaps)}")
        print(f"  Engine B overlaps: {len(engine_b_overlaps)}")
        
        # Step 7: Compile results
        print("\n[Step 7] Compiling results...")
        selected_molecules = self._compile_molecule_data(
            selection, valid_descriptors, candidates
        )
        
        result = EngineCResult(
            selected_molecules=selected_molecules,
            total_candidates_screened=len(candidates),
            n_valid_molecules=len(valid_descriptors),
            n_clusters_found=cluster_result.n_clusters,
            diversity_metrics={
                "diversity_index": diversity_metrics.diversity_index,
                "n_structural_clusters": diversity_metrics.n_clusters,
                "mean_intra_cluster_similarity": diversity_metrics.mean_intra_cluster_similarity,
                "mean_inter_cluster_similarity": diversity_metrics.mean_inter_cluster_similarity,
                "selection_diversity_score": selection.diversity_score,
                "cluster_coverage": selection.coverage_by_cluster
            },
            engine_a_overlaps=engine_a_overlaps,
            engine_b_overlaps=engine_b_overlaps,
            selection_method=selection_method,
            timestamp=datetime.now().isoformat()
        )
        
        print("\n" + "=" * 60)
        print("ENGINE C COMPLETE")
        print(f"Selected: {len(result.selected_molecules)} diverse molecules")
        print(f"Engine A overlaps: {len(engine_a_overlaps)} (prioritize these!)")
        print(f"Engine B overlaps: {len(engine_b_overlaps)} (prioritize these!)")
        print("=" * 60)
        
        return result
    
    def _load_clusters(self) -> List[Dict]:
        """Load Phase I cluster definitions."""
        if self.phase1_clusters_path and self.phase1_clusters_path.exists():
            return load_phase1_clusters(self.phase1_clusters_path)
        else:
            # Use default example clusters if no file provided
            print("  WARNING: Using example clusters (no Phase I file provided)")
            return self._get_example_clusters()
    
    def _get_example_clusters(self) -> List[Dict]:
        """Example clusters for testing (from Phase I design)."""
        return [
            {
                "cluster_id": "HB_GLYCOL_S",
                "smarts_pattern": "[OX2H][CX4][CX4][OX2H]",
                "mw_range": [50, 150],
                "mechanism": "HYDROGEN_BONDING"
            },
            {
                "cluster_id": "HB_GLYCOL_M",
                "smarts_pattern": "[OX2H][CX4][CX4][OX2H]",
                "mw_range": [150, 300],
                "mechanism": "HYDROGEN_BONDING"
            },
            {
                "cluster_id": "HB_AMIDE_S",
                "smarts_pattern": "[NX3]([#6])([#6])[CX3](=[OX1])[#6]",
                "mw_range": [50, 150],
                "mechanism": "HYDROGEN_BONDING"
            },
            {
                "cluster_id": "HB_LACTAM_S",
                "smarts_pattern": "[NR1][CR1](=O)",
                "mw_range": [80, 150],
                "mechanism": "HYDROGEN_BONDING"
            },
            {
                "cluster_id": "PS_SULFOXIDE_S",
                "smarts_pattern": "[SX3](=[OX1])([#6])[#6]",
                "mw_range": [50, 150],
                "mechanism": "POLARITY_SHIFT"
            },
        ]
    
    def _retrieve_molecules(
        self, 
        clusters: List[Dict], 
        max_total: int
    ) -> List[MoleculeCandidate]:
        """Retrieve molecules from all clusters."""
        return self.retriever.retrieve_from_all_clusters(
            clusters,
            self.property_filter,
            max_per_cluster=max_total // max(len(clusters), 1),
            max_total=max_total
        )
    
    def _add_benchmark_compounds(
        self, 
        candidates: List[MoleculeCandidate]
    ) -> List[MoleculeCandidate]:
        """Add benchmark compounds from Phase I."""
        # Benchmark compounds defined in Phase I
        benchmarks = [
            MoleculeCandidate(
                smiles="OCCO",
                name="Ethylene glycol",
                cid=174,
                cluster_id="BENCHMARK",
                molecular_weight=62.07,
                source="benchmark"
            ),
            MoleculeCandidate(
                smiles="CN1CCCC1=O",
                name="N-Methyl-2-pyrrolidone",
                cid=13387,
                cluster_id="BENCHMARK",
                molecular_weight=99.13,
                source="benchmark"
            ),
            MoleculeCandidate(
                smiles="CS(C)=O",
                name="Dimethyl sulfoxide",
                cid=679,
                cluster_id="BENCHMARK",
                molecular_weight=78.13,
                source="benchmark"
            ),
        ]
        
        # Avoid duplicates
        existing_smiles = {c.smiles for c in candidates}
        for benchmark in benchmarks:
            if benchmark.smiles not in existing_smiles:
                candidates.append(benchmark)
                existing_smiles.add(benchmark.smiles)
                
        return candidates
    
    def _calculate_descriptors(
        self, 
        candidates: List[MoleculeCandidate]
    ) -> List[MolecularDescriptors]:
        """Calculate descriptors for all candidates."""
        smiles_list = [c.smiles for c in candidates]
        return self.descriptor_calc.calculate_batch(smiles_list)
    
    def _get_cluster_for_smiles(
        self, 
        smiles: str, 
        candidates: List[MoleculeCandidate]
    ) -> int:
        """Get the Phase I cluster ID for a molecule."""
        for i, c in enumerate(candidates):
            if c.smiles == smiles:
                # Convert cluster_id to int for compatibility
                cluster_str = c.cluster_id
                # Simple hash for string cluster IDs
                return hash(cluster_str) % 100
        return 0
    
    def _get_mechanism_for_smiles(
        self, 
        smiles: str, 
        candidates: List[MoleculeCandidate]
    ) -> str:
        """Get the separation mechanism for a molecule."""
        for c in candidates:
            if c.smiles == smiles:
                # Infer mechanism from cluster_id pattern
                if "HB_" in c.cluster_id:
                    return "HYDROGEN_BONDING"
                elif "PS_" in c.cluster_id:
                    return "POLARITY_SHIFT"
                elif "SO_" in c.cluster_id:
                    return "SALTING_OUT"
                else:
                    return "UNKNOWN"
        return "UNKNOWN"
    
    def _perform_selection(
        self,
        smiles_list: List[str],
        structural_clusters: List[int],
        phase1_clusters: List[int],
        mechanisms: List[str],
        target_molecules: int,
        method: str
    ) -> DiverseSelection:
        """Perform diversity selection with specified method."""
        
        if method == "maxmin":
            return self.selector.maxmin_selection(smiles_list, target_molecules)
            
        elif method == "cluster_weighted":
            return self.selector.cluster_weighted_selection(
                smiles_list, 
                structural_clusters, 
                target_molecules
            )
            
        elif method == "mechanism_balanced":
            return self.selector.mechanism_balanced_selection(
                smiles_list,
                phase1_clusters,
                mechanisms,
                target_molecules
            )
            
        else:
            print(f"  WARNING: Unknown method '{method}', using maxmin")
            return self.selector.maxmin_selection(smiles_list, target_molecules)
    
    def _compile_molecule_data(
        self,
        selection: DiverseSelection,
        descriptors: List[MolecularDescriptors],
        candidates: List[MoleculeCandidate]
    ) -> List[Dict]:
        """Compile selected molecules with all relevant data."""
        compiled = []
        
        # Create lookup by SMILES
        desc_lookup = {d.smiles: d for d in descriptors if d.valid}
        cand_lookup = {c.smiles: c for c in candidates}
        
        for idx, smiles in zip(selection.selected_indices, selection.selected_smiles):
            desc = desc_lookup.get(smiles)
            cand = cand_lookup.get(smiles)
            
            molecule_data = {
                "smiles": smiles,
                "name": cand.name if cand else "",
                "cid": cand.cid if cand else None,
                "cluster_id": cand.cluster_id if cand else "",
                "selection_order": selection.selection_order.index(idx) if idx in selection.selection_order else -1,
                "properties": desc.physicochemical if desc else {},
                "engine_a_overlap": smiles in self.engine_a_molecules,
                "engine_b_overlap": smiles in self.engine_b_molecules,
                "source": "engine_c"
            }
            compiled.append(molecule_data)
            
        return compiled
    
    def export_results(
        self, 
        result: EngineCResult, 
        output_path: Path
    ) -> Path:
        """Export Engine C results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "engine": "C",
            "methodology": "Cheminformatics & Diversity Clustering",
            "selected_molecules": result.selected_molecules,
            "statistics": {
                "total_candidates_screened": result.total_candidates_screened,
                "valid_molecules": result.n_valid_molecules,
                "structural_clusters_found": result.n_clusters_found,
                "molecules_selected": len(result.selected_molecules)
            },
            "diversity_metrics": result.diversity_metrics,
            "overlaps": {
                "engine_a": result.engine_a_overlaps,
                "engine_b": result.engine_b_overlaps,
                "total_overlaps": len(result.engine_a_overlaps) + len(result.engine_b_overlaps)
            },
            "selection_method": result.selection_method,
            "timestamp": result.timestamp
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        print(f"Results saved to: {output_path}")
        return output_path


def run_engine_c_pipeline(
    phase1_clusters_path: Optional[Path] = None,
    engine_a_results_path: Optional[Path] = None,
    engine_b_results_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> EngineCResult:
    """
    Main entry point for Engine C.
    
    Args:
        phase1_clusters_path: Path to Phase I cluster definitions
        engine_a_results_path: Path to Engine A results
        engine_b_results_path: Path to Engine B results
        output_path: Where to save results
        
    Returns:
        EngineCResult with selected molecules
    """
    orchestrator = EngineCOrchestrator(
        phase1_clusters_path=phase1_clusters_path,
        engine_a_results_path=engine_a_results_path,
        engine_b_results_path=engine_b_results_path
    )
    
    result = orchestrator.run_pipeline(
        target_molecules=50,
        max_candidates=500,  # Limit for reasonable API usage
        selection_method="mechanism_balanced"
    )
    
    if output_path is None:
        output_path = Path("data/engine_c_results.json")
        
    orchestrator.export_results(result, output_path)
    
    return result


if __name__ == "__main__":
    result = run_engine_c_pipeline()
```

---

## Code Artifacts Summary

### Project Structure Addition

```
src/
├── cheminformatics/
│   ├── __init__.py
│   ├── molecule_retrieval.py      # PubChem queries, Phase I integration
│   ├── descriptor_calculator.py   # RDKit fingerprints/descriptors
│   ├── diversity_clustering.py    # Butina, hierarchical clustering
│   ├── diversity_selection.py     # MaxMin, cluster-weighted selection
│   └── engine_c_orchestrator.py   # Complete pipeline
```

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `18_molecule_retrieval.ipynb` | Test PubChem queries with Phase I clusters |
| `19_descriptor_calculation.ipynb` | Explore RDKit descriptors on candidates |
| `20_diversity_clustering.ipynb` | Visualize chemical space with t-SNE |
| `21_diversity_selection.ipynb` | Compare selection algorithms |
| `22_engine_c_integration.ipynb` | Full Engine C pipeline |

### Requirements Update

```
# requirements.txt additions for Engine C
rdkit>=2023.3.1        # Cheminformatics toolkit
scikit-learn>=1.3.0    # Clustering, dimensionality reduction
numpy>=1.24.0          # Numerical operations
requests>=2.31.0       # API calls
```

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | Reference |
|------|-----------------|-----------|
| RDKit installation | `pip install rdkit` | https://www.rdkit.org/docs/Install.html |
| PubChem rate limits | Check current policy | https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest#section=Request-Rate-Limitations |
| Butina clustering parameters | Validate threshold for your dataset | Adjust `similarity_threshold` based on results |
| SMARTS patterns from Phase I | Verify against known compounds | Test with RDKit before database queries |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| Morgan fingerprints (ECFP) | RDKit documentation | High confidence |
| Tanimoto similarity | Standard cheminformatics metric | High confidence |
| Butina clustering algorithm | Butina, D. J. Chem. Inf. Comput. Sci. 1999 | High confidence |
| MaxMin diversity selection | Standard cheminformatics algorithm | High confidence |
| PubChem PUG REST API | Official documentation | High confidence |

### Accuracy Limitations

1. **PubChem Query Limitations**: Complex SMARTS patterns may return many results or timeout. The code includes rate limiting but may need adjustment for production use.

2. **Descriptor Selection**: The physicochemical descriptors chosen are based on general separation science principles. Domain-specific descriptors for entrainer selection may need refinement based on literature review.

3. **Clustering Threshold**: The default Tanimoto threshold of 0.6-0.7 is a starting point. Optimal values depend on your specific chemical space and diversity requirements.

---

## GitHub Portfolio Framing

### README Section for Phase II-C

```markdown
## Phase II-C: Multi-Vector Initial Selection 🧪

### Engine C: Cheminformatics & Diversity Clustering

**Status:** Complete

This module provides a purely algorithmic, reproducible approach to molecule 
selection using established cheminformatics methods.

#### Methodology
| Step | Tool | Purpose |
|------|------|---------|
| Retrieval | PubChem API | Fetch molecules matching Phase I clusters |
| Fingerprints | RDKit Morgan (ECFP4) | Structural representation |
| Clustering | Butina Algorithm | Identify structural groups |
| Selection | MaxMin/Cluster-weighted | Ensure diversity |

#### Key Features
- **Reproducible**: Same inputs → same outputs (no LLM variance)
- **Diversity Guaranteed**: Mathematical maximization of structural spread
- **Mechanism Coverage**: Balances selection across separation mechanisms

#### Outputs
- 25-50 structurally diverse molecules
- Diversity metrics (Tanimoto-based)
- Chemical space visualization coordinates (t-SNE)
- Overlap flags with Engines A/B

### Reproducibility
```bash
# Install dependencies
pip install rdkit scikit-learn

# Run Engine C
python -m src.cheminformatics.engine_c_orchestrator
```

### Diversity Metrics
| Metric | Value |
|--------|-------|
| Diversity Index | 0.XX |
| Structural Clusters | XX |
| Selection Coverage | XX% |
```

### Suggested Badges

```markdown
![RDKit](https://img.shields.io/badge/Library-RDKit-blue)
![Method](https://img.shields.io/badge/Method-Diversity%20Clustering-green)
![Reproducible](https://img.shields.io/badge/Reproducible-Yes-brightgreen)
```

---

## Confidence Assessment

### High Confidence
- RDKit fingerprint calculation (Morgan, MACCS)
- Tanimoto similarity calculation
- Butina clustering algorithm
- MaxMin selection algorithm
- PubChem API basic queries
- Physicochemical descriptor calculation
- Python implementation patterns

### Needs Verification
- Optimal Tanimoto threshold for entrainer selection (start with 0.6-0.7, adjust)
- PubChem current rate limits (verify at time of use)
- Complex SMARTS pattern performance in PubChem queries
- scikit-learn API compatibility with current version

### Outside My Expertise
- Optimal descriptor selection for entrainer-specific properties
- Validation against experimental separation data
- Industry-standard property ranges for entrainer filtering

---

## Integration with Engines A and B

### Overlap Detection Strategy

Engine C checks for overlaps with Engines A and B. Molecules appearing in multiple engines should be **prioritized** as they are supported by:
- Literature evidence (Engine A)
- Innovation/TRIZ analysis (Engine B)  
- Structural diversity requirements (Engine C)

```python
# Priority scoring based on engine agreement
def calculate_priority_score(molecule: Dict) -> float:
    """
    Score molecules by engine agreement.
    
    Molecules appearing in all 3 engines = highest priority
    """
    score = 1.0  # Base score (Engine C)
    
    if molecule.get("engine_a_overlap"):
        score += 1.5  # Literature-grounded
        
    if molecule.get("engine_b_overlap"):
        score += 1.0  # Innovation-supported
        
    return score
```