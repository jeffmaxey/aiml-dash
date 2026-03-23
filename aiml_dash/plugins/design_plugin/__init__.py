"""Design plugin definition.

This module defines the design plugin for AIML Dash and its page registry.
"""

from aiml_dash.plugins.design_plugin import callbacks
from aiml_dash.plugins.design_plugin.constants import (
    DOE_ICON, DOE_ID, PLUGIN_DESCRIPTION, PLUGIN_ID, PLUGIN_NAME,
    PLUGIN_VERSION, RANDOMIZER_ICON, RANDOMIZER_ID, SAMPLE_SIZE_COMPARE_ICON,
    SAMPLE_SIZE_COMPARE_ID, SAMPLE_SIZE_ICON, SAMPLE_SIZE_ID, SAMPLING_ICON,
    SAMPLING_ID, SECTION_NAME)
from aiml_dash.plugins.design_plugin.layout import (doe_layout,
                                                    randomizer_layout,
                                                    samplesize_layout,
                                                    samplesizecomp_layout,
                                                    sampling_layout)
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the design plugin definition.

    Returns
    -------
    value : Plugin
        Result produced by this function."""

    pages = [
        PluginPage(
            id=DOE_ID,
            label="Design of Experiments",
            icon=DOE_ICON,
            section=SECTION_NAME,
            order=1,
            layout=doe_layout,
            description="Design experiments",
        ),
        PluginPage(
            id=RANDOMIZER_ID,
            label="Randomizer",
            icon=RANDOMIZER_ICON,
            section=SECTION_NAME,
            order=2,
            layout=randomizer_layout,
            description="Randomize treatments",
        ),
        PluginPage(
            id=SAMPLE_SIZE_ID,
            label="Sample Size",
            icon=SAMPLE_SIZE_ICON,
            section=SECTION_NAME,
            order=3,
            layout=samplesize_layout,
            description="Calculate sample size",
        ),
        PluginPage(
            id=SAMPLE_SIZE_COMPARE_ID,
            label="Sample Size Compare",
            icon=SAMPLE_SIZE_COMPARE_ICON,
            section=SECTION_NAME,
            order=4,
            layout=samplesizecomp_layout,
            description="Compare sample sizes",
        ),
        PluginPage(
            id=SAMPLING_ID,
            label="Sampling",
            icon=SAMPLING_ICON,
            section=SECTION_NAME,
            order=5,
            layout=sampling_layout,
            description="Sampling methods",
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
