"""
Multivariate Analysis Pages Module
===================================

This module contains all multivariate analysis pages for the AIML Dash application.
"""

from . import (
    pre_factor,
    full_factor,
    kmeans_cluster,
    hierarchical_cluster,
    perceptual_map,
    mds,
    conjoint,
)

__all__ = [
    "pre_factor",
    "full_factor",
    "kmeans_cluster",
    "hierarchical_cluster",
    "perceptual_map",
    "mds",
    "conjoint",
]
