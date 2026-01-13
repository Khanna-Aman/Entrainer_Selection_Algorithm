"""
Phase III: Graph Traversal & Expansion
======================================

Neo4j-based molecular similarity exploration:
- Breadth-first traversal from seed molecules
- Similarity-based edge creation
- Scaffold hopping for novel candidates

Key Components:
- GraphTraverser: BFS/DFS traversal algorithms
- SimilarityNetworkBuilder: Edge creation based on Tanimoto
- ScaffoldHopper: Novel structure generation
- ExpansionOrchestrator: Main coordinator

CRITICAL FIX Applied:
- Similarity threshold: 0.75 (was 0.5)
- Scaffold hop threshold: 0.50 (for exploration only)
- Clear separation between exploitation (high similarity) and exploration (scaffold hopping)

Output:
- Expanded candidate set
- Similarity network for visualization
- Traversal paths for explainability
"""

__all__ = []

