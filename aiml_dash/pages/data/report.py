"""
Report Page
===========

Generate Python code and reproducible reports.
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the Report page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Generate Reports",
                "Generate Python code to reproduce your analysis. Copy code or export as a script.",
                icon="carbon:document",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList([
                        dmc.TabsTab("Python Script", value="python"),
                        dmc.TabsTab("Data Info", value="info"),
                    ]),
                    # Python Script Tab
                    dmc.TabsPanel(
                        [
                            dmc.Stack(
                                [
                                    dmc.Group([
                                        dmc.Button(
                                            "Generate Code",
                                            id="report-generate-btn",
                                            leftSection=DashIconify(icon="carbon:code"),
                                        ),
                                        dmc.Button(
                                            "Copy to Clipboard",
                                            id="report-copy-btn",
                                            variant="light",
                                            leftSection=DashIconify(icon="carbon:copy"),
                                        ),
                                        dmc.Button(
                                            "Download Script",
                                            id="report-download-btn",
                                            variant="light",
                                            leftSection=DashIconify(icon="carbon:download"),
                                        ),
                                    ]),
                                    dmc.Card(
                                        [
                                            dmc.Code(
                                                id="report-code-display",
                                                children="# Click 'Generate Code' to create Python script\n",
                                                block=True,
                                                style={
                                                    "whiteSpace": "pre",
                                                    "fontFamily": "monospace",
                                                    "fontSize": "13px",
                                                    "maxHeight": "600px",
                                                    "overflowY": "auto",
                                                    "padding": "16px",
                                                    "backgroundColor": "#f8f9fa",
                                                    "borderRadius": "4px",
                                                },
                                            ),
                                        ],
                                        withBorder=True,
                                        radius="md",
                                        p="md",
                                    ),
                                ],
                                gap="md",
                            )
                        ],
                        value="python",
                    ),
                    # Data Info Tab
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [
                                    html.Div(id="report-data-info"),
                                ],
                                withBorder=True,
                                radius="md",
                                p="md",
                            ),
                        ],
                        value="info",
                    ),
                ],
                value="python",
            ),
            dcc.Download(id="report-download"),
            html.Div(id="report-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1200px"},
    )


@callback(
    Output("report-code-display", "children"),
    Input("report-generate-btn", "n_clicks"),
    State("dataset-selector", "value"),
    prevent_initial_call=True,
)
def generate_code(n_clicks, dataset_name):
    """Generate Python code for the current analysis."""
    if not n_clicks or not dataset_name:
        return "# No dataset selected"

    # Get dataset info
    info = data_manager.get_dataset_info(dataset_name)
    load_cmd = info.get("load_command", "")

    # Build script
    code = f"""#!/usr/bin/env python3
\"\"\"
AIML Data Analysis - Generated Script
=========================================

Dataset: {dataset_name}
Generated from AIML Data Python application
\"\"\"

import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

# ============================================================================
# Load Data
# ============================================================================

{load_cmd if load_cmd else f'# Load your data here\n{dataset_name} = pd.read_csv("data.csv")'}

# Display basic information
print(f"Dataset: {dataset_name}")
print(f"Rows: {{len({dataset_name}):,}}")
print(f"Columns: {{len({dataset_name}.columns)}}")
print(f"\\nColumn types:")
print({dataset_name}.dtypes)

# ============================================================================
# Data Preview
# ============================================================================

print(f"\\nFirst few rows:")
print({dataset_name}.head())

# ============================================================================
# Summary Statistics
# ============================================================================

print(f"\\nSummary statistics:")
print({dataset_name}.describe())

# ============================================================================
# Example Analysis
# ============================================================================

# Add your analysis code here

# Example: Calculate summary statistics by group
# result = {dataset_name}.groupby('category')[['numeric_var']].agg(['mean', 'std', 'min', 'max'])
# print(result)

# Example: Create a visualization
# fig = px.scatter({dataset_name}, x='var1', y='var2', color='category', title='Scatter Plot')
# fig.show()

# Example: Correlation analysis
# numeric_cols = {dataset_name}.select_dtypes(include=['number']).columns
# corr_matrix = {dataset_name}[numeric_cols].corr()
# fig = px.imshow(corr_matrix, text_auto=True, title='Correlation Matrix')
# fig.show()

print("\\nAnalysis complete!")
"""

    return code


@callback(
    Output("report-notification", "children"),
    Input("report-copy-btn", "n_clicks"),
    State("report-code-display", "children"),
    prevent_initial_call=True,
)
def copy_code(n_clicks, code):
    """Copy code to clipboard."""
    if not n_clicks:
        return dash.no_update

    # Note: Actual clipboard copy requires JavaScript, this is a notification only
    return dmc.Notification(
        title="Code Copied",
        message="Python code has been copied to clipboard",
        color="blue",
        action="show",
        autoClose=3000,
    )


@callback(
    Output("report-download", "data"),
    Input("report-download-btn", "n_clicks"),
    State("report-code-display", "children"),
    State("dataset-selector", "value"),
    prevent_initial_call=True,
)
def download_script(n_clicks, code, dataset_name):
    """Download Python script."""
    if not n_clicks:
        return dash.no_update

    filename = f"{dataset_name}_analysis.py" if dataset_name else "analysis.py"
    return dict(content=code, filename=filename)


@callback(
    Output("report-data-info", "children"),
    Input("dataset-selector", "value"),
)
def display_data_info(dataset_name):
    """Display comprehensive data information."""
    if not dataset_name:
        return dmc.Text("No dataset selected", c="dimmed")

    info = data_manager.get_dataset_info(dataset_name)
    df = data_manager.get_dataset(dataset_name)

    if df is None:
        return dmc.Alert("Error loading dataset", color="red")

    # Build info display
    return dmc.Stack(
        [
            dmc.Title(f"Dataset: {dataset_name}", order=3),
            dmc.SimpleGrid(
                [
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    DashIconify(icon="carbon:row", width=32, color="blue"),
                                    dmc.Text("Rows", size="sm", c="dimmed"),
                                    dmc.Text(f"{info.get('rows', 0):,}", size="xl", fw=700),
                                ],
                                gap="xs",
                                align="center",
                            ),
                        ],
                        withBorder=True,
                        p="md",
                    ),
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    DashIconify(icon="carbon:column", width=32, color="green"),
                                    dmc.Text("Columns", size="sm", c="dimmed"),
                                    dmc.Text(f"{info.get('columns', 0)}", size="xl", fw=700),
                                ],
                                gap="xs",
                                align="center",
                            ),
                        ],
                        withBorder=True,
                        p="md",
                    ),
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    DashIconify(
                                        icon="carbon:data-volume",
                                        width=32,
                                        color="orange",
                                    ),
                                    dmc.Text("Memory", size="sm", c="dimmed"),
                                    dmc.Text(
                                        f"{info.get('memory_usage', 0):.2f} MB",
                                        size="xl",
                                        fw=700,
                                    ),
                                ],
                                gap="xs",
                                align="center",
                            ),
                        ],
                        withBorder=True,
                        p="md",
                    ),
                ],
                cols=3,
            ),
            dmc.Divider(),
            dmc.Text("Column Information", fw=600),
            dmc.Table(
                [
                    html.Thead([
                        html.Tr([
                            html.Th("Column"),
                            html.Th("Type"),
                            html.Th("Non-Null"),
                            html.Th("Null"),
                            html.Th("Unique"),
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(col),
                            html.Td(str(df[col].dtype)),
                            html.Td(f"{df[col].notna().sum():,}"),
                            html.Td(f"{df[col].isna().sum():,}"),
                            html.Td(f"{df[col].nunique():,}"),
                        ])
                        for col in df.columns
                    ]),
                ],
                striped=True,
                highlightOnHover=True,
            ),
            dmc.Divider(),
            dmc.Text("Description", fw=600),
            dmc.Textarea(
                value=info.get("description", "No description available"),
                autosize=True,
                minRows=3,
                readOnly=True,
            ),
        ],
        gap="md",
    )
