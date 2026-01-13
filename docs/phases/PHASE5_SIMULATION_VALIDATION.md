# Phase V: Process Simulation & Validation

> Rigorous validation of Pareto-optimal candidates using DWSIM process simulation

## 🎯 Objective

Validate the top Pareto-optimal candidates from Phase IV through rigorous process simulation in DWSIM, producing a final ranked list of 10-20 entrainers with verified performance metrics.

---

## 📊 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE V PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input: 15-25 Pareto Candidates from Phase IV                          │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                  DWSIM Process Simulation                        │   │
│   │                                                                  │   │
│   │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │   │
│   │   │  Feed   │───▶│Extract. │───▶│Recovery │───▶│ Product │     │   │
│   │   │  Prep   │    │ Column  │    │ Column  │    │ Streams │     │   │
│   │   └─────────┘    └─────────┘    └─────────┘    └─────────┘     │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│           ┌───────────────┼───────────────┐                             │
│           ▼               ▼               ▼                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       │
│   │  Efficiency │ │   Energy    │ │   Safety    │                       │
│   │   Metrics   │ │   Metrics   │ │   Metrics   │                       │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                       │
│          │               │               │                              │
│          └───────────────┼───────────────┘                              │
│                          ▼                                              │
│   Output: Final Top 10-20 Ranking with Validated Metrics                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Process Configuration

### Extractive Distillation Flowsheet

```
                    ┌─────────────────┐
                    │   Entrainer     │
                    │   Recycle       │
                    └────────┬────────┘
                             │
                             ▼
┌─────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Feed   │────────▶│   Extractive    │────────▶│    Recovery     │
│ EtOH/H2O│         │    Column       │         │    Column       │
│ 10/90   │         │   (40 stages)   │         │   (20 stages)   │
└─────────┘         └────────┬────────┘         └────────┬────────┘
                             │                           │
                             ▼                           ▼
                    ┌─────────────────┐         ┌─────────────────┐
                    │  Ethanol        │         │  Water          │
                    │  Product        │         │  Product        │
                    │  (≥99.5%)       │         │                 │
                    └─────────────────┘         └─────────────────┘
```

### Simulation Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Feed composition | 10% EtOH, 90% H2O | mol% |
| Feed flow rate | 100 | kmol/h |
| Feed temperature | 298 | K |
| Operating pressure | 101.325 | kPa |
| Entrainer/Feed ratio | Variable (optimized) | mol/mol |
| Target purity | ≥ 99.5% | mol% EtOH |

---

## 🧮 DWSIM Automation

### COM Interface

```python
import win32com.client

class DWSIMSimulator:
    def __init__(self):
        self.dwsim = win32com.client.Dispatch("DWSIM.Automation.Automation")
        
    def run_simulation(self, entrainer_smiles: str, params: dict) -> dict:
        """Run extractive distillation simulation."""
        # Load base flowsheet
        flowsheet = self.dwsim.LoadFlowsheet("templates/extractive_distillation.dwxmz")
        
        # Configure entrainer
        self._set_entrainer(flowsheet, entrainer_smiles)
        
        # Set operating parameters
        self._set_parameters(flowsheet, params)
        
        # Run simulation
        flowsheet.Solve()
        
        # Extract results
        return self._extract_results(flowsheet)
```

### Thermodynamic Models

| Model | Application |
|-------|-------------|
| UNIFAC | Activity coefficients |
| NRTL | VLE calculations |
| Peng-Robinson | Vapor phase |
| UNIQUAC | Alternative activity model |

---

## 📊 Performance Metrics

### Efficiency Metrics

```python
@dataclass
class EfficiencyMetrics:
    ethanol_purity: float          # mol% in product
    ethanol_recovery: float        # % of feed ethanol
    entrainer_ratio: float         # mol entrainer / mol feed
    specific_energy: float         # kJ/mol ethanol
    column_stages: int             # Total stages required
```

### Energy Metrics

```python
@dataclass
class EnergyMetrics:
    reboiler_duty_extract: float   # kW
    reboiler_duty_recovery: float  # kW
    condenser_duty_extract: float  # kW
    condenser_duty_recovery: float # kW
    total_energy: float            # kW
```

### Safety Metrics (Validated)

```python
@dataclass
class SafetyMetrics:
    flash_point_k: float           # From simulation conditions
    max_temperature_k: float       # Highest T in process
    thermal_stability: bool        # Stable at max T?
    entrainer_losses: float        # kg/h lost to products
```

---

## 🎯 Validation Criteria

### Minimum Requirements

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Ethanol purity | ≥ 99.5 mol% | Product specification |
| Ethanol recovery | ≥ 98% | Economic viability |
| Convergence | Yes | Valid simulation |
| Thermal stability | Stable at T_max | Safety requirement |

### Benchmark Comparison

Compare against known entrainers:

| Entrainer | Purity | Recovery | Energy | Safety |
|-----------|--------|----------|--------|--------|
| Ethylene glycol | 99.7% | 99.1% | 45 kJ/mol | Medium |
| Glycerol | 99.5% | 98.5% | 52 kJ/mol | High |
| Benzene (negative) | 99.8% | 99.5% | 38 kJ/mol | Very Low |

---

## 📈 Final Ranking

### Composite Score

```python
def final_score(efficiency: EfficiencyMetrics, 
                energy: EnergyMetrics,
                safety: SafetyMetrics) -> float:
    """Calculate final composite score."""
    weights = {
        "purity": 0.15,
        "recovery": 0.15,
        "energy": 0.20,
        "safety": 0.50,  # Safety-by-Design emphasis
    }
    
    scores = {
        "purity": normalize(efficiency.ethanol_purity, 99.0, 99.9),
        "recovery": normalize(efficiency.ethanol_recovery, 95, 100),
        "energy": 1 - normalize(energy.total_energy, 30, 60),  # Lower is better
        "safety": safety.composite_score,
    }
    
    return sum(w * scores[k] for k, w in weights.items())
```

---

## 📁 Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `phase5_results.json` | JSON | All simulation results |
| `phase5_ranking.csv` | CSV | Final ranked list |
| `phase5_pareto_library.json` | JSON | Complete Pareto library |
| `simulation_logs/` | Directory | Individual simulation logs |

---

## 🔧 Configuration

```yaml
# science_config.yaml
phase5:
  dwsim:
    template: "templates/extractive_distillation.dwxmz"
    thermodynamic_model: "UNIFAC"
    max_iterations: 100
    tolerance: 1e-6
  process:
    feed_ethanol_mol_pct: 10
    feed_flow_kmol_h: 100
    target_purity_mol_pct: 99.5
    pressure_kpa: 101.325
  optimization:
    optimize_entrainer_ratio: true
    ratio_range: [0.5, 3.0]
  ranking:
    safety_weight: 0.50
    efficiency_weight: 0.30
    energy_weight: 0.20
```

---

## 📈 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Simulation success rate | ≥ 90% | Convergence count |
| Candidates meeting spec | ≥ 80% | Purity/recovery check |
| Safety improvement | ≥ 20% vs EG | Benchmark comparison |
| Energy penalty | ≤ 8% vs EG | Benchmark comparison |

