"""
Pages Package
=============

Contains all page modules for the AIML Dash application.
Organized by functionality:
- data: Data-related pages (manage, view, explore, transform, visualize, pivot, combine, report)
- design: Experimental design pages (doe, sampling, sample_size, sample_size_comp, randomizer)
- model: Statistical modeling pages (regression, classification, trees, evaluation, etc.)
- multivariate: Multivariate analysis pages (factor analysis, clustering, MDS, conjoint)
- basics: Basic statistics pages (means, proportions, correlation, hypothesis tests)

Note: Subpackages are not imported automatically to avoid circular dependencies.
Import specific modules as needed.
"""

__all__ = ["basics", "data", "design", "model", "multivariate"]
