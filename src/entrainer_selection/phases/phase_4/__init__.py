"""
Phase IV: Multi-Objective Bayesian Optimization
================================================

BoTorch-based Pareto optimization:
- qEHVI acquisition function
- Multi-objective: Efficiency, Safety, Cost
- Constraint handling for safety barriers

Key Components:
- MOBOOptimizer: Main optimization loop
- ObjectiveCalculator: Efficiency/Safety/Cost scoring
- ConstraintHandler: Safety barrier functions
- ParetoAnalyzer: Frontier analysis and knee point detection
- UNIFACOracle: Property estimation for efficiency

CRITICAL FIX Applied:
- Ternary azeotrope check in Oracle (not just Phase V)
- If ternary azeotrope exists, efficiency score = 0
- Safety barrier uses VERIFIED GHS data only

Output:
- Pareto frontier molecules
- Top 10 candidates for Phase V
- Optimization history and hypervolume
"""

__all__ = []

