"""Component metadata for legacy pages plugin."""

from typing import TypedDict


class LegacyPageDefinition(TypedDict, total=False):
    """Typed metadata for legacy pages."""

    id: str
    label: str
    icon: str
    section: str
    group: str
    order: int
    group_order: int
    description: str


LEGACY_PAGE_DEFINITIONS: list[LegacyPageDefinition] = []
