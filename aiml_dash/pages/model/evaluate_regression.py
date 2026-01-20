"""
Evaluate Regression Page
=========================

Evaluate and compare regression model performance.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from utils.data_manager import data_manager


def layout():
    """Create the evaluate regression page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Evaluate Regression",
                "Evaluate and compare regression model predictions. Calculate performance metrics and visualize residuals.",
                icon="carbon:chart-evaluation",
            ),
            dmc.Grid([
                # Left panel - evaluation settings
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Evaluation Settings", order=4),
                                        dmc.Select(
                                            id="evalreg-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="evalreg-actual",
                                            label="Actual Values",
                                            placeholder="Select actual column...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="evalreg-predicted",
                                            label="Predicted Values",
                                            placeholder="Select predicted column...",
                                            data=[],
                                        ),
                                        dmc.Divider(
                                            label="Compare Models",
                                            labelPosition="center",
                                        ),
                                        dmc.MultiSelect(
                                            id="evalreg-compare-preds",
                                            label="Additional Predictions",
                                            description="Select other prediction columns to compare",
                                            placeholder="Select columns...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Button(
                                            "Evaluate Model",
                                            id="evalreg-evaluate-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
                                        ),
                                        dmc.Divider(),
                                        dmc.Button(
                                            "Export Report (CSV)",
                                            id="evalreg-export-btn",
                                            leftSection=DashIconify(icon="carbon:download", width=20),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                    ],
                                    gap="sm",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                # Right panel - results
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Metrics",
                                        value="metrics",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Residuals",
                                        value="residuals",
                                        leftSection=DashIconify(icon="carbon:chart-scatter"),
                                    ),
                                    dmc.TabsTab(
                                        "Actual vs Predicted",
                                        value="predictions",
                                        leftSection=DashIconify(icon="carbon:chart-line"),
                                    ),
                                    dmc.TabsTab(
                                        "Distribution",
                                        value="distribution",
                                        leftSection=DashIconify(icon="carbon:chart-histogram"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="evalreg-metrics"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="metrics",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalreg-residuals-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="residuals",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalreg-predictions-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="predictions",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalreg-distribution-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="distribution",
                                ),
                            ],
                            value="metrics",
                            id="evalreg-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden components
            dcc.Download(id="evalreg-download"),
            html.Div(id="evalreg-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("evalreg-dataset", "data"),
    Input("evalreg-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("evalreg-actual", "data"),
        Output("evalreg-predicted", "data"),
        Output("evalreg-compare-preds", "data"),
    ],
    Input("evalreg-dataset", "value"),
)
def update_columns(dataset_name):
    """Update available columns when dataset changes."""
    if not dataset_name:
        return [], [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        columns = [{"label": col, "value": col} for col in numeric_cols]
        return columns, columns, columns
    except Exception:
        return [], [], []


@callback(
    [
        Output("evalreg-metrics", "children"),
        Output("evalreg-residuals-plot", "figure"),
        Output("evalreg-predictions-plot", "figure"),
        Output("evalreg-distribution-plot", "figure"),
        Output("evalreg-notification", "children"),
    ],
    Input("evalreg-evaluate-btn", "n_clicks"),
    [
        State("evalreg-dataset", "value"),
        State("evalreg-actual", "value"),
        State("evalreg-predicted", "value"),
        State("evalreg-compare-preds", "value"),
    ],
    prevent_initial_call=True,
)
def evaluate_regression(n_clicks, dataset_name, actual_col, pred_col, compare_cols):
    """Evaluate regression model performance."""
    if not all([dataset_name, actual_col, pred_col]):
        return (
            dmc.Text("Please select dataset, actual, and predicted columns.", c="red"),
            {},
            {},
            {},
            dmc.Notification(
                title="Error",
                message="Missing required inputs",
                color="red",
                action="show",
            ),
        )

    try:
        # Get data
        df = data_manager.get_dataset(dataset_name)
        y_actual = df[actual_col].dropna()
        y_pred = df[pred_col].loc[y_actual.index]

        # Remove any remaining NaN values
        mask = ~(y_pred.isna())
        y_actual = y_actual[mask]
        y_pred = y_pred[mask]

        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
        mae = mean_absolute_error(y_actual, y_pred)
        r2 = r2_score(y_actual, y_pred)

        try:
            mape = mean_absolute_percentage_error(y_actual, y_pred) * 100
        except Exception:
            mape = np.mean(np.abs((y_actual - y_pred) / y_actual)) * 100

        residuals = y_actual - y_pred

        # Metrics summary
        metrics_data = [
            {"Metric": "R² Score", "Value": f"{r2:.4f}"},
            {"Metric": "RMSE", "Value": f"{rmse:.4f}"},
            {"Metric": "MAE", "Value": f"{mae:.4f}"},
            {"Metric": "MAPE", "Value": f"{mape:.2f}%"},
            {"Metric": "Mean Residual", "Value": f"{residuals.mean():.4f}"},
            {"Metric": "Std Residual", "Value": f"{residuals.std():.4f}"},
        ]

        # Add comparison metrics if other predictions selected
        if compare_cols:
            compare_data = []
            for col in compare_cols:
                if col != pred_col and col in df.columns:
                    y_comp = df[col].loc[y_actual.index]
                    mask = ~(y_comp.isna())
                    y_act_comp = y_actual[mask]
                    y_comp = y_comp[mask]

                    if len(y_comp) > 0:
                        r2_comp = r2_score(y_act_comp, y_comp)
                        rmse_comp = np.sqrt(mean_squared_error(y_act_comp, y_comp))
                        compare_data.append({
                            "Model": col,
                            "R²": f"{r2_comp:.4f}",
                            "RMSE": f"{rmse_comp:.4f}",
                        })

            if compare_data:
                compare_table = dag.AgGrid(
                    rowData=compare_data,
                    columnDefs=[
                        {"field": "Model"},
                        {"field": "R²"},
                        {"field": "RMSE"},
                    ],
                    defaultColDef={"sortable": True, "filter": True},
                    style={"height": "200px"},
                )

                metrics = dmc.Stack(
                    [
                        dmc.Text("Primary Model Metrics:", fw=600, size="lg"),
                        dag.AgGrid(
                            rowData=metrics_data,
                            columnDefs=[
                                {"field": "Metric", "flex": 1},
                                {"field": "Value", "flex": 1},
                            ],
                            defaultColDef={"sortable": False},
                            style={"height": "250px"},
                        ),
                        dmc.Divider(),
                        dmc.Text("Model Comparison:", fw=600, size="lg"),
                        compare_table,
                    ],
                    gap="md",
                )
            else:
                metrics = dag.AgGrid(
                    rowData=metrics_data,
                    columnDefs=[
                        {"field": "Metric", "flex": 1},
                        {"field": "Value", "flex": 1},
                    ],
                    defaultColDef={"sortable": False},
                    style={"height": "300px"},
                )
        else:
            metrics = dag.AgGrid(
                rowData=metrics_data,
                columnDefs=[
                    {"field": "Metric", "flex": 1},
                    {"field": "Value", "flex": 1},
                ],
                defaultColDef={"sortable": False},
                style={"height": "300px"},
            )

        # Residuals plot
        residuals_df = pd.DataFrame({
            "Predicted": y_pred,
            "Residuals": residuals,
        })

        residuals_fig = px.scatter(
            residuals_df,
            x="Predicted",
            y="Residuals",
            title="Residuals vs Predicted",
            trendline="lowess",
        )
        residuals_fig.add_hline(y=0, line_dash="dash", line_color="red")

        # Predictions plot
        pred_df = pd.DataFrame({
            "Actual": y_actual,
            "Predicted": y_pred,
        })

        predictions_fig = px.scatter(
            pred_df,
            x="Actual",
            y="Predicted",
            title="Actual vs Predicted",
            trendline="ols",
        )
        # Add perfect prediction line
        min_val = min(y_actual.min(), y_pred.min())
        max_val = max(y_actual.max(), y_pred.max())
        predictions_fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode="lines",
                line={"color": "red", "dash": "dash"},
                name="Perfect Prediction",
            )
        )

        # Distribution plot
        distribution_fig = go.Figure()
        distribution_fig.add_trace(
            go.Histogram(
                x=y_actual,
                name="Actual",
                opacity=0.7,
            )
        )
        distribution_fig.add_trace(
            go.Histogram(
                x=y_pred,
                name="Predicted",
                opacity=0.7,
            )
        )
        distribution_fig.update_layout(
            title="Distribution of Actual vs Predicted",
            barmode="overlay",
            xaxis_title="Value",
            yaxis_title="Count",
        )

        return (
            metrics,
            residuals_fig,
            predictions_fig,
            distribution_fig,
            dmc.Notification(
                title="Success",
                message="Evaluation complete",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {e!s}", c="red"),
            {},
            {},
            {},
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("evalreg-download", "data"),
    Input("evalreg-export-btn", "n_clicks"),
    [
        State("evalreg-dataset", "value"),
        State("evalreg-actual", "value"),
        State("evalreg-predicted", "value"),
    ],
    prevent_initial_call=True,
)
def export_evaluation(n_clicks, dataset_name, actual_col, pred_col):
    """Export evaluation metrics to CSV."""
    if not all([dataset_name, actual_col, pred_col]):
        return None

    try:
        df = data_manager.get_dataset(dataset_name)
        y_actual = df[actual_col].dropna()
        y_pred = df[pred_col].loc[y_actual.index]

        mask = ~(y_pred.isna())
        y_actual = y_actual[mask]
        y_pred = y_pred[mask]

        results_df = pd.DataFrame({
            "Actual": y_actual,
            "Predicted": y_pred,
            "Residual": y_actual - y_pred,
        })

        return dcc.send_data_frame(results_df.to_csv, "regression_evaluation.csv", index=False)

    except Exception:
        return None
