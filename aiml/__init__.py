"""
aiml – Exploratory Data Analytics and Machine Learning
=======================================================

A unified Python API for model construction, evaluation, selection, and
prediction.

Supervised Learning
-------------------
Linear models::

    from aiml.supervised.linear import LinearRegression, LogisticRegression

Generalised linear models (regularised)::

    from aiml.supervised.glm import Ridge, Lasso, ElasticNet

Decision trees and ensembles::

    from aiml.supervised.trees import (
        DecisionTreeRegressor, DecisionTreeClassifier,
        RandomForestRegressor, RandomForestClassifier,
        GradientBoostingRegressor, GradientBoostingClassifier,
    )

Unsupervised Learning
---------------------
::

    from aiml.unsupervised.pca import PCA
    from aiml.unsupervised.clustering import HierarchicalClustering, KMeans

Deep Learning
-------------
::

    from aiml.deep_learning.neural_network import NeuralNetwork

Model Selection
---------------
::

    from aiml.model_selection import cross_validate, grid_search, compare_models

Experiments
-----------
Track, log, compare, save, and export end-to-end ML experiments::

    from aiml.experiments import Experiment, ExperimentRegistry
"""

from aiml.base import BaseModel
from aiml.deep_learning.neural_network import NeuralNetwork
from aiml.experiments.experiment import Experiment, ExperimentStatus
from aiml.experiments.registry import ExperimentRegistry
from aiml.model_selection import compare_models, cross_validate, grid_search, random_search
from aiml.supervised.glm import ElasticNet, Lasso, Ridge
from aiml.supervised.linear import LinearRegression, LogisticRegression
from aiml.supervised.trees import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from aiml.unsupervised.clustering import HierarchicalClustering, KMeans
from aiml.unsupervised.pca import PCA

__version__ = "0.1.0"

__all__ = [
    # Base
    "BaseModel",
    # Supervised – linear
    "LinearRegression",
    "LogisticRegression",
    # Supervised – GLM
    "Ridge",
    "Lasso",
    "ElasticNet",
    # Supervised – trees
    "DecisionTreeRegressor",
    "DecisionTreeClassifier",
    "RandomForestRegressor",
    "RandomForestClassifier",
    "GradientBoostingRegressor",
    "GradientBoostingClassifier",
    # Unsupervised
    "PCA",
    "HierarchicalClustering",
    "KMeans",
    # Deep learning
    "NeuralNetwork",
    # Model selection
    "cross_validate",
    "grid_search",
    "random_search",
    "compare_models",
    # Experiments
    "Experiment",
    "ExperimentRegistry",
    "ExperimentStatus",
]
