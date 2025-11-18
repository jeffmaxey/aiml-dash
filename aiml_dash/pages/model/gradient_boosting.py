"""
Gradient Boosted Trees Page
============================

Train gradient boosted tree models for classification and regression.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    r2_score,
    mean_squared_error,
    classification_report,
)
import plotly.graph_objects as go
import plotly.express as px

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the gradient boosting page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Gradient Boosted Trees",
                "Train gradient boosted tree models using iterative ensemble learning. Powerful for both classification and regression tasks.",
                icon="carbon:tree-view",
            ),
            dmc.Grid([
                # Left panel - model configuration
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Model Configuration", order=4),
                                        dmc.Select(
                                            id="gbt-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="gbt-target",
                                            label="Response Variable",
                                            placeholder="Select target variable...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="gbt-features",
                                            label="Explanatory Variables",
                                            placeholder="Select features...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.SegmentedControl(
                                            id="gbt-type",
                                            label="Model Type",
                                            data=[
                                                {
                                                    "label": "Classification",
                                                    "value": "classification",
                                                },
                                                {
                                                    "label": "Regression",
                                                    "value": "regression",
                                                },
                                            ],
                                            value="classification",
                                        ),
                                        dmc.Divider(
                                            label="Hyperparameters",
                                            labelPosition="center",
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-n-estimators",
                                            label="Number of Trees",
                                            description="Number of boosting stages",
                                            value=100,
                                            min=10,
                                            max=1000,
                                            step=10,
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-learning-rate",
                                            label="Learning Rate",
                                            description="Step size shrinkage",
                                            value=0.1,
                                            min=0.001,
                                            max=1.0,
                                            step=0.01,
                                            decimalScale=3,
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-max-depth",
                                            label="Maximum Depth",
                                            description="Maximum tree depth",
                                            value=3,
                                            min=1,
                                            max=20,
                                            step=1,
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-min-samples-split",
                                            label="Min Samples Split",
                                            description="Minimum samples to split node",
                                            value=2,
                                            min=2,
                                            max=100,
                                            step=1,
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-subsample",
                                            label="Subsample",
                                            description="Fraction of samples for fitting",
                                            value=1.0,
                                            min=0.1,
                                            max=1.0,
                                            step=0.1,
                                            decimalScale=2,
                                        ),
                                        dmc.Divider(
                                            label="Validation",
                                            labelPosition="center",
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-test-size",
                                            label="Test Set Size (%)",
                                            value=20,
                                            min=10,
                                            max=50,
                                            step=5,
                                        ),
                                        dmc.NumberInput(
                                            id="gbt-random-seed",
                                            label="Random Seed",
                                            value=1234,
                                            min=0,
                                            step=1,
                                        ),
                                        dmc.Button(
                                            "Train Model",
                                            id="gbt-train-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
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
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Predictions",
                                        value="predictions",
                                        leftSection=DashIconify(icon="carbon:chart-scatter"),
                                    ),
                                    dmc.TabsTab(
                                        "Feature Importance",
                                        value="importance",
                                        leftSection=DashIconify(icon="carbon:chart-bar"),
                                    ),
                                    dmc.TabsTab(
                                        "Training History",
                                        value="history",
                                        leftSection=DashIconify(icon="carbon:chart-line"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="gbt-summary"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="gbt-predictions"),
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
                                                dcc.Graph(id="gbt-importance-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="importance",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="gbt-history-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="history",
                                ),
                            ],
                            value="summary",
                            id="gbt-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="gbt-model-store"),
            html.Div(id="gbt-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("gbt-dataset", "data"),
    Input("gbt-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("gbt-target", "data"), Output("gbt-features", "data")],
    Input("gbt-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        columns = [{"label": col, "value": col} for col in df.columns]
        return columns, columns
    except Exception:
        return [], []


@callback(
    [
        Output("gbt-summary", "children"),
        Output("gbt-predictions", "children"),
        Output("gbt-importance-plot", "figure"),
        Output("gbt-history-plot", "figure"),
        Output("gbt-model-store", "data"),
        Output("gbt-notification", "children"),
    ],
    Input("gbt-train-btn", "n_clicks"),
    [
        State("gbt-dataset", "value"),
        State("gbt-target", "value"),
        State("gbt-features", "value"),
        State("gbt-type", "value"),
        State("gbt-n-estimators", "value"),
        State("gbt-learning-rate", "value"),
        State("gbt-max-depth", "value"),
        State("gbt-min-samples-split", "value"),
        State("gbt-subsample", "value"),
        State("gbt-test-size", "value"),
        State("gbt-random-seed", "value"),
    ],
    prevent_initial_call=True,
)
def train_gradient_boosting(
    n_clicks,
    dataset_name,
    target,
    features,
    model_type,
    n_estimators,
    learning_rate,
    max_depth,
    min_samples_split,
    subsample,
    test_size,
    random_seed,
):
    """Train gradient boosting model."""
    if not all([dataset_name, target, features]):
        return (
            dmc.Text("Please select dataset, target, and features.", c="red"),
            "",
            {},
            {},
            None,
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
        X = df[features]
        y = df[target]

        # Handle categorical features
        X_encoded = pd.get_dummies(X, drop_first=True)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=test_size / 100, random_state=random_seed
        )

        # Train model
        if model_type == "classification":
            model = GradientBoostingClassifier(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                subsample=subsample,
                random_state=random_seed,
            )
        else:
            model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                subsample=subsample,
                random_state=random_seed,
            )

        model.fit(X_train, y_train)

        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Summary
        if model_type == "classification":
            train_acc = accuracy_score(y_train, y_train_pred)
            test_acc = accuracy_score(y_test, y_test_pred)

            summary = dmc.Stack(
                [
                    dmc.Text("Model Type: Classification", fw=600),
                    dmc.Text(f"Number of Trees: {n_estimators}"),
                    dmc.Text(f"Learning Rate: {learning_rate}"),
                    dmc.Text(f"Max Depth: {max_depth}"),
                    dmc.Divider(),
                    dmc.Text(f"Training Accuracy: {train_acc:.4f}", c="blue"),
                    dmc.Text(f"Test Accuracy: {test_acc:.4f}", c="green", fw=600),
                    dmc.Divider(),
                    dmc.Text("Classification Report:", fw=600),
                    dmc.Code(classification_report(y_test, y_test_pred), block=True),
                ],
                gap="xs",
            )
        else:
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

            summary = dmc.Stack(
                [
                    dmc.Text("Model Type: Regression", fw=600),
                    dmc.Text(f"Number of Trees: {n_estimators}"),
                    dmc.Text(f"Learning Rate: {learning_rate}"),
                    dmc.Text(f"Max Depth: {max_depth}"),
                    dmc.Divider(),
                    dmc.Text(f"Training R²: {train_r2:.4f}", c="blue"),
                    dmc.Text(f"Test R²: {test_r2:.4f}", c="green", fw=600),
                    dmc.Text(f"Training RMSE: {train_rmse:.4f}"),
                    dmc.Text(f"Test RMSE: {test_rmse:.4f}"),
                ],
                gap="xs",
            )

        # Predictions plot
        pred_df = pd.DataFrame({
            "Actual": y_test,
            "Predicted": y_test_pred,
        })

        if model_type == "classification":
            # Confusion matrix as heatmap
            from sklearn.metrics import confusion_matrix

            cm = confusion_matrix(y_test, y_test_pred)
            predictions = dcc.Graph(
                figure=px.imshow(
                    cm,
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    title="Confusion Matrix",
                    text_auto=True,
                )
            )
        else:
            # Actual vs predicted scatter
            predictions = dcc.Graph(
                figure=px.scatter(
                    pred_df,
                    x="Actual",
                    y="Predicted",
                    title="Actual vs Predicted",
                    trendline="ols",
                )
            )

        # Feature importance
        importance_df = pd.DataFrame({
            "Feature": X_encoded.columns,
            "Importance": model.feature_importances_,
        }).sort_values("Importance", ascending=True)

        importance_fig = px.bar(
            importance_df.tail(15),
            x="Importance",
            y="Feature",
            orientation="h",
            title="Top 15 Feature Importances",
        )

        # Training history (validation deviance)
        history_fig = go.Figure()
        history_fig.add_trace(
            go.Scatter(
                x=list(range(1, n_estimators + 1)),
                y=model.train_score_,
                mode="lines",
                name="Training",
            )
        )
        history_fig.update_layout(
            title="Training Deviance",
            xaxis_title="Boosting Iteration",
            yaxis_title="Deviance",
        )

        return (
            summary,
            predictions,
            importance_fig,
            history_fig,
            {"model": "trained"},
            dmc.Notification(
                title="Success",
                message="Model trained successfully",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {str(e)}", c="red"),
            "",
            {},
            {},
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )
