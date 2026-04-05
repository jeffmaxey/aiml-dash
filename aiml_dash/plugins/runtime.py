"""Plugin runtime for AIML Dash.

This module provides the ``PluginRuntime`` class which manages the full
lifecycle of plugins: static registration, optional dynamic discovery,
dependency/version validation, RBAC filtering, and callback registration.

Classes:
    PluginRuntime: Central runtime managing plugin state and operations.
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any

from aiml_dash.plugins.dependency_manager import resolve_dependencies, validate_plugin
from aiml_dash.plugins.loader import load_plugins_dynamically
from aiml_dash.plugins.models import Plugin, PluginPage

if TYPE_CHECKING:
    from aiml_dash.auth import AuthorizationService, UserContext
    from aiml_dash.utils.config import AppSettings

logger = logging.getLogger(__name__)

# Ordered list of built-in plugin module paths
_STATIC_PLUGIN_MODULES: list[str] = [
    "aiml_dash.plugins.core",
    "aiml_dash.plugins.data_plugin",
    "aiml_dash.plugins.basics_plugin",
    "aiml_dash.plugins.design_plugin",
    "aiml_dash.plugins.model_plugin",
    "aiml_dash.plugins.multivariate_plugin",
    "aiml_dash.plugins.example_plugin",
    "aiml_dash.plugins.template_plugin",
]


def _load_static_plugins() -> list[Plugin]:
    """Import each static plugin module and call its ``get_plugin()``."""
    plugins: list[Plugin] = []
    for module_path in _STATIC_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, "get_plugin"):
                logger.warning("Plugin module '%s' has no get_plugin()", module_path)
                continue
            plugin = module.get_plugin()
            if isinstance(plugin, Plugin):
                plugins.append(plugin)
            else:
                logger.warning("get_plugin() in '%s' did not return a Plugin", module_path)
        except Exception:
            logger.exception("Failed to load static plugin '%s'", module_path)
    return plugins


class PluginRuntime:
    """Runtime that owns plugin state and exposes management operations.

    Parameters
    ----------
    settings : AppSettings
        Application settings providing configuration values.
    authorization : AuthorizationService
        Service used for role-based access filtering.
    """

    def __init__(
        self,
        settings: AppSettings,
        authorization: AuthorizationService,
    ) -> None:
        self._settings = settings
        self._authorization = authorization
        self._static_plugins: list[Plugin] | None = None

    @property
    def settings(self) -> AppSettings:
        """Return the application settings."""
        return self._settings

    # ------------------------------------------------------------------
    # Plugin loading
    # ------------------------------------------------------------------

    def _ensure_static_plugins(self) -> list[Plugin]:
        """Load static plugins lazily (once per runtime instance)."""
        if self._static_plugins is None:
            self._static_plugins = _load_static_plugins()
        return self._static_plugins

    def get_static_plugins(self) -> Sequence[Plugin]:
        """Return the list of statically registered plugins.

        Returns
        -------
        Sequence[Plugin]
            All built-in plugins in their declared order.
        """
        return list(self._ensure_static_plugins())

    def get_plugins(self, *, enable_dynamic_loading: bool = False) -> Sequence[Plugin]:
        """Return all available plugins, with optional dynamic discovery.

        When *enable_dynamic_loading* is ``True`` the plugins directory is
        scanned for additional plugin packages beyond the built-in set.

        Parameters
        ----------
        enable_dynamic_loading : bool
            Enable runtime discovery of non-built-in plugins.

        Returns
        -------
        Sequence[Plugin]
            Combined list of static and (optionally) dynamically discovered
            plugins, deduplicated by plugin id.
        """
        plugins = list(self._ensure_static_plugins())

        if enable_dynamic_loading and self._settings.enable_dynamic_plugins:
            from pathlib import Path

            plugins_path = Path(__file__).resolve().parent
            dynamic = load_plugins_dynamically(plugins_path)
            known_ids = {p.id for p in plugins}
            for plugin in dynamic:
                if plugin.id not in known_ids:
                    plugins.append(plugin)
                    known_ids.add(plugin.id)

        # Validate and filter plugins with unmet dependencies / incompatible
        # versions, but never remove locked plugins.
        app_version = self._settings.app_version
        supported_api = self._settings.plugin_api_version
        plugin_map = {p.id: p for p in plugins}

        validated: list[Plugin] = []
        for plugin in plugins:
            ok, errors = validate_plugin(
                plugin,
                plugin_map,
                app_version=app_version,
                supported_api_version=supported_api,
            )
            if ok or plugin.locked:
                validated.append(plugin)
            else:
                logger.warning(
                    "Plugin '%s' failed validation and will be skipped: %s",
                    plugin.id,
                    "; ".join(errors),
                )

        resolved, dep_errors = resolve_dependencies(validated)
        for err in dep_errors:
            logger.warning("Dependency resolution: %s", err)

        # Keep locked plugins even if dependency resolution struggled
        resolved_ids = {p.id for p in resolved}
        for plugin in validated:
            if plugin.locked and plugin.id not in resolved_ids:
                resolved.append(plugin)

        return resolved

    def get_plugin_registry(self, *, enable_dynamic_loading: bool = False) -> dict[str, Plugin]:
        """Return plugins keyed by their identifier.

        Parameters
        ----------
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_plugins`.

        Returns
        -------
        dict[str, Plugin]
            Mapping of plugin id → ``Plugin`` instance.
        """
        return {p.id: p for p in self.get_plugins(enable_dynamic_loading=enable_dynamic_loading)}

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_plugin_metadata(
        self,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[dict[str, Any]]:
        """Return serialisable plugin metadata for UI rendering.

        Parameters
        ----------
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_plugins`.
        user : UserContext | None
            When supplied, plugins inaccessible to this user are omitted.

        Returns
        -------
        list[dict[str, Any]]
            One metadata dict per accessible plugin.
        """
        plugins = self.get_plugins(enable_dynamic_loading=enable_dynamic_loading)
        result: list[dict[str, Any]] = []
        for plugin in plugins:
            if user is not None and not self._authorization.can_access(
                user, plugin.allowed_roles
            ):
                continue
            result.append(
                {
                    "id": plugin.id,
                    "name": plugin.name,
                    "description": plugin.description,
                    "version": plugin.version,
                    "default_enabled": plugin.default_enabled,
                    "locked": plugin.locked,
                    "dependencies": list(plugin.dependencies),
                    "capabilities": list(plugin.capabilities),
                }
            )
        return result

    # ------------------------------------------------------------------
    # Enable / disable helpers
    # ------------------------------------------------------------------

    def get_default_enabled_plugins(
        self,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[str]:
        """Return the ids of plugins that are enabled by default.

        Parameters
        ----------
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_plugins`.
        user : UserContext | None
            When supplied, only plugins accessible to this user are returned.

        Returns
        -------
        list[str]
            Plugin ids that have ``default_enabled=True`` and pass RBAC.
        """
        plugins = self.get_plugins(enable_dynamic_loading=enable_dynamic_loading)
        result: list[str] = []
        for plugin in plugins:
            if not plugin.default_enabled:
                continue
            if user is not None and not self._authorization.can_access(
                user, plugin.allowed_roles
            ):
                continue
            result.append(plugin.id)
        return result

    def normalize_enabled_plugins(
        self,
        enabled_plugins: Iterable[str] | None,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[str]:
        """Ensure locked plugins are always present in *enabled_plugins*.

        Parameters
        ----------
        enabled_plugins : Iterable[str] | None
            Current enabled-plugins list (may be ``None``).
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_plugins`.
        user : UserContext | None
            When supplied, inaccessible plugins are removed.

        Returns
        -------
        list[str]
            Normalised list that always contains all locked plugin ids.
        """
        plugins = self.get_plugins(enable_dynamic_loading=enable_dynamic_loading)
        plugin_map = {p.id: p for p in plugins}

        if enabled_plugins is None:
            current: set[str] = set()
        else:
            current = set(enabled_plugins)

        # Always include locked plugins
        for plugin in plugins:
            if plugin.locked:
                current.add(plugin.id)

        # Remove unknown or inaccessible plugin ids
        normalised: list[str] = []
        for plugin_id in current:
            plugin = plugin_map.get(plugin_id)
            if plugin is None:
                continue
            if user is not None and not self._authorization.can_access(
                user, plugin.allowed_roles
            ):
                continue
            normalised.append(plugin_id)

        return normalised

    # ------------------------------------------------------------------
    # Page helpers
    # ------------------------------------------------------------------

    def get_pages(
        self,
        enabled_plugins: Iterable[str] | None = None,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> list[PluginPage]:
        """Return pages for the enabled plugins.

        Parameters
        ----------
        enabled_plugins : Iterable[str] | None
            Restrict pages to these plugin ids.  ``None`` returns all pages
            from all default-enabled plugins.
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_plugins`.
        user : UserContext | None
            When supplied, pages inaccessible to this user are omitted.

        Returns
        -------
        list[PluginPage]
            Flat list of accessible pages in plugin order.
        """
        plugin_registry = self.get_plugin_registry(enable_dynamic_loading=enable_dynamic_loading)

        if enabled_plugins is None:
            active_ids = {
                pid for pid, p in plugin_registry.items() if p.default_enabled
            }
        else:
            active_ids = set(enabled_plugins)

        pages: list[PluginPage] = []
        for plugin_id, plugin in plugin_registry.items():
            if plugin_id not in active_ids:
                continue
            if user is not None and not self._authorization.can_access(
                user, plugin.allowed_roles
            ):
                continue
            for page in plugin.pages:
                if user is not None and not self._authorization.can_access(
                    user, page.allowed_roles
                ):
                    continue
                pages.append(page)
        return pages

    def get_page_registry(
        self,
        enabled_plugins: Iterable[str] | None = None,
        *,
        enable_dynamic_loading: bool = False,
        user: UserContext | None = None,
    ) -> dict[str, PluginPage]:
        """Return a mapping of page id → ``PluginPage`` for enabled plugins.

        Parameters
        ----------
        enabled_plugins : Iterable[str] | None
            Forwarded to :meth:`get_pages`.
        enable_dynamic_loading : bool
            Forwarded to :meth:`get_pages`.
        user : UserContext | None
            Forwarded to :meth:`get_pages`.

        Returns
        -------
        dict[str, PluginPage]
            Page registry keyed by page id.
        """
        return {
            p.id: p
            for p in self.get_pages(
                enabled_plugins,
                enable_dynamic_loading=enable_dynamic_loading,
                user=user,
            )
        }

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def register_plugin_callbacks(self, app: object) -> None:
        """Invoke each static plugin's ``register_callbacks`` function.

        Parameters
        ----------
        app : object
            The Dash application instance passed to each plugin's callback
            registration function.
        """
        for plugin in self._ensure_static_plugins():
            if plugin.register_callbacks is not None:
                try:
                    plugin.register_callbacks(app)
                except Exception:
                    logger.exception(
                        "Failed to register callbacks for plugin '%s'", plugin.id
                    )
