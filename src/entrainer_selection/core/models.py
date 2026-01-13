"""
Core Data Models
================

Pydantic models for data validation across all phases.
These models ensure type safety and data integrity throughout the pipeline.

Usage:
    from entrainer_selection.core.models import Molecule, SafetyProfile, SimulationResult
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Enums
# =============================================================================

class GHSCategory(str, Enum):
    """GHS hazard categories."""
    CATEGORY_1 = "1"
    CATEGORY_2 = "2"
    CATEGORY_3 = "3"
    CATEGORY_4 = "4"
    CATEGORY_5 = "5"
    NOT_CLASSIFIED = "NC"


class DataSource(str, Enum):
    """Data source identifiers."""
    PUBCHEM = "pubchem"
    COMPTOX = "comptox"
    LLM_EXTRACTED = "llm_extracted"
    LITERATURE = "literature"
    CALCULATED = "calculated"


class PhaseStatus(str, Enum):
    """Processing status for each phase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# =============================================================================
# Core Molecule Models
# =============================================================================

class MoleculeIdentifiers(BaseModel):
    """Molecule identification data."""
    smiles: str = Field(..., description="Canonical SMILES string")
    inchi: Optional[str] = Field(None, description="InChI identifier")
    inchi_key: Optional[str] = Field(None, description="InChI key")
    cas_number: Optional[str] = Field(None, description="CAS registry number")
    pubchem_cid: Optional[int] = Field(None, description="PubChem compound ID")

    @field_validator("smiles")
    @classmethod
    def validate_smiles(cls, v: str) -> str:
        """Basic SMILES validation."""
        if not v or len(v) < 1:
            raise ValueError("SMILES string cannot be empty")
        return v


class PhysicalProperties(BaseModel):
    """Physical properties of a molecule."""
    molecular_weight: Optional[float] = Field(None, ge=0, description="Molecular weight (g/mol)")
    boiling_point: Optional[float] = Field(None, description="Boiling point (°C)")
    melting_point: Optional[float] = Field(None, description="Melting point (°C)")
    density: Optional[float] = Field(None, ge=0, description="Density (g/cm³)")
    viscosity: Optional[float] = Field(None, ge=0, description="Viscosity (cP)")
    vapor_pressure: Optional[float] = Field(None, ge=0, description="Vapor pressure (mmHg at 25°C)")
    flash_point: Optional[float] = Field(None, description="Flash point (°C)")

    # Antoine equation coefficients
    antoine_a: Optional[float] = None
    antoine_b: Optional[float] = None
    antoine_c: Optional[float] = None


class SafetyProfile(BaseModel):
    """Safety and hazard information."""
    # GHS Classifications
    acute_toxicity_oral: Optional[GHSCategory] = None
    acute_toxicity_dermal: Optional[GHSCategory] = None
    acute_toxicity_inhalation: Optional[GHSCategory] = None
    flammability: Optional[GHSCategory] = None
    health_hazard: Optional[GHSCategory] = None
    environmental_hazard: Optional[GHSCategory] = None

    # Quantitative data
    ld50_oral: Optional[float] = Field(None, ge=0, description="LD50 oral (mg/kg)")
    ld50_dermal: Optional[float] = Field(None, ge=0, description="LD50 dermal (mg/kg)")
    lc50_inhalation: Optional[float] = Field(None, ge=0, description="LC50 inhalation (mg/L)")

    # Data provenance
    data_source: DataSource = DataSource.PUBCHEM
    verification_status: str = "unverified"

    def compute_safety_score(self) -> float:
        """
        Compute normalized safety score (0-1, higher is safer).

        CRITICAL: This uses verified GHS data, not LLM-extracted values.
        """
        score = 1.0

        # Penalize based on GHS categories (lower category = more hazardous)
        category_penalties = {
            GHSCategory.CATEGORY_1: 0.4,
            GHSCategory.CATEGORY_2: 0.3,
            GHSCategory.CATEGORY_3: 0.2,
            GHSCategory.CATEGORY_4: 0.1,
            GHSCategory.CATEGORY_5: 0.05,
            GHSCategory.NOT_CLASSIFIED: 0.0,
        }

        for attr in ["acute_toxicity_oral", "flammability", "health_hazard"]:
            category = getattr(self, attr)
            if category:
                score -= category_penalties.get(category, 0)

        return max(0.0, min(1.0, score))


class EntrainerEfficiency(BaseModel):
    """Entrainer efficiency metrics for ethanol-water separation."""
    # Selectivity at infinite dilution
    selectivity_inf: Optional[float] = Field(None, ge=0, description="S∞ = γ_water∞ / γ_ethanol∞")

    # Capacity
    capacity: Optional[float] = Field(None, ge=0, description="Entrainer capacity")

    # Performance index
    performance_index: Optional[float] = Field(None, description="PI = S∞ × capacity")

    # UNIFAC-calculated activity coefficients
    gamma_ethanol_inf: Optional[float] = None
    gamma_water_inf: Optional[float] = None

    # Azeotrope breaking capability
    breaks_azeotrope: Optional[bool] = None
    forms_ternary_azeotrope: Optional[bool] = None  # CRITICAL FIX: Check for ternary azeotropes

    def compute_efficiency_score(self) -> float:
        """
        Compute normalized efficiency score (0-1, higher is better).

        CRITICAL: Returns 0 if ternary azeotrope is formed.
        """
        if self.forms_ternary_azeotrope:
            return 0.0

        if self.selectivity_inf is None:
            return 0.0

        # Normalize selectivity (typical range 1-10)
        normalized = min(1.0, (self.selectivity_inf - 1) / 9)
        return max(0.0, normalized)


class Molecule(BaseModel):
    """
    Complete molecule representation used across all phases.

    This is the central data model that accumulates information
    as the molecule progresses through the pipeline.
    """
    # Identification
    identifiers: MoleculeIdentifiers
    name: str = Field(..., description="Common name")
    iupac_name: Optional[str] = None

    # Properties
    physical_properties: PhysicalProperties = Field(default_factory=PhysicalProperties)
    safety_profile: SafetyProfile = Field(default_factory=SafetyProfile)
    efficiency: EntrainerEfficiency = Field(default_factory=EntrainerEfficiency)

    # Classification
    functional_groups: List[str] = Field(default_factory=list)
    cluster_id: Optional[str] = None

    # Phase tracking
    phase_status: Dict[str, PhaseStatus] = Field(default_factory=dict)

    # Scores (computed during optimization)
    efficiency_score: Optional[float] = None
    safety_score: Optional[float] = None
    cost_score: Optional[float] = None
    pareto_rank: Optional[int] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[DataSource] = Field(default_factory=list)

    def update_scores(self) -> None:
        """Recompute all scores from underlying data."""
        self.safety_score = self.safety_profile.compute_safety_score()
        self.efficiency_score = self.efficiency.compute_efficiency_score()
        self.updated_at = datetime.utcnow()


# =============================================================================
# Simulation Models
# =============================================================================

class ColumnSpecification(BaseModel):
    """Distillation column specification."""
    num_stages: int = Field(..., ge=1, description="Number of theoretical stages")
    feed_stage: int = Field(..., ge=1, description="Feed stage location")
    reflux_ratio: float = Field(..., ge=0, description="Reflux ratio")
    entrainer_feed_stage: Optional[int] = None
    entrainer_to_feed_ratio: Optional[float] = None


class SimulationResult(BaseModel):
    """Results from Phase V process simulation."""
    molecule_id: str

    # Product specifications
    ethanol_purity: float = Field(..., ge=0, le=1, description="Ethanol mole fraction in product")
    water_purity: float = Field(..., ge=0, le=1, description="Water mole fraction in bottoms")

    # Energy consumption
    reboiler_duty: float = Field(..., ge=0, description="Reboiler duty (kW)")
    condenser_duty: float = Field(..., ge=0, description="Condenser duty (kW)")
    total_energy: float = Field(..., ge=0, description="Total energy consumption (kW)")

    # Entrainer performance
    entrainer_circulation_rate: float = Field(..., ge=0, description="Entrainer flow (kmol/h)")
    entrainer_loss: float = Field(..., ge=0, description="Entrainer loss fraction")

    # Column specifications used
    extractive_column: ColumnSpecification
    recovery_column: ColumnSpecification

    # Validation
    converged: bool = True
    simulation_engine: str = "dwsim"
    simulation_time: float = Field(..., ge=0, description="Simulation time (seconds)")

    # Comparison with benchmark
    benchmark_comparison: Optional[Dict[str, float]] = None


# =============================================================================
# Phase Output Models
# =============================================================================

class Phase1Output(BaseModel):
    """Output from Phase I: Domain Mapping."""
    clusters: List[Dict[str, Any]]
    total_molecules: int
    functional_group_distribution: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Phase2Output(BaseModel):
    """Output from Phase II: Multi-Vector Selection."""
    selected_molecules: List[Molecule]
    graph_rag_candidates: List[str]  # SMILES
    triz_candidates: List[str]
    clustering_candidates: List[str]
    consensus_candidates: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Phase3Output(BaseModel):
    """Output from Phase III: Graph Traversal."""
    expanded_molecules: List[Molecule]
    traversal_paths: List[Dict[str, Any]]
    similarity_network: Dict[str, List[str]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Phase4Output(BaseModel):
    """Output from Phase IV: Bayesian Optimization."""
    pareto_frontier: List[Molecule]
    optimization_history: List[Dict[str, Any]]
    hypervolume_history: List[float]
    best_candidates: List[Molecule]  # Top 10 for Phase V
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Phase5Output(BaseModel):
    """Output from Phase V: Simulation Validation."""
    simulation_results: List[SimulationResult]
    final_ranking: List[Molecule]
    benchmark_comparison: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
