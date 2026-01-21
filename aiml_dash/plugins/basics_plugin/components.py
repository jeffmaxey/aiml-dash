"""Reusable components for the basics plugin.

This module provides reusable UI components for the basics plugin pages.
Currently, all components are defined inline within the layout functions for simplicity
and better code locality. This module can be extended in the future if common patterns emerge.

Component Organization:
- Page-specific components are defined within their respective layout functions
- Common components (like page headers) are imported from components.common
- Alert and notification components are created inline using dmc components

Future Extensions:
- Extract common alert/notification builders if patterns emerge
- Create reusable data display components (tables, cards, etc.)
- Add shared form input validators or formatters
"""

# This module intentionally left minimal as components are best kept local to layouts
# for maintainability and clarity. Common cross-plugin components are in components.common

