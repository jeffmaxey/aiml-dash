"""
Components Package
==================

Reusable UI components for the AIML Dash application.
"""

from .common import (
    create_page_header,
    create_filter_section,
    create_variable_selector,
    create_function_selector,
    create_download_button,
    create_code_display,
    create_tabs,
    create_info_card,
)

from .shell import (
    create_header,
    create_navigation,
    create_aside,
    create_footer,
)

__all__ = [
    # Common components
    "create_page_header",
    "create_filter_section",
    "create_variable_selector",
    "create_function_selector",
    "create_download_button",
    "create_code_display",
    "create_tabs",
    "create_info_card",
    # Shell components
    "create_header",
    "create_navigation",
    "create_aside",
    "create_footer",
]
