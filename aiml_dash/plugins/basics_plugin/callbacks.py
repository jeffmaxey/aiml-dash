"""Callback aggregator for the basics plugin.

All callbacks for the basics plugin are split into per-analysis sub-modules
that register themselves automatically via ``@callback`` decorators.
This module imports each sub-module to trigger their registration and exposes
the ``register_callbacks`` entry-point required by the plugin framework.

Sub-modules:

* :mod:`callbacks_single_mean` — single mean hypothesis test
* :mod:`callbacks_compare_means` — compare means
* :mod:`callbacks_single_prop` — single proportion test
* :mod:`callbacks_compare_props` — compare proportions
* :mod:`callbacks_correlation` — correlation analysis
* :mod:`callbacks_cross_tabs` — cross-tabulation (chi-square)
* :mod:`callbacks_goodness` — goodness-of-fit and probability calculator
* :mod:`callbacks_clt` — central limit theorem simulation
"""

# Importing each sub-module triggers their @callback decorator registrations.
from aiml_dash.plugins.basics_plugin import (  # noqa: F401
    callbacks_clt,
    callbacks_compare_means,
    callbacks_compare_props,
    callbacks_correlation,
    callbacks_cross_tabs,
    callbacks_goodness,
    callbacks_single_mean,
    callbacks_single_prop,
)


def register_callbacks(app: object) -> None:
    """Register all callbacks for the basics plugin.

    All callbacks are registered automatically via ``@callback`` decorators
    when each sub-module is imported above.  The ``app`` argument is accepted
    for API compatibility with other plugins that do require it.

    Parameters
    ----------
    app : object
        Value provided for this parameter."""
