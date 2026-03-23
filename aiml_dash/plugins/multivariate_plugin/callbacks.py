"""Callback registration for the multivariate plugin.

Multivariate page callbacks are declared with Dash's ``@callback`` decorator
in the canonical application page modules under
``aiml_dash.pages.multivariate``.
"""

from importlib import import_module
from pkgutil import iter_modules

PAGES_PACKAGE = "aiml_dash.pages.multivariate"


def _import_page_modules() -> None:
    """Import all modules under the multivariate plugin pages package."""
    package = import_module(PAGES_PACKAGE)
    if not hasattr(package, "__path__"):
        return

    module_infos = sorted(
        iter_modules(package.__path__, prefix=f"{PAGES_PACKAGE}."),
        key=lambda module_info: module_info.name,
    )
    for module_info in module_infos:
        import_module(module_info.name)


def register_callbacks(_app: object) -> None:
    """Register callbacks for the multivariate plugin.

    Parameters
    ----------
    _app : object
        Dash app instance kept for interface compatibility.
    """
    _import_page_modules()
