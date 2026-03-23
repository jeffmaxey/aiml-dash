"""
App Shell Components
====================

Reusable components for the AIML Dash AppShell structure.
"""

from typing import cast

import dash_mantine_components as dmc
from dash import html
from dash.development.base_component import Component
from dash_iconify import DashIconify

from aiml_dash.plugins.models import HOME_PAGE_ID
from aiml_dash.utils.constants import APP_TITLE, GITHUB_URL

theme_toggle = dmc.Switch(
    offLabel=DashIconify(
        icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]
    ),
    onLabel=DashIconify(
        icon="radix-icons:moon",
        width=15,
        color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
    ),
    id="docs-color-scheme-switch",
    persistence=True,
    color="gray",
    size="md",
)

rtl_toggle = dmc.Tooltip(
    dmc.ActionIcon(
        DashIconify(icon="tabler:text-direction-rtl", width=18, id="rtl-icon"),
        id="rtl-toggle",
        variant="light",
        color="gray",
        visibleFrom="sm",
    ),
    label="Text Direction",
)


def create_header():
    """Create application header for AppShellHeader."""
    return dmc.Group(
        [
            dmc.Group(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="carbon:menu", width=20),
                        id="navbar-toggle",
                        variant="subtle",
                        size="lg",
                    ),
                    DashIconify(
                        icon="carbon:analytics", width=32, height=32, color="#1971c2"
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Enterprise Analytics Workspace", size="xs", c="dimmed", tt="uppercase", fw=700, lts="0.12em"),
                            dmc.Title(children=APP_TITLE, order=3),
                        ],
                        gap=0,
                    ),
                ],
                gap="xs",
                className="aiml-brand",
            ),
            dmc.Group(
                [
                    rtl_toggle,
                    theme_toggle,
                    dmc.Text(
                        id="active-dataset-display",
                        size="sm",
                        c="dimmed",
                        className="aiml-header-status",
                    ),
                    dmc.Badge(
                        "Python Version",
                        color="cyan",
                        variant="light",
                        radius="xl",
                    ),
                    dmc.Menu(
                        [
                            dmc.MenuTarget(
                                dmc.ActionIcon(
                                    DashIconify(icon="carbon:save", width=20),
                                    variant="subtle",
                                    size="lg",
                                )
                            ),
                            dmc.MenuDropdown(
                                [
                                    dmc.MenuItem(
                                        "Export State",
                                        leftSection=DashIconify(
                                            icon="carbon:download", width=16
                                        ),
                                        id="export-state-btn",
                                    ),
                                    dmc.MenuItem(
                                        "Import State",
                                        leftSection=DashIconify(
                                            icon="carbon:upload", width=16
                                        ),
                                        id="import-state-btn",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="carbon:side-panel-close", width=20),
                        id="aside-toggle",
                        variant="subtle",
                        size="lg",
                    ),
                ],
                gap="md",
                className="aiml-header-actions",
            ),
        ],
        justify="space-between",
        style={"width": "100%"},
        className="aiml-header-group",
    )


def create_navigation(sections: list[dict[str, object]]) -> dmc.Accordion:
    """Create navigation sidebar for AppShellNavbar.

    Parameters
    ----------
    sections : list[dict[str, object]]
        Input value for ``sections``.

    Returns
    -------
    value : dmc.Accordion
        Result produced by this function."""

    def get_attr(item, key, fallback=""):
        """Read a key from a page definition.

        Parameters
        ----------
        item : Any
            Input value for ``item``.
        key : Any
            Input value for ``key``.
        fallback : Any
            Value provided for this parameter."""
        if hasattr(item, key):
            return getattr(item, key)
        if isinstance(item, dict):
            return item.get(key, fallback)
        return fallback

    def create_nav_links(items: list[object]) -> list[dmc.NavLink]:
        """Helper to create navigation links.

        Parameters
        ----------
        items : list[object]
            Input value for ``items``.

        Returns
        -------
        value : list[dmc.NavLink]
            Result produced by this function."""
        links = []
        for item in items:
            page_id = get_attr(item, "id", get_attr(item, "value"))
            links.append(
                dmc.NavLink(
                    label=get_attr(item, "label"),
                    leftSection=DashIconify(
                        icon=get_attr(item, "icon"), width=20, height=20
                    ),
                    active=False,
                    variant="subtle",
                    id={"type": "nav-link", "index": page_id},
                    n_clicks=0,
                    href=f"#{page_id}",
                    className="aiml-nav-link",
                )
            )
        return links

    accordion_items = []
    for section in sections:
        panel_children: list[Component] = []
        pages = cast(list[object], section.get("pages") or [])
        if pages:
            panel_children.extend(create_nav_links(pages))
        groups = cast(list[dict[str, object]], section.get("groups") or [])
        for index, group in enumerate(groups):
            label = group.get("label") if isinstance(group, dict) else None
            if label:
                panel_children.append(
                    dmc.Text(label, size="xs", fw=600, c="dimmed", pl="xs")
                )
            group_pages = group.get("pages") if isinstance(group, dict) else []
            panel_children.extend(
                create_nav_links(cast(list[object], group_pages or []))
            )
            if index < len(groups) - 1:
                panel_children.append(dmc.Divider(my="xs"))
        accordion_items.append(
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        section.get("label"),
                        icon=DashIconify(icon=section.get("icon"), width=20, height=20),
                    ),
                    dmc.AccordionPanel(dmc.Stack(panel_children, gap="xs")),
                ],
                value=section.get("label"),
            )
        )

    expanded_label = sections[0]["label"] if sections else None
    expanded = [expanded_label] if expanded_label else []
    return dmc.Accordion(
        children=accordion_items,
        value=expanded,
        chevronPosition="right",
        multiple=True,
        className="aiml-nav-accordion",
    )


def create_aside():
    """Create aside panel for dataset selector."""
    return dmc.Stack(
        [
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    dmc.Text("Projects", fw=500, size="sm"),
                                    dmc.Badge(
                                        id="project-protected-badge",
                                        children="Unprotected",
                                        color="gray",
                                        variant="light",
                                    ),
                                ],
                                justify="space-between",
                            ),
                            dmc.Select(
                                id="project-selector",
                                data=[],
                                placeholder="Select project...",
                                searchable=True,
                                clearable=True,
                                leftSection=DashIconify(icon="carbon:workspace"),
                            ),
                            dmc.Text(
                                id="project-description",
                                size="xs",
                                c="dimmed",
                                children="No project selected",
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "New",
                                        id="project-create-button",
                                        leftSection=DashIconify(icon="carbon:add"),
                                        variant="light",
                                        size="xs",
                                    ),
                                    dmc.Button(
                                        "Edit",
                                        id="project-edit-button",
                                        leftSection=DashIconify(icon="carbon:edit"),
                                        variant="light",
                                        size="xs",
                                    ),
                                    dmc.Button(
                                        "Copy",
                                        id="project-copy-button",
                                        leftSection=DashIconify(icon="carbon:copy"),
                                        variant="light",
                                        size="xs",
                                    ),
                                ],
                                gap="xs",
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Save",
                                        id="project-save-button",
                                        leftSection=DashIconify(icon="carbon:save"),
                                        variant="subtle",
                                        size="xs",
                                    ),
                                    dmc.Button(
                                        "Delete",
                                        id="project-delete-button",
                                        leftSection=DashIconify(
                                            icon="carbon:trash-can"
                                        ),
                                        color="red",
                                        variant="subtle",
                                        size="xs",
                                    ),
                                    dmc.Button(
                                        "Protect",
                                        id="project-protect-button",
                                        leftSection=DashIconify(icon="carbon:locked"),
                                        variant="subtle",
                                        size="xs",
                                    ),
                                ],
                                gap="xs",
                            ),
                            html.Div(id="project-status"),
                        ],
                        gap="xs",
                    )
                ],
                p="sm",
                className="aiml-side-card",
            ),
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Active Dataset", fw=500, size="sm"),
                            dmc.Select(
                                id="dataset-selector",
                                data=[],
                                placeholder="Select dataset...",
                                searchable=True,
                                clearable=False,
                                leftSection=DashIconify(icon="carbon:data-table"),
                            ),
                            dmc.Group(
                                [
                                    dmc.Badge(
                                        id="dataset-rows-badge",
                                        children="0 rows",
                                        color="blue",
                                        variant="light",
                                    ),
                                    dmc.Badge(
                                        id="dataset-cols-badge",
                                        children="0 cols",
                                        color="green",
                                        variant="light",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                        gap="xs",
                    )
                ],
                p="sm",
                className="aiml-side-card",
            ),
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Quick Stats", fw=500, size="sm"),
                            dmc.Text(id="dataset-memory", size="xs", c="dimmed"),
                        ],
                        gap="xs",
                    )
                ],
                p="sm",
                className="aiml-side-card",
            ),
        ],
        gap="md",
        className="aiml-aside-stack",
    )


def create_footer():
    """Create application footer."""
    return dmc.Group(
        [
            dmc.Text(APP_TITLE, size="sm", c="dimmed"),
            dmc.Group(
                [
                    dmc.Anchor(
                        "Documentation", href=f"#{HOME_PAGE_ID}", size="sm", c="dimmed"
                    ),
                    dmc.Text("•", size="sm", c="dimmed"),
                    dmc.Anchor(
                        "GitHub",
                        href=GITHUB_URL,
                        size="sm",
                        c="dimmed",
                        target="_blank",
                    ),
                    dmc.Text("•", size="sm", c="dimmed"),
                    dmc.Anchor(
                        "Report Issue",
                        href=f"{GITHUB_URL}/issues",
                        size="sm",
                        c="dimmed",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
        ],
        justify="space-between",
        style={"width": "100%"},
        className="aiml-footer-group",
    )
