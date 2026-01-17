"""
Evaluate Classification Page
=============================

Evaluate and compare classification model performance.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    auc,
    classification_report,
)
import plotly.graph_objects as go
import plotly.express as px

from components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the evaluate classification page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Evaluate Classification",
                "Evaluate and compare classification model predictions. Calculate metrics and visualize confusion matrices.",
                icon="carbon:chart-evaluation",
            ),
            create_two_column_layout(
                # Left panel
                create_control_card(
                    [
                        dmc.Title("Evaluation Settings", order=4),
                        dmc.Select(
                            id="evalclass-dataset",
                            label="Dataset",
                            placeholder="Select dataset...",
                            data=[],
                        ),
                        dmc.Select(
                            id="evalclass-actual",
                            label="Actual Labels",
                            placeholder="Select actual column...",
                            data=[],
                        ),
                        dmc.Select(
                            id="evalclass-predicted",
                            label="Predicted Labels",
                            placeholder="Select predicted column...",
                            data=[],
                        ),
                        dmc.Select(
                            id="evalclass-proba",
                            label="Predicted Probabilities (Optional)",
                            placeholder="Select probability column...",
                            data=[],
                        ),
                        dmc.Divider(
                            label="Compare Models",
                            labelPosition="center",
                        ),
                        dmc.MultiSelect(
                            id="evalclass-compare-preds",
                            label="Additional Predictions",
                            description="Select other prediction columns to compare",
                            placeholder="Select columns...",
                            data=[],
                            searchable=True,
                        ),
                        create_action_button(
                            button_id="evalclass-evaluate-btn",
                            label="Evaluate Model",
                            icon="carbon:play",
                            size="lg",
                            color="blue",
                        ),
                        create_action_button(
                            button_id="evalclass-export-btn",
                            label="Export Report (CSV)",
                            icon="carbon:download",
                            variant="light",
                        ),
                    ],
                ),
                # Right panel
                dmc.Tabs(
                    [
                        dmc.TabsList([
                            dmc.TabsTab(
                                "Metrics",
                                value="metrics",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Confusion Matrix",
                                value="confusion",
                                leftSection=DashIconify(icon="carbon:table"),
                            ),
                            dmc.TabsTab(
                                "ROC Curve",
                                value="roc",
                                leftSection=DashIconify(icon="carbon:chart-line"),
                            ),
                            dmc.TabsTab(
                                "Class Distribution",
                                value="distribution",
                                leftSection=DashIconify(icon="carbon:chart-bar"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="evalclass-metrics"),
                                    ],
                                ),
                            ],
                                    value="metrics",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalclass-confusion-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="confusion",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalclass-roc-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="roc",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="evalclass-distribution-plot"),
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
                            id="evalclass-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden components
            dcc.Download(id="evalclass-download"),
            html.Div(id="evalclass-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("evalclass-dataset", "data"),
    Input("evalclass-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("evalclass-actual", "data"),
        Output("evalclass-predicted", "data"),
        Output("evalclass-proba", "data"),
        Output("evalclass-compare-preds", "data"),
    ],
    Input("evalclass-dataset", "value"),
)
def update_columns(dataset_name):
    """Update available columns when dataset changes."""
    if not dataset_name:
        return [], [], [], []

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        return all_cols, all_cols, numeric_cols, all_cols
    except Exception:
        return [], [], [], []


@callback(
    [
        Output("evalclass-metrics", "children"),
        Output("evalclass-confusion-plot", "figure"),
        Output("evalclass-roc-plot", "figure"),
        Output("evalclass-distribution-plot", "figure"),
        Output("evalclass-notification", "children"),
    ],
    Input("evalclass-evaluate-btn", "n_clicks"),
    [
        State("evalclass-dataset", "value"),
        State("evalclass-actual", "value"),
        State("evalclass-predicted", "value"),
        State("evalclass-proba", "value"),
        State("evalclass-compare-preds", "value"),
    ],
    prevent_initial_call=True,
)
def evaluate_classification(n_clicks, dataset_name, actual_col, pred_col, proba_col, compare_cols):
    """Evaluate classification model performance."""
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
        df = app_manager.data_manager.get_dataset(dataset_name)
        y_actual = df[actual_col].dropna()
        y_pred = df[pred_col].loc[y_actual.index]

        # Remove any remaining NaN values
        mask = ~(y_pred.isna())
        y_actual = y_actual[mask]
        y_pred = y_pred[mask]

        # Calculate metrics
        accuracy = accuracy_score(y_actual, y_pred)

        # Handle binary vs multiclass
        labels = sorted(y_actual.unique())
        is_binary = len(labels) == 2

        if is_binary:
            precision = precision_score(y_actual, y_pred, average="binary")
            recall = recall_score(y_actual, y_pred, average="binary")
            f1 = f1_score(y_actual, y_pred, average="binary")
        else:
            precision = precision_score(y_actual, y_pred, average="weighted", zero_division=0)
            recall = recall_score(y_actual, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_actual, y_pred, average="weighted", zero_division=0)

        # Metrics summary
        metrics_data = [
            {"Metric": "Accuracy", "Value": f"{accuracy:.4f}"},
            {"Metric": "Precision", "Value": f"{precision:.4f}"},
            {"Metric": "Recall", "Value": f"{recall:.4f}"},
            {"Metric": "F1 Score", "Value": f"{f1:.4f}"},
            {"Metric": "Samples", "Value": str(len(y_actual))},
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
                        acc_comp = accuracy_score(y_act_comp, y_comp)
                        if is_binary:
                            f1_comp = f1_score(y_act_comp, y_comp, average="binary", zero_division=0)
                        else:
                            f1_comp = f1_score(y_act_comp, y_comp, average="weighted", zero_division=0)
                        compare_data.append({
                            "Model": col,
                            "Accuracy": f"{acc_comp:.4f}",
                            "F1 Score": f"{f1_comp:.4f}",
                        })

            if compare_data:
                compare_table = dag.AgGrid(
                    rowData=compare_data,
                    columnDefs=[
                        {"field": "Model"},
                        {"field": "Accuracy"},
                        {"field": "F1 Score"},
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
                            style={"height": "200px"},
                        ),
                        dmc.Divider(),
                        dmc.Text("Classification Report:", fw=600),
                        dmc.Code(classification_report(y_actual, y_pred), block=True),
                        dmc.Divider(),
                        dmc.Text("Model Comparison:", fw=600, size="lg"),
                        compare_table,
                    ],
                    gap="md",
                )
            else:
                metrics = dmc.Stack(
                    [
                        dag.AgGrid(
                            rowData=metrics_data,
                            columnDefs=[
                                {"field": "Metric", "flex": 1},
                                {"field": "Value", "flex": 1},
                            ],
                            defaultColDef={"sortable": False},
                            style={"height": "200px"},
                        ),
                        dmc.Divider(),
                        dmc.Text("Classification Report:", fw=600),
                        dmc.Code(classification_report(y_actual, y_pred), block=True),
                    ],
                    gap="md",
                )
        else:
            metrics = dmc.Stack(
                [
                    dag.AgGrid(
                        rowData=metrics_data,
                        columnDefs=[
                            {"field": "Metric", "flex": 1},
                            {"field": "Value", "flex": 1},
                        ],
                        defaultColDef={"sortable": False},
                        style={"height": "200px"},
                    ),
                    dmc.Divider(),
                    dmc.Text("Classification Report:", fw=600),
                    dmc.Code(classification_report(y_actual, y_pred), block=True),
                ],
                gap="md",
            )

        # Confusion matrix
        cm = confusion_matrix(y_actual, y_pred, labels=labels)
        confusion_fig = px.imshow(
            cm,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=labels,
            y=labels,
            title="Confusion Matrix",
            text_auto=True,
            color_continuous_scale="Blues",
        )

        # ROC curve (if probabilities available)
        if proba_col and proba_col in df.columns and is_binary:
            y_proba = df[proba_col].loc[y_actual.index]
            mask = ~(y_proba.isna())
            y_act_roc = y_actual[mask]
            y_proba = y_proba[mask]

            if len(y_proba) > 0:
                fpr, tpr, _ = roc_curve(y_act_roc, y_proba, pos_label=labels[1])
                roc_auc = auc(fpr, tpr)

                roc_fig = go.Figure()
                roc_fig.add_trace(
                    go.Scatter(
                        x=fpr,
                        y=tpr,
                        mode="lines",
                        name=f"ROC (AUC = {roc_auc:.4f})",
                        line=dict(color="blue", width=2),
                    )
                )
                roc_fig.add_trace(
                    go.Scatter(
                        x=[0, 1],
                        y=[0, 1],
                        mode="lines",
                        name="Random",
                        line=dict(color="red", dash="dash"),
                    )
                )
                roc_fig.update_layout(
                    title="ROC Curve",
                    xaxis_title="False Positive Rate",
                    yaxis_title="True Positive Rate",
                )
            else:
                roc_fig = go.Figure()
                roc_fig.add_annotation(
                    text="No valid probability data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )
        else:
            roc_fig = go.Figure()
            roc_fig.add_annotation(
                text="ROC curve requires binary classification and probability column",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        # Distribution plot
        dist_df = pd.DataFrame({
            "Class": list(y_actual) + list(y_pred),
            "Type": ["Actual"] * len(y_actual) + ["Predicted"] * len(y_pred),
        })

        distribution_fig = px.histogram(
            dist_df,
            x="Class",
            color="Type",
            barmode="group",
            title="Class Distribution: Actual vs Predicted",
        )

        return (
            metrics,
            confusion_fig,
            roc_fig,
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
            dmc.Text(f"Error: {str(e)}", c="red"),
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
    Output("evalclass-download", "data"),
    Input("evalclass-export-btn", "n_clicks"),
    [
        State("evalclass-dataset", "value"),
        State("evalclass-actual", "value"),
        State("evalclass-predicted", "value"),
    ],
    prevent_initial_call=True,
)
def export_evaluation(n_clicks, dataset_name, actual_col, pred_col):
    """Export evaluation results to CSV."""
    if not all([dataset_name, actual_col, pred_col]):
        return None

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        y_actual = df[actual_col].dropna()
        y_pred = df[pred_col].loc[y_actual.index]

        mask = ~(y_pred.isna())
        y_actual = y_actual[mask]
        y_pred = y_pred[mask]

        results_df = pd.DataFrame({
            "Actual": y_actual,
            "Predicted": y_pred,
            "Correct": y_actual == y_pred,
        })

        return dcc.send_data_frame(results_df.to_csv, "classification_evaluation.csv", index=False)

    except Exception:
        return None
