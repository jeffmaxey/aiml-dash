"""
Common Components
================

Reusable UI components for the AIML Dash application.
"""

from typing import Any

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def create_page_header(title: str, description: str, icon: str = "carbon:data-table") -> dmc.Stack:
    """
    Create a consistent page header.

    Parameters
    ----------
    title : str
        Page title
    description : str
        Page description
    icon : str
        Iconify icon name

    Returns
    -------
    dmc.Stack
        Header component
    """
    return dmc.Stack(
        [
            dmc.Group(
                [
                    DashIconify(icon=icon, width=32, height=32),
                    dmc.Title(title, order=2),
                ],
                gap="sm",
            ),
            dmc.Text(description, c="dimmed", size="sm"),
        ],
        gap="xs",
        mb="md",
    )


def create_filter_section() -> dmc.Accordion:
    """
    Create data filter section with filter, sort, and slice controls.

    Returns
    -------
    dmc.Accordion
        Filter section component
    """
    return dmc.Accordion(
        children=[
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl("Data Filter & Sort"),
                    dmc.AccordionPanel([
                        dmc.Stack(
                            [
                                dmc.Textarea(
                                    id="data-filter-input",
                                    label="Filter (pandas query syntax)",
                                    placeholder="e.g., price > 5000 & cut == 'Ideal'",
                                    description="Enter a pandas query expression",
                                    minRows=2,
                                    autosize=True,
                                ),
                                dmc.TextInput(
                                    id="data-sort-input",
                                    label="Sort by (comma-separated columns)",
                                    placeholder="e.g., price, carat",
                                    description="Prefix with '-' for descending (e.g., -price)",
                                ),
                                dmc.TextInput(
                                    id="data-slice-input",
                                    label="Rows (slice)",
                                    placeholder="e.g., 1:100 or 0,5,10",
                                    description="Python slice notation or comma-separated indices",
                                ),
                            ],
                            gap="sm",
                        )
                    ]),
                ],
                value="filter",
            ),
        ],
        value=None,  # Start collapsed
    )


def create_variable_selector(
    var_id: str,
    label: str,
    multiple: bool = True,
    required: bool = False,
    description: str | None = None,
) -> dmc.Select | dmc.MultiSelect:
    """
    Create a variable selector component.

    Parameters
    ----------
    var_id : str
        Component ID
    label : str
        Label text
    multiple : bool
        Allow multiple selection
    required : bool
        Mark as required
    description : str, optional
        Help text

    Returns
    -------
    dmc.Select or dmc.MultiSelect
        Variable selector
    """
    common_props = {
        "id": var_id,
        "label": label,
        "placeholder": "Select variable(s)...",
        "searchable": True,
        "clearable": True,
        "nothingFoundMessage": "No variables found",
    }

    if description:
        common_props["description"] = description

    if required:
        common_props["required"] = True
        common_props["withAsterisk"] = True

    if multiple:
        return dmc.MultiSelect(**common_props)
    else:
        return dmc.Select(**common_props)


def create_function_selector(
    func_id: str,
    functions: dict[str, tuple],
    default: list[str] | None = None,
    label: str = "Functions",
) -> dmc.MultiSelect:
    """
    Create function selector for statistical functions.

    Parameters
    ----------
    func_id : str
        Component ID
    functions : dict
        Dictionary of function names to (display_name, description) tuples
    default : list of str, optional
        Default selected functions
    label : str
        Label text

    Returns
    -------
    dmc.MultiSelect
        Function selector
    """
    data: list[dict[str, Any]] = [
        {"value": k, "label": v[1] if isinstance(v, tuple) else k} for k, v in functions.items()
    ]

    return dmc.MultiSelect(
        id=func_id,
        label=label,
        placeholder="Select functions...",
        data=data,  # type: ignore[arg-type]
        value=default or [],
        searchable=True,
        clearable=True,
    )


def create_download_button(button_id: str, label: str = "Download Data", icon: str = "carbon:download") -> dmc.Group:
    """
    Create download button with icon.

    Parameters
    ----------
    button_id : str
        Component ID
    label : str
        Button label
    icon : str
        Icon name

    Returns
    -------
    dmc.Group
        Download button group
    """
    return dmc.Group([
        dmc.Button(
            label,
            id=button_id,
            leftSection=DashIconify(icon=icon),
            variant="light",
        ),
        dcc.Download(id=f"{button_id}-download"),
    ])


def create_notification(notif_id: str) -> html.Div:
    """
    Create notification container.

    Parameters
    ----------
    notif_id : str
        Component ID

    Returns
    -------
    html.Div
        Notification container
    """
    return html.Div(id=notif_id)


def create_code_display(code_id: str, language: str = "python") -> dmc.Code:
    """
    Create code display component.

    Parameters
    ----------
    code_id : str
        Component ID
    language : str
        Programming language

    Returns
    -------
    dmc.Code
        Code display component
    """
    return dmc.Code(
        id=code_id,
        children="# No code generated yet",
        block=True,
        style={
            "whiteSpace": "pre",
            "fontFamily": "monospace",
            "fontSize": "13px",
            "maxHeight": "400px",
            "overflowY": "auto",
            "padding": "16px",
            "backgroundColor": "#f8f9fa",
            "borderRadius": "4px",
        },
    )


def create_tabs(tabs_id: str, tabs_data: list[dict[str, Any]]) -> dmc.Tabs:
    """
    Create tabs component.

    Parameters
    ----------
    tabs_id : str
        Component ID
    tabs_data : list of dict
        List of tab specifications with 'value', 'label', 'icon', 'children'

    Returns
    -------
    dmc.Tabs
        Tabs component
    """
    tab_list = []
    tab_panels = []

    for tab in tabs_data:
        # Create tab
        tab_content = [tab["label"]]
        if "icon" in tab:
            tab_content.insert(0, DashIconify(icon=tab["icon"], width=16, height=16))

        tab_list.append(
            dmc.TabsTab(
                tab["label"],
                value=tab["value"],
                leftSection=DashIconify(icon=tab.get("icon", "carbon:document"), width=16, height=16)
                if "icon" in tab
                else None,
            )
        )

        # Create panel
        tab_panels.append(
            dmc.TabsPanel(
                tab["children"],
                value=tab["value"],
            )
        )

    return dmc.Tabs(
        id=tabs_id,
        value=tabs_data[0]["value"] if tabs_data else None,
        children=[dmc.TabsList(tab_list), *tab_panels],
    )


def create_info_card(title: str, value: Any, icon: str, color: str = "blue") -> dmc.Card:
    """
    Create information card for displaying stats.

    Parameters
    ----------
    title : str
        Card title
    value : Any
        Value to display
    icon : str
        Icon name
    color : str
        Color scheme

    Returns
    -------
    dmc.Card
        Info card component
    """
    return dmc.Card(
        children=[
            dmc.Group(
                [
                    DashIconify(icon=icon, width=24, height=24, color=color),
                    dmc.Stack(
                        [
                            dmc.Text(title, size="sm", c="dimmed"),
                            dmc.Text(str(value), size="xl", fw=700),
                        ],
                        gap=0,
                    ),
                ],
                justify="space-between",
            )
        ],
        withBorder=True,
        padding="sm",
        radius="md",
    )
