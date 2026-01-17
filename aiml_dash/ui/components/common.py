"""
Common Components
================

Reusable UI components for the AIML Dash application.
"""

import dash_mantine_components as dmc
import dash_ag_grid as dag
from dash_iconify import DashIconify
from dash import html, dcc
from typing import List, Optional, Dict, Any, Literal, TypedDict


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
    description: Optional[str] = None,
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
    functions: Dict[str, tuple],
    default: Optional[List[str]] = None,
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
    data: List[Dict[str, Any]] = [
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


def create_tabs(tabs_id: str, tabs_data: List[Dict[str, Any]]) -> dmc.Tabs:
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


def create_ag_grid(
    grid_id: str,
    row_data: Optional[List[Dict[str, Any]]] = None,
    column_defs: Optional[List[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> dag.AgGrid:
    """
    Create an AG Grid component with standardized configuration.

    Parameters
    ----------
    grid_id : str
        Component ID
    row_data : list of dict, optional
        Grid row data
    column_defs : list of dict, optional
        Column definitions. If not provided, the first column will have checkboxes.
    **kwargs : Any
        Additional AG Grid properties

    Returns
    -------
    dag.AgGrid
        Configured AG Grid component
    """
    # Default column definitions with checkbox in first column
    default_column_defs = column_defs or []

    # Add checkbox selection to first column if column_defs provided
    if default_column_defs and len(default_column_defs) > 0:
        if "checkboxSelection" not in default_column_defs[0]:
            default_column_defs[0]["checkboxSelection"] = True
            default_column_defs[0]["headerCheckboxSelection"] = True

    # Default configuration
    default_config = {
        "id": grid_id,
        "rowData": row_data or [],
        "columnDefs": default_column_defs,
        "defaultColDef": {
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # we NEED to add this line or the cells won't adjust per columns
            "autoHeight": True,
        },
        "style": {"height": "600px", "width": "100%"},
        "dashGridOptions": {
            # Enable multiple selection
            "rowSelection": "multiple",
            # "suppressRowClickSelection": True,
            # "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "pagination": True,
            # Compact spacing similar to ag-theme-balham
            "rowHeight": 30,  # Smaller rows like balham
            "headerHeight": 30,  # Smaller headers like balham
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    }

    # Merge with any additional kwargs
    default_config.update(kwargs)

    return dag.AgGrid(**default_config)


def create_error_notification(message: str, title: str = "Error") -> dmc.Notification:
    """
    Create an error notification.

    Parameters
    ----------
    message : str
        Error message
    title : str
        Notification title

    Returns
    -------
    dmc.Notification
        Error notification component
    """
    return dmc.Notification(
        title=title,
        message=message,
        color="red",
        action="show",
        autoClose=5000,
        icon=DashIconify(icon="carbon:warning"),
    )


def create_success_notification(message: str, title: str = "Success") -> dmc.Notification:
    """
    Create a success notification.

    Parameters
    ----------
    message : str
        Success message
    title : str
        Notification title

    Returns
    -------
    dmc.Notification
        Success notification component
    """
    return dmc.Notification(
        title=title,
        message=message,
        color="green",
        action="show",
        autoClose=5000,
        icon=DashIconify(icon="carbon:checkmark"),
    )


def create_error_alert(message: str, title: str = "Error") -> dmc.Alert:
    """
    Create an error alert.

    Parameters
    ----------
    message : str
        Error message
    title : str
        Alert title

    Returns
    -------
    dmc.Alert
        Error alert component
    """
    return dmc.Alert(
        title=title,
        children=message,
        color="red",
        icon=DashIconify(icon="carbon:warning"),
    )


def create_warning_alert(message: str, title: str = "Warning") -> dmc.Alert:
    """
    Create a warning alert.

    Parameters
    ----------
    message : str
        Warning message
    title : str
        Alert title

    Returns
    -------
    dmc.Alert
        Warning alert component
    """
    return dmc.Alert(
        title=title,
        children=message,
        color="yellow",
        icon=DashIconify(icon="carbon:warning-alt"),
    )


def create_info_alert(message: str, title: str = "Info") -> dmc.Alert:
    """
    Create an info alert.

    Parameters
    ----------
    message : str
        Info message
    title : str
        Alert title

    Returns
    -------
    dmc.Alert
        Info alert component
    """
    return dmc.Alert(
        title=title,
        children=message,
        color="blue",
        icon=DashIconify(icon="carbon:information"),
    )


def get_table(table_id, column_defs: List[Dict[str, Any]]) -> dag.AgGrid:
    table = dag.AgGrid(
        id=table_id,
        columnDefs=column_defs,
        persistence=True,  # https://community.plotly.com/t/how-to-add-persistence-to-dash-ag-grid/74944
        style={"height": "600px", "width": "100%"},
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # we  NEED to add this line or the cells won't adjust per columns
            "autoHeight": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
        },
        dashGridOptions={
            # Enable multiple selection
            "alwaysShowHorizontalScroll": True,
            "rowSelection": "multiple",
            "checkboxSelection": "True",
            # "suppressRowClickSelection": True,
            # "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "pagination": True,
            "isRowSelectable": {"function": "log(params)"},
            # Compact spacing similar to ag-theme-balham
            "rowHeight": 30,  # Smaller rows like balham
            "headerHeight": 30,  # Smaller headers like balham
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options,
            # tooltips will not disappear while hovered and users
            # will be able to click and select text within
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            # "tooltipShowDelay": 0,  # Makes tooltip show immediately (Default 2000ms)
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
            # this will set the number of items per page be a function of the height
            # if we load too many rows that are not visible, the graphics is not smart enough
            # to hide what is not visible, so it takes longer for the page to load
            "paginationAutoPageSize": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
            # Known issue: https://community.plotly.com/t/dash-ag-grid-showing-empty-cells-where-there-shouldnt-be-empty-cells/76108/2
            # AG Grid will display headers containing "dot" characters as empty cells
            "suppressFieldDotNotation": True,
        },
    )
    return table

def create_control_card(children: Any, title: Optional[str] = None) -> dmc.Card:
    """
    Create a card for control panels.

    Parameters
    ----------
    children : Any
        Card content
    title : str, optional
        Card title

    Returns
    -------
    dmc.Card
        Control card component
    """
    content = []
    if title:
        content.append(dmc.Title(title, order=4, mb="md"))

    if isinstance(children, list):
        content.extend(children)
    else:
        content.append(children)

    return dmc.Card(
        dmc.Stack(content, gap="md"),
        withBorder=True,
        radius="md",
        p="md",
    )


def create_results_card(children: Any, title: Optional[str] = None) -> dmc.Card:
    """
    Create a card for results display.

    Parameters
    ----------
    children : Any
        Card content
    title : str, optional
        Card title

    Returns
    -------
    dmc.Card
        Results card component
    """
    content = []
    if title:
        content.append(dmc.Title(title, order=4, mb="md"))

    if isinstance(children, list):
        content.extend(children)
    else:
        content.append(children)

    return dmc.Card(
        content if len(content) == 1 else dmc.Stack(content, gap="md"),
        withBorder=True,
        radius="md",
        p="md",
    )


def create_two_column_layout(
    left_content: Any,
    right_content: Any,
    left_span: int = 4,
    right_span: int = 8,
) -> dmc.Grid:
    """
    Create a two-column layout (typically controls on left, results on right).

    Parameters
    ----------
    left_content : Any
        Left column content
    right_content : Any
        Right column content
    left_span : int
        Left column span (out of 12)
    right_span : int
        Right column span (out of 12)

    Returns
    -------
    dmc.Grid
        Two-column grid layout
    """
    return dmc.Grid([
        dmc.GridCol(left_content, span={"base": 12, "md": left_span}),
        dmc.GridCol(right_content, span={"base": 12, "md": right_span}),
    ])


def create_action_button(
    button_id: str,
    label: str,
    icon: str = "carbon:play",
    color: str = "blue",
    variant: str = "filled",
    full_width: bool = True,
    size: str = "md",
) -> dmc.Button:
    """
    Create a standardized action button.

    Parameters
    ----------
    button_id : str
        Component ID
    label : str
        Button label
    icon : str
        Icon name
    color : str
        Button color
    variant : str
        Button variant
    full_width : bool
        Full width button
    size : str
        Button size

    Returns
    -------
    dmc.Button
        Action button
    """
    return dmc.Button(
        label,
        id=button_id,
        leftSection=DashIconify(icon=icon, width=20),
        color=color,
        variant=variant,
        fullWidth=full_width,
        size=size,
    )


def create_dataset_selector(
    selector_id: str = "dataset-selector",
    label: str = "Dataset",
    required: bool = True,
) -> dmc.Select:
    """
    Create a dataset selector.

    Parameters
    ----------
    selector_id : str
        Component ID
    label : str
        Selector label
    required : bool
        Mark as required

    Returns
    -------
    dmc.Select
        Dataset selector
    """
    props = {
        "id": selector_id,
        "label": label,
        "placeholder": "Select dataset...",
        "data": [],
        "searchable": True,
        "clearable": not required,
    }

    if required:
        props["required"] = True
        props["withAsterisk"] = True

    return dmc.Select(**props)


def create_numeric_input(
    input_id: str,
    label: str,
    value: float = 0,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    step: float = 0.1,
    description: Optional[str] = None,
) -> dmc.NumberInput:
    """
    Create a numeric input field.

    Parameters
    ----------
    input_id : str
        Component ID
    label : str
        Input label
    value : float
        Default value
    min_val : float, optional
        Minimum value
    max_val : float, optional
        Maximum value
    step : float
        Step size
    description : str, optional
        Help text

    Returns
    -------
    dmc.NumberInput
        Numeric input component
    """
    props = {
        "id": input_id,
        "label": label,
        "value": value,
        "step": step,
    }

    if min_val is not None:
        props["min"] = min_val
    if max_val is not None:
        props["max"] = max_val
    if description:
        props["description"] = description

    return dmc.NumberInput(**props)


def create_upload_button(
    upload_id: str,
    button_text: str = "Upload File",
    icon: str = "carbon:upload",
    multiple: bool = False,
) -> dcc.Upload:
    """
    Create an upload button.

    Parameters
    ----------
    upload_id : str
        Component ID
    button_text : str
        Button text
    icon : str
        Icon name
    multiple : bool
        Allow multiple files

    Returns
    -------
    dcc.Upload
        Upload component
    """
    return dcc.Upload(
        id=upload_id,
        children=dmc.Button(
            button_text,
            leftSection=DashIconify(icon=icon),
            variant="light",
            fullWidth=True,
        ),
        multiple=multiple,
    )


def create_export_section(
    export_csv_id: str = "export-csv",
    export_excel_id: str = "export-excel",
    show_excel: bool = False,
) -> dmc.Stack:
    """
    Create export buttons section.

    Parameters
    ----------
    export_csv_id : str
        CSV export button ID
    export_excel_id : str
        Excel export button ID
    show_excel : bool
        Show Excel export button

    Returns
    -------
    dmc.Stack
        Export buttons stack
    """
    buttons = [
        dmc.Button(
            "Export to CSV",
            id=export_csv_id,
            leftSection=DashIconify(icon="carbon:download"),
            variant="light",
            fullWidth=True,
        ),
        dcc.Download(id=f"{export_csv_id}-download"),
    ]

    if show_excel:
        buttons.extend([
            dmc.Button(
                "Export to Excel",
                id=export_excel_id,
                leftSection=DashIconify(icon="carbon:document-export"),
                variant="light",
                fullWidth=True,
            ),
            dcc.Download(id=f"{export_excel_id}-download"),
        ])

    return dmc.Stack(buttons, gap="sm")


def create_segmented_control(
    control_id: str,
    options: List[Dict[str, str]],
    default_value: Optional[str] = None,
    label: Optional[str] = None,
    full_width: bool = True,
) -> dmc.Stack | dmc.SegmentedControl:
    """
    Create a segmented control with optional label.

    Parameters
    ----------
    control_id : str
        Component ID
    options : list of dict
        List of {'label': str, 'value': str} options
    default_value : str, optional
        Default selected value
    label : str, optional
        Control label
    full_width : bool
        Full width control

    Returns
    -------
    dmc.Stack or dmc.SegmentedControl
        Segmented control (with label if provided)
    """
    control = dmc.SegmentedControl(
        id=control_id,
        value=default_value or options[0]["value"] if options else None,
        data=options,
        fullWidth=full_width,
    )

    if label:
        return dmc.Stack(
            [
                dmc.Text(label, fw=600, size="sm"),
                control,
            ],
            gap="xs",
        )

    return control


def create_empty_state(
    message: str = "No data available",
    icon: str = "carbon:data-base",
    height: str = "400px",
) -> dmc.Center:
    """
    Create an empty state display.

    Parameters
    ----------
    message : str
        Message to display
    icon : str
        Icon name
    height : str
        Container height

    Returns
    -------
    dmc.Center
        Empty state component
    """
    return dmc.Center(
        dmc.Stack(
            [
                DashIconify(icon=icon, width=48, height=48, color="gray"),
                dmc.Text(message, c="dimmed", size="lg"),
            ],
            align="center",
            gap="md",
        ),
        style={"height": height},
    )
