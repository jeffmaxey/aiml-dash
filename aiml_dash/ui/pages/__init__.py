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
"""

# Import subpackages for convenience
from . import data, design, model, multivariate, basics

__all__ = ["data", "design", "model", "multivariate", "basics"]
