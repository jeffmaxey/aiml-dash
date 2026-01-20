"""
Design Pages Package
====================

All experimental design pages for the AIML application.
Includes: DOE, Sampling, Sample Size, Sample Size Comparison, Randomizer
"""

from . import doe, randomizer, sample_size, sample_size_comp, sampling

__all__ = [
    "doe",
    "randomizer",
    "sample_size",
    "sample_size_comp",
    "sampling",
]
