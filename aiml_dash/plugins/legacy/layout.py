"""Layout mapping for legacy pages."""

from collections.abc import Callable
from typing import Any

# Legacy pages have been fully migrated into plugin-owned modules.
PAGE_LAYOUTS: dict[str, Callable[[], Any]] = {}
