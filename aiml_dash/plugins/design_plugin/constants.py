"""Constants for the design plugin.

This module defines plugin-specific constants used throughout the design plugin,
including page IDs, display labels, and plugin metadata.
"""

# Plugin metadata
PLUGIN_ID = "design"
PLUGIN_NAME = "Design"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Design of experiments and sampling tools"

# Section and ordering
SECTION_NAME = "Design"

# Page identifiers
DOE_ID = "doe"
RANDOMIZER_ID = "randomizer"
SAMPLE_SIZE_ID = "sample-size"
SAMPLE_SIZE_COMPARE_ID = "sample-size-comp"
SAMPLING_ID = "sampling"

# Icons
DOE_ICON = "carbon:chemistry"
RANDOMIZER_ICON = "carbon:shuffle"
SAMPLE_SIZE_ICON = "carbon:data-share"
SAMPLE_SIZE_COMPARE_ICON = "carbon:compare"
SAMPLING_ICON = "carbon:data-1"

# Layout configuration
CONTAINER_SIZE = "fluid"

PAGE_DEFINITIONS = [
    {"id": DOE_ID, "label": "Design of Experiments", "icon": DOE_ICON, "section": SECTION_NAME, "order": 1, "description": "Design experiments"},
    {"id": RANDOMIZER_ID, "label": "Randomizer", "icon": RANDOMIZER_ICON, "section": SECTION_NAME, "order": 2, "description": "Randomize treatments"},
    {"id": SAMPLE_SIZE_ID, "label": "Sample Size", "icon": SAMPLE_SIZE_ICON, "section": SECTION_NAME, "order": 3, "description": "Calculate sample size"},
    {"id": SAMPLE_SIZE_COMPARE_ID, "label": "Sample Size Compare", "icon": SAMPLE_SIZE_COMPARE_ICON, "section": SECTION_NAME, "order": 4, "description": "Compare sample sizes"},
    {"id": SAMPLING_ID, "label": "Sampling", "icon": SAMPLING_ICON, "section": SECTION_NAME, "order": 5, "description": "Sampling methods"},
]
