# Phase I: Domain Mapping & Cluster Definition

> Systematic mapping of the chemical space to identify promising molecular "hot spots" for entrainer selection

## 🎯 Objective

Reduce the vast chemical space (100,000+ molecules) to a manageable set of ~500 representative cluster centroids while preserving chemical diversity relevant to extractive distillation.

---

## 📊 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE I PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│   │  Literature │    │  Database   │    │  Property   │                 │
│   │   Survey    │───▶│   Scoping   │───▶│  Filtering  │                 │
│   │             │    │  (PubChem)  │    │             │                 │
│   └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                │                         │
│                                                ▼                         │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│   │   Cluster   │◀───│ Fingerprint │◀───│  Structural │                 │
│   │  Definition │    │ Generation  │    │  Filtering  │                 │
│   │  (K-means)  │    │  (Morgan)   │    │  (SMARTS)   │                 │
│   └─────────────┘    └─────────────┘    └─────────────┘                 │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              Output: 500 Cluster Centroids + Metadata            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Key Steps

### 1. Literature Survey

**Purpose**: Identify known entrainers and establish baseline understanding.

**Sources**:
- Perry's Chemical Engineers' Handbook (Chapter 13)
- Laroche et al. (1991) - Homogeneous Azeotropic Distillation
- NIST TDE Database
- Recent review articles (2020-2025)

**Output**: Seed list of ~50 known entrainers with documented performance.

### 2. Database Scoping

**Purpose**: Query PubChem for molecules matching entrainer criteria.

**Query Parameters**:
```python
QUERY_CRITERIA = {
    "molecular_weight": (50, 300),      # g/mol
    "boiling_point": (350, 500),        # K
    "hydrogen_bond_donor_count": (0, 3),
    "hydrogen_bond_acceptor_count": (1, 6),
    "rotatable_bond_count": (0, 10),
}
```

**Expected Volume**: 100,000 - 150,000 molecules

### 3. Property Filtering

**Purpose**: Apply thermodynamic constraints for extractive distillation.

**Filters**:
| Property | Constraint | Rationale |
|----------|------------|-----------|
| Boiling Point | > Ethanol (351 K) | Must be separable |
| Vapor Pressure | < 10 kPa @ 298 K | Minimize losses |
| Miscibility | Miscible with ethanol | Process requirement |
| Thermal Stability | Stable to 450 K | Operating conditions |

### 4. Structural Filtering (SMARTS)

**Purpose**: Exclude molecules with problematic functional groups.

**Exclusion Patterns**:
```python
EXCLUSION_SMARTS = [
    "[N+](=O)[O-]",      # Nitro groups (explosive)
    "[Cl,Br,I]",         # Halogens (environmental)
    "[#6]=[#6]=[#6]",    # Allenes (reactive)
    "C#N",               # Nitriles (toxic)
    "[As,Se,Te]",        # Heavy metalloids
]
```

### 5. Fingerprint Generation

**Purpose**: Create numerical representations for clustering.

**Method**: Morgan Fingerprints (ECFP4)
- Radius: 2
- Bits: 2048
- Features: Connectivity-based

### 6. Clustering

**Purpose**: Group similar molecules and select representatives.

**Algorithm**: K-means with silhouette optimization
- Target clusters: 500
- Distance metric: Tanimoto
- Centroid selection: Molecule closest to cluster center

---

## 📁 Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `phase1_clusters.parquet` | Parquet | Cluster assignments and centroids |
| `phase1_metadata.json` | JSON | Clustering parameters and statistics |
| `phase1_excluded.csv` | CSV | Molecules excluded with reasons |

---

## 🔧 Configuration

```yaml
# science_config.yaml
phase1:
  pubchem:
    max_results: 150000
    batch_size: 1000
  filtering:
    min_boiling_point_k: 351
    max_molecular_weight: 300
  clustering:
    n_clusters: 500
    random_state: 42
    max_iter: 300
```

---

## 📈 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Coverage | ≥95% of known entrainers in clusters | Cross-reference with literature |
| Diversity | Silhouette score ≥ 0.3 | Clustering quality |
| Reduction | 100K → 500 (200x) | Computational feasibility |

---

## 🚀 Usage

```bash
# Run Phase I
python -m src.phase1.main

# With custom config
python -m src.phase1.main --config config/custom_phase1.yaml

# Resume from checkpoint
python -m src.phase1.main --resume data/checkpoints/phase1_step3.pkl
```

---

## 📚 References

1. Laroche, L., et al. (1991). "Homogeneous Azeotropic Distillation"
2. Perry's Chemical Engineers' Handbook, 9th Ed., Chapter 13
3. Rogers, D., & Hahn, M. (2010). "Extended-Connectivity Fingerprints"

