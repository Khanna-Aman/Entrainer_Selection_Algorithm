"""
Phase II-C: Cheminformatics & Diversity Clustering
==================================================

RDKit-based molecular analysis and diversity selection:
- Morgan fingerprint generation
- Tanimoto similarity calculations
- Diversity-based clustering

Key Components:
- FingerprintGenerator: Morgan/MACCS fingerprint calculation
- SimilarityCalculator: Tanimoto coefficient computation
- DiversitySelector: MaxMin diversity selection
- ClusterAnalyzer: Cluster quality metrics

CRITICAL FIX Applied:
- Tanimoto threshold tightened from 0.5 to 0.75-0.85
- 0.5 threshold used ONLY for scaffold hopping (exploration)
- 0.75+ threshold used for similarity edges (exploitation)

Output:
- Diversity-selected candidate molecules
- Cluster assignments and quality metrics
"""

__all__ = []

