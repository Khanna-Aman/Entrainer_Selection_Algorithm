# Phase IV: Multi-Objective Bayesian Optimization

> Active learning loop using Gaussian Process surrogates and qEHVI acquisition for Pareto frontier identification

## 🎯 Objective

Simultaneously optimize safety and efficiency objectives using Multi-Objective Bayesian Optimization (MOBO) to identify the Pareto frontier and locate "knee points" representing optimal trade-offs.

---

## 📊 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE IV PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input: 150-300 Candidates from Phase III                              │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                 Initial Sampling (n=20)                          │   │
│   │            Latin Hypercube + Known Entrainers                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              ACTIVE LEARNING LOOP (50 iterations)                │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │   │
│   │  │  Gaussian   │───▶│    qEHVI    │───▶│   Evaluate  │          │   │
│   │  │  Process    │    │ Acquisition │    │   Candidate │          │   │
│   │  │  Surrogate  │    │  Function   │    │             │          │   │
│   │  └─────────────┘    └─────────────┘    └──────┬──────┘          │   │
│   │         ▲                                      │                 │   │
│   │         └──────────────────────────────────────┘                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│                           ▼                                              │
│   Output: Pareto Frontier with Knee Points Identified                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Objective Functions

### Efficiency Objective (Maximize)

```python
def efficiency_score(molecule: Molecule) -> float:
    """Composite efficiency score for extractive distillation."""
    # Selectivity at infinite dilution
    selectivity = calculate_selectivity_inf(molecule, "ethanol", "water")
    
    # Capacity (solvent power)
    capacity = calculate_capacity(molecule, "ethanol")
    
    # Combined score (higher is better)
    return 0.6 * normalize(selectivity) + 0.4 * normalize(capacity)
```

### Safety Objective (Maximize)

```python
def safety_score(molecule: Molecule) -> float:
    """Composite safety score (higher = safer)."""
    scores = {
        "flash_point": normalize_flash_point(molecule.flash_point_k),
        "ld50": normalize_ld50(molecule.ld50_oral),
        "ghs_hazard": normalize_ghs(molecule.ghs_codes),
        "environmental": normalize_env_impact(molecule),
    }
    weights = {"flash_point": 0.25, "ld50": 0.30, "ghs_hazard": 0.25, "environmental": 0.20}
    return sum(w * scores[k] for k, w in weights.items())
```

---

## 🧮 Gaussian Process Surrogate

### Model Architecture

```python
from botorch.models import SingleTaskGP
from gpytorch.kernels import MaternKernel, ScaleKernel

class EntrainerGP(SingleTaskGP):
    def __init__(self, train_X, train_Y):
        super().__init__(train_X, train_Y)
        self.covar_module = ScaleKernel(
            MaternKernel(nu=2.5, ard_num_dims=train_X.shape[-1])
        )
```

### Input Features

| Feature | Description | Normalization |
|---------|-------------|---------------|
| Morgan FP (PCA) | 50 principal components | StandardScaler |
| Molecular weight | g/mol | MinMax [0, 1] |
| LogP | Partition coefficient | MinMax [0, 1] |
| H-bond donors | Count | MinMax [0, 1] |
| H-bond acceptors | Count | MinMax [0, 1] |
| TPSA | Topological polar surface area | MinMax [0, 1] |

---

## 📈 qEHVI Acquisition Function

### Expected Hypervolume Improvement

```python
from botorch.acquisition.multi_objective import qExpectedHypervolumeImprovement

def get_acquisition(model, ref_point, pareto_Y):
    """Configure qEHVI acquisition function."""
    return qExpectedHypervolumeImprovement(
        model=model,
        ref_point=ref_point,
        partitioning=FastNondominatedPartitioning(
            ref_point=ref_point,
            Y=pareto_Y
        ),
        sampler=SobolQMCNormalSampler(sample_shape=torch.Size([128]))
    )
```

### Reference Point Selection

```python
# Reference point: worst acceptable values
REF_POINT = torch.tensor([
    0.0,  # Minimum efficiency (normalized)
    0.0,  # Minimum safety (normalized)
])
```

---

## 🎯 Hypothesis Validation

### H1: Pareto Frontier Structure

**Hypothesis**: Pareto frontier exhibits convex structure with identifiable knee points.

**Validation**:
```python
def identify_knee_points(pareto_front: np.ndarray) -> list[int]:
    """Find knee points using maximum curvature."""
    from kneed import KneeLocator
    
    # Sort by first objective
    sorted_idx = np.argsort(pareto_front[:, 0])
    sorted_front = pareto_front[sorted_idx]
    
    kneedle = KneeLocator(
        sorted_front[:, 0],
        sorted_front[:, 1],
        curve="convex",
        direction="decreasing"
    )
    return [sorted_idx[i] for i in kneedle.all_knees]
```

### H2: Computational Efficiency

**Hypothesis**: qEHVI achieves equivalent hypervolume with ≤30% computational budget.

**Validation**:
```python
def validate_efficiency(full_hv: float, partial_hv: float, budget_ratio: float) -> bool:
    """Check if partial budget achieves target hypervolume."""
    return partial_hv >= 0.95 * full_hv and budget_ratio <= 0.30
```

---

## 📊 Hypervolume Tracking

```python
def calculate_hypervolume(pareto_Y: torch.Tensor, ref_point: torch.Tensor) -> float:
    """Calculate hypervolume indicator."""
    from botorch.utils.multi_objective import Hypervolume
    hv = Hypervolume(ref_point=ref_point)
    return hv.compute(pareto_Y)
```

### Convergence Criteria

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| HV improvement | < 0.1% for 5 iterations | Early stop |
| Max iterations | 50 | Stop |
| Pareto size | ≥ 20 points | Continue |

---

## 📁 Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `phase4_pareto.json` | JSON | Pareto-optimal candidates |
| `phase4_gp_model.pt` | PyTorch | Trained GP model |
| `phase4_hv_history.csv` | CSV | Hypervolume progression |
| `phase4_knee_points.json` | JSON | Identified knee points |

---

## 🔧 Configuration

```yaml
# science_config.yaml
phase4:
  mobo:
    n_initial_samples: 20
    n_iterations: 50
    batch_size: 1
    acquisition: "qEHVI"
  gp:
    kernel: "matern_2.5"
    ard: true
    normalize_inputs: true
  convergence:
    min_hv_improvement: 0.001
    patience: 5
  reference_point: [0.0, 0.0]
```

---

## 📈 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Pareto size | 15-25 points | Count |
| Knee points | ≥ 1 identified | H1 validation |
| HV at 30% budget | ≥ 95% of full HV | H2 validation |
| Convergence | < 50 iterations | Efficiency |

