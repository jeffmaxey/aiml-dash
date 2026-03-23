"""Multivariate plugin definition.

This module defines the multivariate plugin for AIML Dash and its page registry.
"""

from aiml_dash.plugins.models import Plugin, PluginPage
from aiml_dash.plugins.multivariate_plugin import callbacks
from aiml_dash.plugins.multivariate_plugin.constants import (
    CONJOINT_ICON, CONJOINT_ID, FULL_FACTOR_ICON, FULL_FACTOR_ID,
    HIERARCHICAL_CLUSTER_ICON, HIERARCHICAL_CLUSTER_ID, KMEANS_CLUSTER_ICON,
    KMEANS_CLUSTER_ID, MDS_ICON, MDS_ID, PERCEPTUAL_MAP_ICON,
    PERCEPTUAL_MAP_ID, PLUGIN_DESCRIPTION, PLUGIN_ID, PLUGIN_NAME,
    PLUGIN_VERSION, PRE_FACTOR_ICON, PRE_FACTOR_ID, SECTION_NAME)
from aiml_dash.plugins.multivariate_plugin.layout import (
    conjoint_layout, fullfactor_layout, hierarchicalcluster_layout,
    kmeanscluster_layout, mds_layout, perceptualmap_layout, prefactor_layout)


def get_plugin() -> Plugin:
    """Return the multivariate plugin definition.

    Returns
    -------
    value : Plugin
        Result produced by this function."""

    pages = [
        PluginPage(
            id=CONJOINT_ID,
            label="Conjoint",
            icon=CONJOINT_ICON,
            section=SECTION_NAME,
            order=1,
            layout=conjoint_layout,
            description="Conjoint analysis",
        ),
        PluginPage(
            id=FULL_FACTOR_ID,
            label="Full Factor",
            icon=FULL_FACTOR_ICON,
            section=SECTION_NAME,
            order=2,
            layout=fullfactor_layout,
            description="Full factorial analysis",
        ),
        PluginPage(
            id=HIERARCHICAL_CLUSTER_ID,
            label="Hierarchical Cluster",
            icon=HIERARCHICAL_CLUSTER_ICON,
            section=SECTION_NAME,
            order=3,
            layout=hierarchicalcluster_layout,
            description="Hierarchical clustering",
        ),
        PluginPage(
            id=KMEANS_CLUSTER_ID,
            label="K-Means Cluster",
            icon=KMEANS_CLUSTER_ICON,
            section=SECTION_NAME,
            order=4,
            layout=kmeanscluster_layout,
            description="K-means clustering",
        ),
        PluginPage(
            id=MDS_ID,
            label="MDS",
            icon=MDS_ICON,
            section=SECTION_NAME,
            order=5,
            layout=mds_layout,
            description="Multidimensional scaling",
        ),
        PluginPage(
            id=PERCEPTUAL_MAP_ID,
            label="Perceptual Map",
            icon=PERCEPTUAL_MAP_ICON,
            section=SECTION_NAME,
            order=6,
            layout=perceptualmap_layout,
            description="Perceptual mapping",
        ),
        PluginPage(
            id=PRE_FACTOR_ID,
            label="Pre-Factor",
            icon=PRE_FACTOR_ICON,
            section=SECTION_NAME,
            order=7,
            layout=prefactor_layout,
            description="Factor analysis",
        ),
    ]

    return Plugin(
        id=PLUGIN_ID,
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        pages=pages,
        version=PLUGIN_VERSION,
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
