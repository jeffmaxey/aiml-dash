"""
Logistic Regression Page
=========================

Binary logistic regression for classification problems.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
import plotly.graph_objects as go
import plotly.express as px

from components.common import create_page_header
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the logistic regression page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Logistic Regression (GLM)",
                "Estimate logistic regression models for binary outcomes. View odds ratios, confusion matrix, and ROC curves.",
                icon="carbon:chart-logistic",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Model Specification", order=4),
                                        dmc.Select(
                                            id="logistic-dataset",
                                            label="Select dataset",
                                            data=[],
                                            placeholder="Choose a dataset",
                                        ),
                                        dmc.Select(
                                            id="logistic-response",
                                            label="Response variable",
                                            data=[],
                                            placeholder="Binary variable",
                                        ),
                                        dmc.MultiSelect(
                                            id="logistic-predictors",
                                            label="Predictors",
                                            data=[],
                                            placeholder="Select predictors",
                                            searchable=True,
                                        ),
                                        dmc.Button(
                                            "Estimate Model",
                                            id="logistic-estimate-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
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
                    span={"base": 12, "md": 4},
                ),
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab("Summary", value="summary"),
                                    dmc.TabsTab("Confusion Matrix", value="confusion"),
                                    dmc.TabsTab("Plots", value="plots"),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [html.Div(id="logistic-summary")],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        )
                                    ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [html.Div(id="logistic-confusion")],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        )
                                    ],
                                    value="confusion",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Select(
                                                    id="logistic-plot-type",
                                                    label="Plot type",
                                                    data=[
                                                        {
                                                            "value": "roc",
                                                            "label": "ROC Curve",
                                                        },
                                                        {
                                                            "value": "coefficients",
                                                            "label": "Coefficients",
                                                        },
                                                    ],
                                                    value="roc",
                                                    mb="md",
                                                ),
                                                dcc.Graph(id="logistic-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        )
                                    ],
                                    value="plots",
                                ),
                            ],
                            value="summary",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            dcc.Store(id="logistic-model-store"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(Output("logistic-dataset", "data"), Input("logistic-dataset", "id"))
def populate_datasets(_):
    return [{"value": name, "label": name} for name in app_manager.data_manager.get_dataset_names()]


@callback(
    [Output("logistic-response", "data"), Output("logistic-predictors", "data")],
    Input("logistic-dataset", "value"),
)
def populate_variables(dataset_name):
    if not dataset_name:
        return [], []
    df = app_manager.data_manager.get_dataset(dataset_name)
    all_cols = [{"value": col, "label": col} for col in df.columns]
    return all_cols, all_cols


@callback(
    [
        Output("logistic-model-store", "data"),
        Output("logistic-summary", "children"),
        Output("logistic-confusion", "children"),
    ],
    Input("logistic-estimate-btn", "n_clicks"),
    [
        State("logistic-dataset", "value"),
        State("logistic-response", "value"),
        State("logistic-predictors", "value"),
    ],
    prevent_initial_call=True,
)
def estimate_model(n_clicks, dataset_name, response, predictors):
    if not all([dataset_name, response, predictors]):
        return None, "Please select all required fields.", None

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        X = pd.get_dummies(df[predictors], drop_first=True)
        y = df[response]

        if y.nunique() != 2:
            return None, "Response variable must be binary (2 unique values).", None

        y_binary = (y == y.unique()[1]).astype(int)

        model = LogisticRegression(max_iter=1000)
        model.fit(X, y_binary)
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]

        acc = accuracy_score(y_binary, y_pred)
        precision = precision_score(y_binary, y_pred, zero_division=0)
        recall = recall_score(y_binary, y_pred, zero_division=0)
        f1 = f1_score(y_binary, y_pred, zero_division=0)
        auc = roc_auc_score(y_binary, y_proba)

        model_store = {
            "coefficients": {col: float(coef) for col, coef in zip(X.columns, model.coef_[0])},
            "intercept": float(model.intercept_[0]),
            "y_true": y_binary.tolist(),
            "y_pred": y_pred.tolist(),
            "y_proba": y_proba.tolist(),
            "accuracy": acc,
            "auc": auc,
        }

        summary = dmc.Stack(
            [
                dmc.Text("Model Summary", size="lg", fw=600),
                dmc.Table(
                    [
                        html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
                        html.Tbody([
                            html.Tr([html.Td("Accuracy"), html.Td(f"{acc:.4f}")]),
                            html.Tr([html.Td("Precision"), html.Td(f"{precision:.4f}")]),
                            html.Tr([html.Td("Recall"), html.Td(f"{recall:.4f}")]),
                            html.Tr([html.Td("F1 Score"), html.Td(f"{f1:.4f}")]),
                            html.Tr([html.Td("AUC"), html.Td(f"{auc:.4f}")]),
                        ]),
                    ],
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                ),
            ],
            gap="md",
        )

        cm = confusion_matrix(y_binary, y_pred)
        confusion_output = dmc.Stack(
            [
                dmc.Text("Confusion Matrix", size="lg", fw=600),
                dmc.Table(
                    [
                        html.Thead(
                            html.Tr([
                                html.Th(""),
                                html.Th("Predicted 0"),
                                html.Th("Predicted 1"),
                            ])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td("Actual 0"),
                                html.Td(f"{cm[0, 0]}"),
                                html.Td(f"{cm[0, 1]}"),
                            ]),
                            html.Tr([
                                html.Td("Actual 1"),
                                html.Td(f"{cm[1, 0]}"),
                                html.Td(f"{cm[1, 1]}"),
                            ]),
                        ]),
                    ],
                    withTableBorder=True,
                ),
            ],
            gap="md",
        )

        return model_store, summary, confusion_output
    except Exception as e:
        return None, f"Error: {str(e)}", None


@callback(
    Output("logistic-plot", "figure"),
    [Input("logistic-plot-type", "value"), Input("logistic-model-store", "data")],
)
def update_plot(plot_type, model_store):
    if not model_store:
        return go.Figure().add_annotation(
            text="Estimate a model first",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    if plot_type == "roc":
        from sklearn.metrics import roc_curve

        y_true = np.array(model_store["y_true"])
        y_proba = np.array(model_store["y_proba"])
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        fig = px.line(
            x=fpr,
            y=tpr,
            labels={"x": "False Positive Rate", "y": "True Positive Rate"},
            title=f"ROC Curve (AUC = {model_store['auc']:.4f})",
        )
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dash"), name="Random"))
    elif plot_type == "coefficients":
        coefs = model_store["coefficients"]
        fig = go.Figure(data=[go.Bar(x=list(coefs.values()), y=list(coefs.keys()), orientation="h")])
        fig.update_layout(title="Coefficient Plot", xaxis_title="Coefficient", yaxis_title="Variable")

    fig.update_layout(template="plotly_white", height=500)
    return fig
