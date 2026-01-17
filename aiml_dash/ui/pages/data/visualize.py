"""
Visualize Page
==============

Data visualization with Plotly charts.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.express as px

from components.common import (
    create_action_button,
    create_control_card,
    create_filter_section,
    create_page_header,
    create_results_card,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager
from utils.settings import app_settings


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
            create_two_column_layout(
                # Left panel - chart controls
                create_control_card(
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
                                create_action_button(
                                    button_id="viz-create-btn",
                                    label="Create Chart",
                                    icon="carbon:chart-line",
                                ),
                            ],
                            gap="md",
                        )
                    ],
                    title="Chart Settings",
                ),
                # Right panel - chart display
                create_results_card(
                    [
                        html.Div(id="viz-chart-container"),
                    ],
                ),
            ),
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

    df = app_manager.data_manager.get_dataset(dataset_name)
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
        return create_empty_state(message="Select variables and click Create Chart")

    df = app_manager.data_manager.get_dataset(dataset_name)
    if df is None:
        return dmc.Alert("Error loading dataset", color="red")

    # Apply filter
    if data_filter and data_filter.strip():
        try:
            df = df.query(data_filter)
        except:
            pass

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
            font=dict(family="Inter, sans-serif"),
        )

        return dcc.Graph(figure=fig, config={"displayModeBar": True, "displaylogo": False})

    except Exception as e:
        return dmc.Alert(
            f"Error creating chart: {str(e)}",
            title="Visualization Error",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
