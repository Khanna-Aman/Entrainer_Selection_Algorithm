# Contributing to Safety-by-Design Entrainer Selection

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold respectful and inclusive behavior.

---

## Getting Started

### Prerequisites

1. Python 3.11+
2. Git
3. Neo4j (for graph-related development)
4. DWSIM (for Phase V development, Windows only)

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/entrainer-selection.git
cd entrainer-selection

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Copy configuration templates
cp config/infra_config.example.yaml config/infra_config.yaml
```

---

## Development Workflow

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/description` | `feature/add-tanimoto-similarity` |
| Bug Fix | `fix/description` | `fix/pubchem-rate-limit` |
| Documentation | `docs/description` | `docs/phase2-api-reference` |
| Refactor | `refactor/description` | `refactor/engine-interface` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(phase2): add TRIZ contradiction matrix lookup
fix(core): handle PubChem 503 errors with retry
docs(readme): update installation instructions
test(phase4): add GP surrogate unit tests
```

---

## Code Standards

### Style Guide

- **Formatter**: Black (line length 88)
- **Import Sorting**: isort
- **Linting**: flake8
- **Type Hints**: Required for all public functions

### Pre-commit Checks

```bash
# Run all checks manually
pre-commit run --all-files

# Individual tools
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Documentation

- All public functions require docstrings (Google style)
- Complex algorithms need inline comments
- Update relevant docs when changing behavior

```python
def calculate_safety_score(molecule: Molecule, weights: dict[str, float]) -> float:
    """Calculate composite safety score for a molecule.

    Args:
        molecule: Molecule object with computed properties.
        weights: Dictionary mapping property names to weights.

    Returns:
        Weighted safety score between 0 (unsafe) and 1 (safe).

    Raises:
        ValueError: If required properties are missing.

    Example:
        >>> mol = Molecule(smiles="CCO")
        >>> score = calculate_safety_score(mol, {"flash_point": 0.3, "ld50": 0.7})
    """
```

---

## Testing Requirements

### Test Structure

```
tests/
├── unit/
│   ├── test_core/
│   ├── test_phase1/
│   └── ...
├── integration/
│   ├── test_database/
│   └── test_api/
└── conftest.py
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific phase
pytest tests/unit/test_phase2/

# Integration tests (requires services)
pytest tests/integration/ -m integration
```

### Coverage Requirements

- Minimum 80% coverage for new code
- Critical paths (MOBO, safety scoring) require 90%+

---

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Pre-commit hooks pass
3. ✅ Documentation updated
4. ✅ No merge conflicts with main

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests (if applicable)
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. Submit PR against `main` branch
2. Automated checks must pass
3. At least one maintainer review required
4. Address feedback promptly
5. Squash and merge when approved

---

## Areas for Contribution

### High Priority

- [ ] Additional safety property calculators
- [ ] Alternative acquisition functions for MOBO
- [ ] Performance optimization for graph traversal
- [ ] Additional DWSIM thermodynamic models

### Documentation

- [ ] API reference improvements
- [ ] Tutorial notebooks
- [ ] Phase-specific guides

### Testing

- [ ] Edge case coverage
- [ ] Property-based tests
- [ ] Performance benchmarks

---

## Questions?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Tag maintainers for urgent items

Thank you for contributing! 🎉

