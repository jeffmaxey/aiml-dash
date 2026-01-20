"""
Visualize Page
==============

Data visualization with Plotly charts.
"""

import contextlib

import dash_mantine_components as dmc
import plotly.express as px
from components.common import create_filter_section, create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from utils.data_manager import data_manager


def layout():
    """Create the Visualize page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Visualize Data",
                "Create interactive charts and visualizations. Choose from scatter plots, histograms, box plots, and more.",
                icon="carbon:chart-scatter",
            ),
            create_filter_section(),
            dmc.Grid([
                # Left panel - chart controls
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Select(
                                            id="viz-chart-type",
                                            label="Chart Type",
                                            value="scatter",
                                            data=[
                                                {
                                                    "label": "Scatter Plot",
                                                    "value": "scatter",
                                                },
                                                {
                                                    "label": "Line Chart",
                                                    "value": "line",
                                                },
                                                {
                                                    "label": "Bar Chart",
                                                    "value": "bar",
                                                },
                                                {
                                                    "label": "Histogram",
                                                    "value": "histogram",
                                                },
                                                {
                                                    "label": "Box Plot",
                                                    "value": "box",
                                                },
                                                {
                                                    "label": "Violin Plot",
                                                    "value": "violin",
                                                },
                                                {
                                                    "label": "Heatmap",
                                                    "value": "heatmap",
                                                },
                                            ],
                                        ),
                                        dmc.Select(
                                            id="viz-x-var",
                                            label="X Variable",
                                            placeholder="Select X variable...",
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="viz-y-var",
                                            label="Y Variable (optional)",
                                            placeholder="Select Y variable...",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.Select(
                                            id="viz-color-var",
                                            label="Color By (optional)",
                                            placeholder="Select color variable...",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.Select(
                                            id="viz-facet-var",
                                            label="Facet By (optional)",
                                            placeholder="Select facet variable...",
                                            searchable=True,
                                            clearable=True,
                                        ),
                                        dmc.TextInput(
                                            id="viz-title",
                                            label="Chart Title",
                                            placeholder="Enter chart title...",
                                        ),
                                        dmc.Button(
                                            "Create Chart",
                                            id="viz-create-btn",
                                            leftSection=DashIconify(icon="carbon:chart-line"),
                                            fullWidth=True,
                                        ),
                                    ],
                                    gap="md",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=4,
                ),
                # Right panel - chart display
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                html.Div(id="viz-chart-container"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span=8,
                ),
            ]),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("viz-x-var", "data"),
    Output("viz-y-var", "data"),
    Output("viz-color-var", "data"),
    Output("viz-facet-var", "data"),
    Input("dataset-selector", "value"),
)
def update_viz_selectors(dataset_name):
    """Update variable selectors for visualization."""
    if not dataset_name:
        return [], [], [], []

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return [], [], [], []

    all_vars = [{"label": col, "value": col} for col in df.columns]
    categorical_vars = [
        {"label": col, "value": col}
        for col in df.columns
        if df[col].dtype in ["object", "category"] or df[col].nunique() < 20
    ]

    return all_vars, all_vars, all_vars, categorical_vars


@callback(
    Output("viz-chart-container", "children"),
    Input("viz-create-btn", "n_clicks"),
    State("dataset-selector", "value"),
    State("viz-chart-type", "value"),
    State("viz-x-var", "value"),
    State("viz-y-var", "value"),
    State("viz-color-var", "value"),
    State("viz-facet-var", "value"),
    State("viz-title", "value"),
    State("data-filter-input", "value"),
    prevent_initial_call=True,
)
def create_visualization(
    n_clicks,
    dataset_name,
    chart_type,
    x_var,
    y_var,
    color_var,
    facet_var,
    title,
    data_filter,
):
    """Create and display visualization."""
    if not n_clicks or not dataset_name or not x_var:
        return dmc.Center(
            dmc.Text("Select variables and click Create Chart", c="dimmed"),
            style={"height": "500px"},
        )

    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Alert("Error loading dataset", color="red")

    # Apply filter
    if data_filter and data_filter.strip():
        with contextlib.suppress(BaseException):
            df = df.query(data_filter)

    try:
        # Create chart based on type
        if chart_type == "scatter":
            if not y_var:
                return dmc.Alert("Scatter plot requires Y variable", color="yellow")
            fig = px.scatter(
                df,
                x=x_var,
                y=y_var,
                color=color_var,
                facet_col=facet_var,
                title=title or "Scatter Plot",
            )

        elif chart_type == "line":
            if not y_var:
                return dmc.Alert("Line chart requires Y variable", color="yellow")
            fig = px.line(
                df,
                x=x_var,
                y=y_var,
                color=color_var,
                facet_col=facet_var,
                title=title or "Line Chart",
            )

        elif chart_type == "bar":
            if not y_var:
                # Count plot
                fig = px.histogram(
                    df,
                    x=x_var,
                    color=color_var,
                    facet_col=facet_var,
                    title=title or "Bar Chart",
                )
            else:
                fig = px.bar(
                    df,
                    x=x_var,
                    y=y_var,
                    color=color_var,
                    facet_col=facet_var,
                    title=title or "Bar Chart",
                )

        elif chart_type == "histogram":
            fig = px.histogram(
                df,
                x=x_var,
                color=color_var,
                facet_col=facet_var,
                title=title or "Histogram",
            )

        elif chart_type == "box":
            fig = px.box(
                df,
                x=x_var,
                y=y_var,
                color=color_var,
                facet_col=facet_var,
                title=title or "Box Plot",
            )

        elif chart_type == "violin":
            fig = px.violin(
                df,
                x=x_var,
                y=y_var,
                color=color_var,
                facet_col=facet_var,
                title=title or "Violin Plot",
            )

        elif chart_type == "heatmap":
            # For heatmap, need to create correlation matrix
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title=title or "Correlation Heatmap")

        else:
            return dmc.Alert("Unknown chart type", color="red")

        # Update layout
        fig.update_layout(
            template="plotly_white",
            height=600,
            font={"family": "Inter, sans-serif"},
        )

        return dcc.Graph(figure=fig, config={"displayModeBar": True, "displaylogo": False})

    except Exception as e:
        return dmc.Alert(
            f"Error creating chart: {e!s}",
            title="Visualization Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
