"""Multivariate plugin for AIML Dash."""

from aiml_dash.plugins.multivariate_plugin import callbacks
from aiml_dash.plugins.multivariate_plugin.layout import *
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the multivariate plugin definition."""
    
    pages = [
        PluginPage(
            id="conjoint", label="Conjoint", icon="carbon:chart-multitype",
            section="Multivariate", order=1, layout=conjoint_layout,
            description="Conjoint analysis"
        ),
        PluginPage(
            id="full-factor", label="Full Factor", icon="carbon:chart-3d",
            section="Multivariate", order=2, layout=fullfactor_layout,
            description="Full factorial analysis"
        ),
        PluginPage(
            id="hierarchical-cluster", label="Hierarchical Cluster", icon="carbon:network-3",
            section="Multivariate", order=3, layout=hierarchicalcluster_layout,
            description="Hierarchical clustering"
        ),
        PluginPage(
            id="kmeans-cluster", label="K-Means Cluster", icon="carbon:network-4",
            section="Multivariate", order=4, layout=kmeanscluster_layout,
            description="K-means clustering"
        ),
        PluginPage(
            id="mds", label="MDS", icon="carbon:chart-scatter",
            section="Multivariate", order=5, layout=mds_layout,
            description="Multidimensional scaling"
        ),
        PluginPage(
            id="perceptual-map", label="Perceptual Map", icon="carbon:map",
            section="Multivariate", order=6, layout=perceptualmap_layout,
            description="Perceptual mapping"
        ),
        PluginPage(
            id="pre-factor", label="Pre-Factor", icon="carbon:chart-area",
            section="Multivariate", order=7, layout=prefactor_layout,
            description="Factor analysis"
        ),
    ]
    
    return Plugin(
        id="multivariate",
        name="Multivariate",
        description="Multivariate analysis tools",
        pages=pages,
        version="1.0.0",
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
