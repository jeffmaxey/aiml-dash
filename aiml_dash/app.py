"""Application factory for AIML Dash."""

from __future__ import annotations

import base64
import json
from datetime import datetime

import dash
import dash_mantine_components as dmc
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html
from dash_iconify import DashIconify
from flask import g, request

from aiml_dash.auth import UserContext
from aiml_dash.components.shell import (
    create_aside,
    create_footer,
    create_header,
    create_navigation,
)
from aiml_dash.plugins.models import HOME_PAGE_ID
from aiml_dash.plugins.registry import build_navigation_sections
from aiml_dash.services import AppServices, build_services
from aiml_dash.utils.config import AppSettings, get_settings
from aiml_dash.utils.logging import (
    clear_request_id,
    get_logger,
    set_request_id,
    setup_logging,
)

logger = get_logger(__name__)


def _build_project_snapshot(
    *,
    app_state: dict | None,
    active_page: str | None,
    enabled_plugins: list[str] | None,
    navbar_collapsed: bool | None,
    aside_collapsed: bool | None,
    active_dataset: str | None,
    data_state: dict,
) -> dict:
    """Build a project snapshot from current UI and data state."""
    return {
        "version": "1.0",
        "ui_state": {
            "app_state": app_state or {},
            "active_page": active_page or HOME_PAGE_ID,
            "enabled_plugins": enabled_plugins or [],
            "navbar_collapsed": bool(navbar_collapsed),
            "aside_collapsed": bool(aside_collapsed),
            "active_dataset": active_dataset,
        },
        "data_state": data_state,
    }


def _project_alert(message: str, *, color: str, title: str) -> dmc.Alert:
    """Build a project status alert."""
    icon = "carbon:checkmark" if color == "green" else "carbon:warning"
    return dmc.Alert(
        message,
        color=color,
        title=title,
        icon=DashIconify(icon=icon),
    )


def _project_metadata_lookup(metadata: list[dict] | None, project_id: str | None) -> dict:
    """Return project metadata dict or empty dict."""
    if not metadata or not project_id:
        return {}
    return next((item for item in metadata if item.get("id") == project_id), {})


def _build_layout(services: AppServices) -> dmc.MantineProvider:
    """Build the app layout."""
    plugin_metadata = services.plugins.get_plugin_metadata()
    default_enabled_plugins = services.plugins.get_default_enabled_plugins()
    projects = services.projects.metadata()
    active_project = services.projects.get_active_project()

    return dmc.MantineProvider(
        id="mantine-provider",
        forceColorScheme="light",
        theme={
            "fontFamily": "'IBM Plex Sans', 'Segoe UI', sans-serif",
            "fontFamilyMonospace": "'IBM Plex Mono', 'Cascadia Code', monospace",
            "primaryColor": "cyan",
            "defaultRadius": "md",
            "cursorType": "pointer",
            "headings": {
                "fontFamily": "'Space Grotesk', 'IBM Plex Sans', sans-serif",
                "fontWeight": "700",
            },
            "colors": {
                "cyan": [
                    "#ecfeff",
                    "#cffafe",
                    "#a5f3fc",
                    "#67e8f9",
                    "#22d3ee",
                    "#06b6d4",
                    "#0891b2",
                    "#0e7490",
                    "#155e75",
                    "#164e63",
                ]
            },
            "shadows": {
                "xs": "0 1px 2px rgba(15, 23, 42, 0.05)",
                "sm": "0 8px 24px rgba(15, 23, 42, 0.08)",
                "md": "0 18px 40px rgba(15, 23, 42, 0.12)",
                "xl": "0 28px 60px rgba(15, 23, 42, 0.18)",
            },
            "components": {
                "AppShell": {
                    "styles": {
                        "main": {
                            "background": "transparent",
                        }
                    }
                },
                "Button": {
                    "defaultProps": {
                        "fw": 600,
                        "radius": "xl",
                    }
                },
                "Alert": {"styles": {"title": {"fontWeight": 500}}},
                "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
                "Card": {
                    "defaultProps": {
                        "radius": "xl",
                        "shadow": "sm",
                        "withBorder": True,
                    }
                },
                "TextInput": {"defaultProps": {"radius": "md"}},
                "Textarea": {"defaultProps": {"radius": "md"}},
                "Select": {"defaultProps": {"radius": "md"}},
                "MultiSelect": {"defaultProps": {"radius": "md"}},
                "Modal": {"defaultProps": {"radius": "xl", "centered": True}},
            },
        },
        children=dmc.DirectionProvider(
            id="direction-provider",
            direction="ltr",
            children=dmc.Box(
                [
                    dmc.AppShell(
                        [
                            dmc.AppShellHeader(
                                create_header(),
                                px="lg",
                                id="app-header",
                                className="aiml-shell-header",
                            ),
                            dmc.AppShellNavbar(
                                dmc.ScrollArea(
                                    offsetScrollbars=True,
                                    type="scroll",
                                    children=dmc.Loader(color="blue", size="sm"),
                                    p="md",
                                    id="app-navigation",
                                    className="aiml-shell-scroll",
                                ),
                                id="app-navbar",
                                className="aiml-shell-navbar",
                            ),
                            dmc.AppShellAside(
                                create_aside(),
                                p="md",
                                id="app-aside",
                                className="aiml-shell-aside",
                            ),
                            dmc.AppShellMain(
                                html.Div(id="page-content", className="aiml-page-container"),
                                id="app-main",
                                className="aiml-shell-main",
                            ),
                            dmc.AppShellFooter(
                                create_footer(),
                                px="lg",
                                py="sm",
                                id="app-footer",
                                className="aiml-shell-footer",
                            ),
                        ],
                        header={"height": 60},
                        navbar={
                            "width": 250,
                            "breakpoint": "sm",
                            "collapsed": {"mobile": False, "desktop": False},
                        },
                        aside={
                            "width": 320,
                            "breakpoint": "md",
                            "collapsed": {"mobile": False, "desktop": False},
                        },
                        footer={"height": 50},
                        padding="md",
                        id="app-shell",
                        className="aiml-shell",
                    ),
                    dcc.Location(id="url", refresh="callback-nav"),
                    dmc.NotificationContainer(id="notification-container"),
                    dcc.Store(id="color-scheme-storage", storage_type="local", data="light"),
                    dcc.Store(id="text-direction-storage", storage_type="local", data="ltr"),
                    dcc.Store(id="plugin-metadata", data=plugin_metadata),
                    dcc.Store(
                        id="enabled-plugins",
                        storage_type="local",
                        data=default_enabled_plugins,
                    ),
                    dcc.Store(id="app-state", storage_type="session"),
                    dcc.Store(id="active-page", data=HOME_PAGE_ID),
                    dcc.Store(id="navbar-collapsed", data=False),
                    dcc.Store(id="aside-collapsed", data=False),
                    dcc.Store(id="project-metadata", data=projects),
                    dcc.Store(
                        id="active-project-id",
                        data=active_project.id if active_project else None,
                    ),
                    dcc.Store(
                        id="user-context",
                        data={"user_id": "anonymous", "roles": list(services.settings.default_user_roles)},
                    ),
                    dcc.Download(id="download-state"),
                    dcc.Upload(
                        id="upload-state",
                        children=html.Div(id="upload-state-trigger"),
                        style={"display": "none"},
                    ),
                    dmc.Modal(
                        id="import-modal",
                        title="Import Application State",
                        children=[
                            dmc.Stack(
                                [
                                    dmc.Text("Click or drag and drop a state file to import:"),
                                    dcc.Upload(
                                        id="upload-state-file",
                                        children=dmc.Card(
                                            [
                                                dmc.Center(
                                                    [
                                                        dmc.Stack(
                                                            [
                                                                DashIconify(
                                                                    icon="carbon:upload",
                                                                    width=48,
                                                                    height=48,
                                                                    color="gray",
                                                                ),
                                                                dmc.Text("Click or Drag & Drop", fw=500),
                                                                dmc.Text(
                                                                    "Upload .json state file",
                                                                    size="sm",
                                                                    c="dimmed",
                                                                ),
                                                            ],
                                                            align="center",
                                                            gap="xs",
                                                        )
                                                    ],
                                                    style={"height": 150},
                                                )
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            style={"cursor": "pointer"},
                                        ),
                                        multiple=False,
                                    ),
                                    html.Div(id="import-status"),
                                ],
                                gap="md",
                            )
                        ],
                        size="lg",
                    ),
                    dmc.Modal(
                        id="project-modal",
                        title="Project",
                        opened=False,
                        children=[
                            dmc.Stack(
                                [
                                    dmc.TextInput(
                                        id="project-name-input",
                                        label="Project name",
                                        required=True,
                                    ),
                                    dmc.Textarea(
                                        id="project-description-input",
                                        label="Description",
                                        minRows=3,
                                    ),
                                    dcc.Store(id="project-modal-mode"),
                                    dmc.Group(
                                        [
                                            dmc.Button(
                                                "Cancel",
                                                id="project-modal-cancel",
                                                variant="default",
                                            ),
                                            dmc.Button(
                                                "Save",
                                                id="project-modal-save",
                                            ),
                                        ],
                                        justify="flex-end",
                                    ),
                                ],
                                gap="sm",
                            )
                        ],
                    ),
                ],
                className="aiml-app",
                id="app-root",
            ),
        ),
    )


def _register_observability(app: Dash, settings: AppSettings) -> None:
    """Register request logging and exception handling."""
    server = app.server

    @server.before_request
    def _before_request() -> None:
        request_id = request.headers.get("X-Request-ID")
        g.request_id = set_request_id(request_id)
        logger.info("Request started %s %s", request.method, request.path)

    @server.after_request
    def _after_request(response):  # type: ignore[no-untyped-def]
        logger.info(
            "Request completed %s %s status=%s",
            request.method,
            request.path,
            response.status_code,
        )
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
        clear_request_id()
        return response

    @server.errorhandler(Exception)
    def _handle_exception(error):  # type: ignore[no-untyped-def]
        logger.exception("Unhandled server error: %s", error)
        return {"error": "Internal server error"}, 500

    if settings.enable_talisman:
        try:
            from flask_talisman import Talisman

            Talisman(server, content_security_policy=None)
        except Exception:
            logger.exception("Failed to enable Flask-Talisman")

    if settings.enable_compression:
        try:
            from flask_compress import Compress

            Compress(server)
        except Exception:
            logger.exception("Failed to enable Flask-Compress")


def _user_from_store(user_data: dict | None, services: AppServices) -> UserContext:
    """Build a user context from stored UI state."""
    if not user_data:
        return services.auth.default_user()
    roles = tuple(user_data.get("roles") or services.settings.default_user_roles)
    return UserContext(user_id=user_data.get("user_id", "anonymous"), roles=roles)


def _register_callbacks(app: Dash, services: AppServices) -> None:
    """Register all core application callbacks."""
    data_manager = services.data_manager
    project_manager = services.projects
    plugin_runtime = services.plugins

    @app.callback(
        Output("navbar-collapsed", "data"),
        Input("navbar-toggle", "n_clicks"),
        State("navbar-collapsed", "data"),
        prevent_initial_call=True,
    )
    def toggle_navbar(n_clicks, collapsed):
        return not collapsed if n_clicks else collapsed

    @app.callback(
        Output("aside-collapsed", "data"),
        Input("aside-toggle", "n_clicks"),
        State("aside-collapsed", "data"),
        prevent_initial_call=True,
    )
    def toggle_aside(n_clicks, collapsed):
        return not collapsed if n_clicks else collapsed

    @app.callback(
        Output("color-scheme-storage", "data"),
        Input("docs-color-scheme-switch", "checked"),
        prevent_initial_call=False,
    )
    def persist_color_scheme(checked):
        return "dark" if checked else "light"

    @app.callback(
        Output("docs-color-scheme-switch", "checked"),
        Output("mantine-provider", "forceColorScheme"),
        Input("color-scheme-storage", "data"),
    )
    def apply_color_scheme(color_scheme):
        scheme = color_scheme if color_scheme in {"light", "dark"} else "light"
        return scheme == "dark", scheme

    @app.callback(
        Output("text-direction-storage", "data"),
        Input("rtl-toggle", "n_clicks"),
        State("text-direction-storage", "data"),
        prevent_initial_call=True,
    )
    def toggle_text_direction(n_clicks, direction):
        if not n_clicks:
            return dash.no_update
        return "rtl" if direction != "rtl" else "ltr"

    @app.callback(
        Output("direction-provider", "direction"),
        Output("rtl-icon", "icon"),
        Output("rtl-toggle", "color"),
        Output("app-root", "dir"),
        Input("text-direction-storage", "data"),
    )
    def apply_text_direction(direction):
        resolved_direction = direction if direction in {"ltr", "rtl"} else "ltr"
        icon = (
            "tabler:text-direction-ltr"
            if resolved_direction == "rtl"
            else "tabler:text-direction-rtl"
        )
        color = "cyan" if resolved_direction == "rtl" else "gray"
        return resolved_direction, icon, color, resolved_direction

    @app.callback(Output("app-shell", "navbar"), Input("navbar-collapsed", "data"))
    def update_navbar_state(collapsed):
        return {
            "width": 250,
            "breakpoint": "sm",
            "collapsed": {"mobile": collapsed, "desktop": collapsed},
        }

    @app.callback(Output("app-shell", "aside"), Input("aside-collapsed", "data"))
    def update_aside_state(collapsed):
        return {
            "width": 300,
            "breakpoint": "md",
            "collapsed": {"mobile": collapsed, "desktop": collapsed},
        }

    @app.callback(
        Output("page-content", "children"),
        Input("active-page", "data"),
        Input("enabled-plugins", "data"),
        State("user-context", "data"),
    )
    def load_page_content(page, enabled_plugins, user_data):
        user = _user_from_store(user_data, services)
        page_registry = plugin_runtime.get_page_registry(enabled_plugins, user=user)
        if page in page_registry:
            return page_registry[page].layout()

        fallback = page_registry.get(HOME_PAGE_ID) if page_registry else None
        fallback = fallback or next(iter(page_registry.values()), None)
        if fallback:
            return fallback.layout()
        return dmc.Center(
            dmc.Text("Page not found or not authorized", size="xl", c="dimmed"),
            style={"height": "50vh"},
        )

    @app.callback(
        Output("app-navigation", "children"),
        Output("plugin-metadata", "data"),
        Input("enabled-plugins", "data"),
        State("user-context", "data"),
    )
    def update_navigation(enabled_plugins, user_data):
        user = _user_from_store(user_data, services)
        pages = plugin_runtime.get_pages(enabled_plugins, user=user)
        return (
            create_navigation(build_navigation_sections(pages)),
            plugin_runtime.get_plugin_metadata(user=user),
        )

    @app.callback(
        Output("enabled-plugins", "data", allow_duplicate=True),
        Input("user-context", "data"),
        State("enabled-plugins", "data"),
        prevent_initial_call=True,
    )
    def reauthorize_plugins(user_data, enabled_plugins):
        user = _user_from_store(user_data, services)
        return plugin_runtime.normalize_enabled_plugins(enabled_plugins, user=user)

    @app.callback(
        Output("active-page", "data", allow_duplicate=True),
        Input("enabled-plugins", "data"),
        State("active-page", "data"),
        State("user-context", "data"),
        prevent_initial_call=True,
    )
    def ensure_active_page(enabled_plugins, active_page, user_data):
        user = _user_from_store(user_data, services)
        page_registry = plugin_runtime.get_page_registry(enabled_plugins, user=user)
        if not page_registry or active_page in page_registry:
            return dash.no_update
        return HOME_PAGE_ID if HOME_PAGE_ID in page_registry else next(iter(page_registry), HOME_PAGE_ID)

    @app.callback(
        Output("active-page", "data"),
        Input({"type": "nav-link", "index": ALL}, "n_clicks"),
        State({"type": "nav-link", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def update_active_page(n_clicks, ids):
        if not ctx.triggered or not any(n_clicks):
            return dash.no_update
        button_id = ctx.triggered_id
        if button_id and "index" in button_id:
            return button_id["index"]
        return dash.no_update

    @app.callback(
        Output("url", "hash"),
        Input("active-page", "data"),
        State("url", "hash"),
    )
    def sync_url_hash(active_page, current_hash):
        target_hash = f"#{active_page}" if active_page else ""
        if current_hash == target_hash:
            return dash.no_update
        return target_hash

    @app.callback(
        Output("active-page", "data", allow_duplicate=True),
        Input("url", "hash"),
        State("active-page", "data"),
        State("enabled-plugins", "data"),
        State("user-context", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def sync_active_page_from_hash(url_hash, active_page, enabled_plugins, user_data):
        if not url_hash:
            return dash.no_update

        requested_page = url_hash.lstrip("#")
        if not requested_page or requested_page == active_page:
            return dash.no_update

        user = _user_from_store(user_data, services)
        page_registry = plugin_runtime.get_page_registry(enabled_plugins, user=user)
        if requested_page in page_registry:
            return requested_page
        return dash.no_update

    @app.callback(
        Output("dataset-selector", "data"),
        Output("dataset-selector", "value"),
        Input("app-state", "modified_timestamp"),
        State("dataset-selector", "value"),
    )
    def update_dataset_selector(ts, current_value):
        datasets = data_manager.get_dataset_names()
        options = [{"label": name, "value": name} for name in datasets]
        active = data_manager.get_active_dataset_name()
        value = current_value if current_value in datasets else active
        return options, value

    @app.callback(
        Output("dataset-rows-badge", "children"),
        Output("dataset-cols-badge", "children"),
        Output("active-dataset-display", "children"),
        Output("dataset-memory", "children"),
        Input("dataset-selector", "value"),
    )
    def update_dataset_info(dataset_name):
        if not dataset_name:
            return "0 rows", "0 cols", "No dataset selected", ""

        data_manager.set_active_dataset(dataset_name)
        info = data_manager.get_dataset_info(dataset_name)
        return (
            f"{info.get('rows', 0):,} rows",
            f"{info.get('columns', 0)} cols",
            f"Dataset: {dataset_name}",
            f"Memory: {info.get('memory_usage', 0):.2f} MB",
        )

    @app.callback(
        Output("project-selector", "data"),
        Output("project-selector", "value"),
        Output("project-description", "children"),
        Output("project-protected-badge", "children"),
        Output("project-protected-badge", "color"),
        Output("project-protect-button", "children"),
        Output("project-edit-button", "disabled"),
        Output("project-copy-button", "disabled"),
        Output("project-delete-button", "disabled"),
        Output("project-protect-button", "disabled"),
        Output("project-save-button", "disabled"),
        Input("project-metadata", "data"),
        Input("active-project-id", "data"),
    )
    def update_project_panel(project_metadata, active_project_id):
        metadata = project_metadata or []
        project = _project_metadata_lookup(metadata, active_project_id)
        protected = bool(project.get("protected"))
        has_project = bool(project)
        return (
            project_manager.project_options(),
            active_project_id,
            project.get("description", "No project selected") if has_project else "No project selected",
            "Protected" if protected else "Unprotected",
            "yellow" if protected else "gray",
            "Unprotect" if protected else "Protect",
            not has_project or protected,
            not has_project,
            not has_project or protected,
            not has_project,
            not has_project or protected,
        )

    @app.callback(
        Output("project-modal", "opened"),
        Output("project-modal", "title"),
        Output("project-modal-mode", "data"),
        Output("project-name-input", "value"),
        Output("project-description-input", "value"),
        Input("project-create-button", "n_clicks"),
        Input("project-edit-button", "n_clicks"),
        Input("project-copy-button", "n_clicks"),
        Input("project-modal-cancel", "n_clicks"),
        State("active-project-id", "data"),
        State("project-metadata", "data"),
        prevent_initial_call=True,
    )
    def manage_project_modal(
        create_clicks,
        edit_clicks,
        copy_clicks,
        cancel_clicks,
        active_project_id,
        project_metadata,
    ):
        triggered = ctx.triggered_id
        if triggered == "project-modal-cancel":
            return False, "Project", None, "", ""

        project = _project_metadata_lookup(project_metadata, active_project_id)
        if triggered == "project-create-button":
            return True, "Create Project", "create", "", ""
        if triggered == "project-edit-button" and project:
            return (
                True,
                "Edit Project",
                "edit",
                project.get("name", ""),
                project.get("description", ""),
            )
        if triggered == "project-copy-button" and project:
            return (
                True,
                "Copy Project",
                "copy",
                f"{project.get('name', '')} Copy",
                project.get("description", ""),
            )
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("project-metadata", "data", allow_duplicate=True),
        Output("active-project-id", "data", allow_duplicate=True),
        Output("project-modal", "opened", allow_duplicate=True),
        Output("project-status", "children"),
        Input("project-modal-save", "n_clicks"),
        State("project-modal-mode", "data"),
        State("project-name-input", "value"),
        State("project-description-input", "value"),
        State("active-project-id", "data"),
        State("app-state", "data"),
        State("active-page", "data"),
        State("enabled-plugins", "data"),
        State("navbar-collapsed", "data"),
        State("aside-collapsed", "data"),
        State("dataset-selector", "value"),
        prevent_initial_call=True,
    )
    def save_project_from_modal(
        n_clicks,
        mode,
        name,
        description,
        active_project_id,
        app_state,
        active_page,
        enabled_plugins,
        navbar_collapsed,
        aside_collapsed,
        active_dataset,
    ):
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        snapshot = _build_project_snapshot(
            app_state=app_state,
            active_page=active_page,
            enabled_plugins=enabled_plugins,
            navbar_collapsed=navbar_collapsed,
            aside_collapsed=aside_collapsed,
            active_dataset=active_dataset,
            data_state=data_manager.export_all_state(),
        )

        try:
            if mode == "create":
                project = project_manager.create_project(
                    name=name or "",
                    description=description or "",
                    state_snapshot=snapshot,
                )
                message = f"Created project '{project.name}'."
            elif mode == "edit":
                project = project_manager.update_project(
                    active_project_id,
                    name=name,
                    description=description,
                )
                message = f"Updated project '{project.name}'."
            elif mode == "copy":
                project = project_manager.copy_project(
                    active_project_id,
                    name=name or "",
                    description=description or "",
                )
                message = f"Copied project to '{project.name}'."
            else:
                raise ValueError("Unknown project action")
            return (
                project_manager.metadata(),
                project.id,
                False,
                _project_alert(message, color="green", title="Projects"),
            )
        except Exception as exc:
            logger.exception("Project modal save failed")
            return (
                dash.no_update,
                dash.no_update,
                True,
                _project_alert(f"{exc!s}", color="red", title="Projects"),
            )

    @app.callback(
        Output("project-metadata", "data", allow_duplicate=True),
        Output("active-project-id", "data", allow_duplicate=True),
        Output("project-status", "children", allow_duplicate=True),
        Input("project-delete-button", "n_clicks"),
        State("active-project-id", "data"),
        prevent_initial_call=True,
    )
    def delete_project(n_clicks, active_project_id):
        if not n_clicks or not active_project_id:
            return dash.no_update, dash.no_update, dash.no_update
        try:
            project = project_manager.get_project(active_project_id)
            project_manager.delete_project(active_project_id)
            return (
                project_manager.metadata(),
                project_manager.active_project_id,
                _project_alert(
                    f"Deleted project '{project.name if project else active_project_id}'.",
                    color="green",
                    title="Projects",
                ),
            )
        except Exception as exc:
            logger.exception("Project deletion failed")
            return (
                dash.no_update,
                dash.no_update,
                _project_alert(f"{exc!s}", color="red", title="Projects"),
            )

    @app.callback(
        Output("project-metadata", "data", allow_duplicate=True),
        Output("project-status", "children", allow_duplicate=True),
        Input("project-protect-button", "n_clicks"),
        State("active-project-id", "data"),
        State("project-metadata", "data"),
        prevent_initial_call=True,
    )
    def toggle_project_protection(n_clicks, active_project_id, project_metadata):
        if not n_clicks or not active_project_id:
            return dash.no_update, dash.no_update
        project = _project_metadata_lookup(project_metadata, active_project_id)
        try:
            updated = project_manager.set_protected(
                active_project_id,
                protected=not bool(project.get("protected")),
            )
            action = "Protected" if updated.protected else "Unprotected"
            return (
                project_manager.metadata(),
                _project_alert(
                    f"{action} project '{updated.name}'.",
                    color="green",
                    title="Projects",
                ),
            )
        except Exception as exc:
            logger.exception("Project protection toggle failed")
            return (
                dash.no_update,
                _project_alert(f"{exc!s}", color="red", title="Projects"),
            )

    @app.callback(
        Output("project-metadata", "data", allow_duplicate=True),
        Output("project-status", "children", allow_duplicate=True),
        Input("project-save-button", "n_clicks"),
        State("active-project-id", "data"),
        State("app-state", "data"),
        State("active-page", "data"),
        State("enabled-plugins", "data"),
        State("navbar-collapsed", "data"),
        State("aside-collapsed", "data"),
        State("dataset-selector", "value"),
        prevent_initial_call=True,
    )
    def save_project_snapshot(
        n_clicks,
        active_project_id,
        app_state,
        active_page,
        enabled_plugins,
        navbar_collapsed,
        aside_collapsed,
        active_dataset,
    ):
        if not n_clicks or not active_project_id:
            return dash.no_update, dash.no_update
        try:
            project = project_manager.save_project_state(
                active_project_id,
                _build_project_snapshot(
                    app_state=app_state,
                    active_page=active_page,
                    enabled_plugins=enabled_plugins,
                    navbar_collapsed=navbar_collapsed,
                    aside_collapsed=aside_collapsed,
                    active_dataset=active_dataset,
                    data_state=data_manager.export_all_state(),
                ),
            )
            return (
                project_manager.metadata(),
                _project_alert(
                    f"Saved experiment state to '{project.name}'.",
                    color="green",
                    title="Projects",
                ),
            )
        except Exception as exc:
            logger.exception("Project save failed")
            return (
                dash.no_update,
                _project_alert(f"{exc!s}", color="red", title="Projects"),
            )

    @app.callback(
        Output("active-project-id", "data", allow_duplicate=True),
        Output("app-state", "data", allow_duplicate=True),
        Output("active-page", "data", allow_duplicate=True),
        Output("enabled-plugins", "data", allow_duplicate=True),
        Output("navbar-collapsed", "data", allow_duplicate=True),
        Output("aside-collapsed", "data", allow_duplicate=True),
        Output("dataset-selector", "value", allow_duplicate=True),
        Output("project-status", "children", allow_duplicate=True),
        Input("project-selector", "value"),
        prevent_initial_call=True,
    )
    def activate_project(project_id):
        if project_id is None:
            project_manager.set_active_project(None)
            return (
                None,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                _project_alert("Cleared active project.", color="green", title="Projects"),
            )

        try:
            project = project_manager.set_active_project(project_id)
            snapshot = project.state_snapshot or {}
            ui_state = snapshot.get("ui_state", {})
            data_state = snapshot.get("data_state")
            if data_state:
                success, message = data_manager.import_all_state(data_state)
                if not success:
                    raise ValueError(message)
            return (
                project.id,
                ui_state.get("app_state", {}),
                ui_state.get("active_page", HOME_PAGE_ID),
                plugin_runtime.normalize_enabled_plugins(
                    ui_state.get("enabled_plugins")
                ),
                ui_state.get("navbar_collapsed", False),
                ui_state.get("aside_collapsed", False),
                ui_state.get("active_dataset"),
                _project_alert(
                    f"Loaded project '{project.name}'.",
                    color="green",
                    title="Projects",
                ),
            )
        except Exception as exc:
            logger.exception("Project activation failed")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                _project_alert(f"{exc!s}", color="red", title="Projects"),
            )

    @app.callback(
        Output("download-state", "data"),
        Input("export-state-btn", "n_clicks"),
        State("app-state", "data"),
        State("active-page", "data"),
        State("enabled-plugins", "data"),
        State("navbar-collapsed", "data"),
        State("aside-collapsed", "data"),
        State("dataset-selector", "value"),
        prevent_initial_call=True,
    )
    def export_state(
        n_clicks,
        app_state,
        active_page,
        enabled_plugins,
        navbar_collapsed,
        aside_collapsed,
        active_dataset,
    ):
        if not n_clicks:
            return dash.no_update

        state = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "ui_state": {
                "app_state": app_state or {},
                "active_page": active_page,
                "enabled_plugins": enabled_plugins or plugin_runtime.get_default_enabled_plugins(),
                "navbar_collapsed": navbar_collapsed,
                "aside_collapsed": aside_collapsed,
                "active_dataset": active_dataset,
            },
            "data_state": data_manager.export_all_state(),
            "page_count": len(plugin_runtime.get_page_registry(enabled_plugins)),
            "feature_flags": {
                "collapsible_panels": True,
                "state_export_import": True,
                "plugin_framework": True,
                "authorization": True,
            },
        }
        return {
            "content": json.dumps(state, indent=2),
            "filename": f"aiml_complete_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        }

    @app.callback(
        Output("import-modal", "opened"),
        Input("import-state-btn", "n_clicks"),
        State("import-modal", "opened"),
        prevent_initial_call=True,
    )
    def toggle_import_modal(n_clicks, is_open):
        return (not is_open) if n_clicks else dash.no_update

    @app.callback(
        Output("app-state", "data", allow_duplicate=True),
        Output("active-page", "data", allow_duplicate=True),
        Output("enabled-plugins", "data", allow_duplicate=True),
        Output("navbar-collapsed", "data", allow_duplicate=True),
        Output("aside-collapsed", "data", allow_duplicate=True),
        Output("dataset-selector", "value", allow_duplicate=True),
        Output("import-status", "children"),
        Output("import-modal", "opened", allow_duplicate=True),
        Input("upload-state-file", "contents"),
        State("upload-state-file", "filename"),
        State("user-context", "data"),
        prevent_initial_call=True,
    )
    def import_state(contents, filename, user_data):
        if not contents:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                "",
                dash.no_update,
            )

        try:
            _content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            state = json.loads(decoded.decode("utf-8"))
            version = state.get("version", "1.0")
            user = _user_from_store(user_data, services)

            if version.startswith("2."):
                ui_state = state.get("ui_state", {})
                success, message = data_manager.import_all_state(state.get("data_state", {}))
                if not success:
                    raise ValueError(message)
                app_state = ui_state.get("app_state", {})
                active_page = ui_state.get("active_page", HOME_PAGE_ID)
                enabled_plugins = plugin_runtime.normalize_enabled_plugins(
                    ui_state.get("enabled_plugins"),
                    user=user,
                )
                navbar_collapsed = ui_state.get("navbar_collapsed", False)
                aside_collapsed = ui_state.get("aside_collapsed", False)
                active_dataset = ui_state.get("active_dataset")
            elif version.startswith("1."):
                app_state = state.get("app_state", {})
                active_page = state.get("active_page", HOME_PAGE_ID)
                enabled_plugins = plugin_runtime.normalize_enabled_plugins(
                    state.get("enabled_plugins"),
                    user=user,
                )
                navbar_collapsed = state.get("navbar_collapsed", False)
                aside_collapsed = state.get("aside_collapsed", False)
                active_dataset = state.get("active_dataset")
            else:
                raise ValueError(f"Unknown state version: {version}")

            available = data_manager.get_dataset_names()
            if active_dataset and active_dataset not in available:
                active_dataset = available[0] if available else None

            success_alert = dmc.Alert(
                [
                    dmc.Text("State imported successfully", fw=500),
                    dmc.Text(f"Source file: {filename}", size="sm"),
                    dmc.Text(f"Restored {len(available)} dataset(s)", size="sm"),
                ],
                title="Import Successful",
                color="green",
                icon=DashIconify(icon="carbon:checkmark"),
            )
            return (
                app_state,
                active_page,
                enabled_plugins,
                navbar_collapsed,
                aside_collapsed,
                active_dataset,
                success_alert,
                False,
            )
        except Exception as exc:
            logger.exception("Failed to import application state")
            error_alert = dmc.Alert(
                [
                    dmc.Text("Failed to import state", fw=500),
                    dmc.Text(f"Error: {exc!s}", size="sm"),
                ],
                title="Import Failed",
                color="red",
                icon=DashIconify(icon="carbon:warning"),
            )
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                error_alert,
                dash.no_update,
            )


def create_app(
    settings: AppSettings | None = None,
    services: AppServices | None = None,
) -> Dash:
    """Create and configure the Dash application."""
    resolved_settings = settings or get_settings()
    resolved_settings.ensure_runtime_directories()
    setup_logging(
        settings=resolved_settings,
        log_file=resolved_settings.log_dir / "app.log",
    )

    resolved_services = services or build_services(resolved_settings)

    app = Dash(
        __name__,
        title=resolved_settings.app_title,
        suppress_callback_exceptions=True,
        external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap"
        ],
    )
    app.title = resolved_settings.app_title
    app.layout = _build_layout(resolved_services)
    app.aiml_services = resolved_services  # type: ignore[attr-defined]
    app.aiml_settings = resolved_settings  # type: ignore[attr-defined]

    _register_observability(app, resolved_settings)
    resolved_services.plugins.register_plugin_callbacks(app)
    _register_callbacks(app, resolved_services)
    return app


app = create_app()
server = app.server
