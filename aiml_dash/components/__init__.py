"""
Components Package
==================

Reusable UI components for the AIML Dash application.
"""

from .common import (
    create_code_display,
    create_download_button,
    create_filter_section,
    create_function_selector,
    create_info_card,
    create_page_header,
    create_tabs,
    create_variable_selector,
)
from .shell import (
    create_aside,
    create_footer,
    create_header,
    create_navigation,
)

__all__ = [
    "create_aside",
    "create_code_display",
    "create_download_button",
    "create_filter_section",
    "create_footer",
    "create_function_selector",
    # Shell components
    "create_header",
    "create_info_card",
    "create_navigation",
    # Common components
    "create_page_header",
    "create_tabs",
    "create_variable_selector",
]
