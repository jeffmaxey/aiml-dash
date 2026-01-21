"""Design plugin for AIML Dash."""

from aiml_dash.plugins.design_plugin import callbacks
from aiml_dash.plugins.design_plugin.layout import *
from aiml_dash.plugins.models import Plugin, PluginPage


def get_plugin() -> Plugin:
    """Return the design plugin definition."""
    
    pages = [
        PluginPage(
            id="doe", label="Design of Experiments", icon="carbon:chemistry",
            section="Design", order=1, layout=doe_layout,
            description="Design experiments"
        ),
        PluginPage(
            id="randomizer", label="Randomizer", icon="carbon:shuffle",
            section="Design", order=2, layout=randomizer_layout,
            description="Randomize treatments"
        ),
        PluginPage(
            id="sample-size", label="Sample Size", icon="carbon:data-share",
            section="Design", order=3, layout=samplesize_layout,
            description="Calculate sample size"
        ),
        PluginPage(
            id="sample-size-comp", label="Sample Size Compare", icon="carbon:compare",
            section="Design", order=4, layout=samplesizecomp_layout,
            description="Compare sample sizes"
        ),
        PluginPage(
            id="sampling", label="Sampling", icon="carbon:data-1",
            section="Design", order=5, layout=sampling_layout,
            description="Sampling methods"
        ),
    ]
    
    return Plugin(
        id="design",
        name="Design",
        description="Design of experiments and sampling tools",
        pages=pages,
        version="1.0.0",
        default_enabled=True,
        locked=False,
        register_callbacks=callbacks.register_callbacks,
    )
