"""
aiml.experiments
================

Experiment tracking, management, and reporting for end-to-end EDA and
machine learning workflows.

Public API::

    from aiml.experiments import Experiment, ExperimentRegistry, ExperimentStatus

See :class:`~aiml.experiments.experiment.Experiment` and
:class:`~aiml.experiments.registry.ExperimentRegistry` for full documentation.
"""

from aiml.experiments.experiment import Experiment, ExperimentStatus
from aiml.experiments.registry import ExperimentRegistry

__all__ = [
    "Experiment",
    "ExperimentRegistry",
    "ExperimentStatus",
]
