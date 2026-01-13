"""
Configuration Management
========================

Centralized configuration using Pydantic Settings with YAML file support.
Supports environment-specific overrides and .env file loading.

Usage:
    from entrainer_selection.core.config import get_settings

    settings = get_settings()
    print(settings.databases.neo4j.uri)
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# =============================================================================
# Nested Configuration Models
# =============================================================================

class Neo4jConfig(BaseModel):
    """Neo4j database configuration."""
    uri: str = "bolt://localhost:7687"
    database: str = "neo4j"
    max_connection_pool_size: int = 50
    connection_timeout: int = 30


class ChromaDBConfig(BaseModel):
    """ChromaDB vector database configuration."""
    persist_directory: str = "./data/chromadb"
    collection_name: str = "entrainer_embeddings"
    embedding_model: str = "all-MiniLM-L6-v2"


class DatabasesConfig(BaseModel):
    """All database configurations."""
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
    chromadb: ChromaDBConfig = Field(default_factory=ChromaDBConfig)


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = "google"
    model: str = "gemini-3-pro-preview"
    temperature: float = 0.0
    max_output_tokens: int = 65535
    top_p: float = 0.95


class PubChemConfig(BaseModel):
    """PubChem API configuration."""
    base_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    rate_limit_requests_per_second: int = 5
    max_retries: int = 3
    timeout: int = 30


class Phase1Config(BaseModel):
    """Phase I: Domain Mapping configuration."""
    pubchem: PubChemConfig = Field(default_factory=PubChemConfig)
    smarts_patterns: Dict[str, str] = Field(default_factory=dict)
    target_clusters: int = 500
    min_molecules_per_cluster: int = 10


class SafetyVerificationConfig(BaseModel):
    """Safety data verification configuration."""
    primary_source: str = "pubchem_pug"
    fallback_to_llm: bool = True
    required_ghs_categories: List[str] = Field(
        default_factory=lambda: ["acute_toxicity", "flammability", "health_hazard"]
    )


class GraphRAGConfig(BaseModel):
    """Graph-RAG configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 10


class Phase2AConfig(BaseModel):
    """Phase II-A: Graph-RAG Engine configuration."""
    graph_rag: GraphRAGConfig = Field(default_factory=GraphRAGConfig)
    safety_verification: SafetyVerificationConfig = Field(default_factory=SafetyVerificationConfig)


class ClusteringConfig(BaseModel):
    """Cheminformatics clustering configuration."""
    fingerprint_type: str = "morgan"
    fingerprint_radius: int = 2
    fingerprint_bits: int = 2048


class DiversityConfig(BaseModel):
    """Diversity selection configuration with CRITICAL FIX thresholds."""
    tanimoto_similarity_threshold: float = 0.80  # CRITICAL FIX: Was 0.5
    tanimoto_scaffold_hop_threshold: float = 0.50
    max_cluster_size: int = 50
    min_diversity_score: float = 0.3


class Phase2CConfig(BaseModel):
    """Phase II-C: Cheminformatics Clustering configuration."""
    clustering: ClusteringConfig = Field(default_factory=ClusteringConfig)
    diversity: DiversityConfig = Field(default_factory=DiversityConfig)


class TraversalConfig(BaseModel):
    """Graph traversal configuration."""
    max_depth: int = 3
    max_neighbors_per_node: int = 20
    similarity_threshold: float = 0.75  # CRITICAL FIX: Was 0.5


class Phase3Config(BaseModel):
    """Phase III: Graph Traversal configuration."""
    traversal: TraversalConfig = Field(default_factory=TraversalConfig)


class MOBOConfig(BaseModel):
    """Multi-Objective Bayesian Optimization configuration."""
    acquisition_function: str = "qEHVI"
    num_initial_samples: int = 20
    batch_size: int = 5
    max_iterations: int = 50


class ConstraintsConfig(BaseModel):
    """Optimization constraints with CRITICAL FIX."""
    enable_ternary_azeotrope_check: bool = True  # CRITICAL FIX
    min_selectivity: float = 1.5
    max_viscosity: float = 10.0
    min_thermal_stability: float = 150.0


class Phase4Config(BaseModel):
    """Phase IV: Bayesian Optimization configuration."""
    mobo: MOBOConfig = Field(default_factory=MOBOConfig)
    constraints: ConstraintsConfig = Field(default_factory=ConstraintsConfig)


# =============================================================================
# Main Settings Class
# =============================================================================

class Settings(BaseSettings):
    """
    Main application settings.

    Loads configuration from:
    1. config/settings.yaml (base configuration)
    2. config/settings.local.yaml (local overrides, git-ignored)
    3. Environment variables (highest priority)
    4. .env file
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Environment variables (loaded from .env)
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: Optional[str] = Field(default=None, alias="NEO4J_PASSWORD")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # Nested configurations (loaded from YAML)
    databases: DatabasesConfig = Field(default_factory=DatabasesConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    phase_1: Phase1Config = Field(default_factory=Phase1Config)
    phase_2a: Phase2AConfig = Field(default_factory=Phase2AConfig)
    phase_2c: Phase2CConfig = Field(default_factory=Phase2CConfig)
    phase_3: Phase3Config = Field(default_factory=Phase3Config)
    phase_4: Phase4Config = Field(default_factory=Phase4Config)
    phase_5: Phase5Config = Field(default_factory=Phase5Config)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Settings":
        """Load settings from a YAML file."""
        if not yaml_path.exists():
            return cls()

        with open(yaml_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}

        return cls(**yaml_data)

    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.paths.data_root,
            self.paths.raw_data,
            self.paths.processed_data,
            self.paths.models,
            self.paths.outputs,
            self.paths.cache,
            self.logging.log_directory,
            self.databases.chromadb.persist_directory,
        ]
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


def _load_yaml_config() -> Dict[str, Any]:
    """Load YAML configuration files."""
    config_dir = Path("config")
    base_config_path = config_dir / "settings.yaml"
    local_config_path = config_dir / "settings.local.yaml"

    config_data: Dict[str, Any] = {}

    # Load base configuration
    if base_config_path.exists():
        with open(base_config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

    # Merge local overrides
    if local_config_path.exists():
        with open(local_config_path, "r", encoding="utf-8") as f:
            local_data = yaml.safe_load(f) or {}
            config_data = _deep_merge(config_data, local_data)

    return config_data


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Settings are loaded once and cached for the lifetime of the application.
    To reload settings, call get_settings.cache_clear() first.

    Returns:
        Settings: Application settings instance
    """
    yaml_config = _load_yaml_config()
    settings = Settings(**yaml_config)
    settings.ensure_directories()
    return settings
