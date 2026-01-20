"""Shared plugin dataclasses for AIML Dash."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from dash.development.base_component import Component

HOME_PAGE_ID = "home"


@dataclass(frozen=True)
class PluginPage:
    """Definition for a plugin-provided page."""

    id: str
    label: str
    icon: str
    layout: Callable[[], Component]
    section: str
    group: str | None = None
    order: int = 0
    group_order: int = 0
    description: str | None = None


@dataclass(frozen=True)
class Plugin:
    """Metadata describing a plugin and its pages."""

    id: str
    name: str
    description: str
    pages: Sequence[PluginPage]
    version: str = "1.0"
    default_enabled: bool = True
    locked: bool = False
    register_callbacks: Callable[[object], None] | None = None
