"""Constants for the multivariate plugin.

This module defines plugin-specific constants used throughout the multivariate
plugin, including page IDs, display labels, and plugin metadata.
"""

# Plugin metadata
PLUGIN_ID = "multivariate"
PLUGIN_NAME = "Multivariate"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Multivariate analysis tools"

# Section and ordering
SECTION_NAME = "Multivariate"

# Page identifiers
CONJOINT_ID = "conjoint"
FULL_FACTOR_ID = "full-factor"
HIERARCHICAL_CLUSTER_ID = "hierarchical-cluster"
KMEANS_CLUSTER_ID = "kmeans-cluster"
MDS_ID = "mds"
PERCEPTUAL_MAP_ID = "perceptual-map"
PRE_FACTOR_ID = "pre-factor"

# Icons
CONJOINT_ICON = "carbon:chart-multitype"
FULL_FACTOR_ICON = "carbon:chart-3d"
HIERARCHICAL_CLUSTER_ICON = "carbon:network-3"
KMEANS_CLUSTER_ICON = "carbon:network-4"
MDS_ICON = "carbon:chart-scatter"
PERCEPTUAL_MAP_ICON = "carbon:map"
PRE_FACTOR_ICON = "carbon:chart-area"

# Layout configuration
CONTAINER_SIZE = "fluid"

PAGE_DEFINITIONS = [
    {"id": CONJOINT_ID, "label": "Conjoint", "icon": CONJOINT_ICON, "section": SECTION_NAME, "order": 1, "description": "Conjoint analysis"},
    {"id": FULL_FACTOR_ID, "label": "Full Factor", "icon": FULL_FACTOR_ICON, "section": SECTION_NAME, "order": 2, "description": "Full factorial analysis"},
    {"id": HIERARCHICAL_CLUSTER_ID, "label": "Hierarchical Cluster", "icon": HIERARCHICAL_CLUSTER_ICON, "section": SECTION_NAME, "order": 3, "description": "Hierarchical clustering"},
    {"id": KMEANS_CLUSTER_ID, "label": "K-Means Cluster", "icon": KMEANS_CLUSTER_ICON, "section": SECTION_NAME, "order": 4, "description": "K-means clustering"},
    {"id": MDS_ID, "label": "MDS", "icon": MDS_ICON, "section": SECTION_NAME, "order": 5, "description": "Multidimensional scaling"},
    {"id": PERCEPTUAL_MAP_ID, "label": "Perceptual Map", "icon": PERCEPTUAL_MAP_ICON, "section": SECTION_NAME, "order": 6, "description": "Perceptual mapping"},
    {"id": PRE_FACTOR_ID, "label": "Pre-Factor", "icon": PRE_FACTOR_ICON, "section": SECTION_NAME, "order": 7, "description": "Factor analysis"},
]
