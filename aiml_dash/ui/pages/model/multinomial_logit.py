"""
Multinomial Logistic Regression Page
======================================

Multinomial logistic regression for multi-class classification problems.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
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
    """Create the multinomial logistic regression page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Multinomial Logistic Regression",
                "Estimate multinomial logistic regression models for multi-class classification problems.",
                icon="carbon:flow",
            ),
            create_two_column_layout(
                # Left panel
                create_control_card(
                    [
                        dmc.Title("Model Configuration", order=4),
                        dmc.Select(
                            id="mnl-dataset",
                            label="Dataset",
                            placeholder="Select dataset...",
                            data=[],
                        ),
                        dmc.Select(
                            id="mnl-target",
                            label="Response Variable",
                            placeholder="Select target variable...",
                            data=[],
                        ),
                        dmc.MultiSelect(
                            id="mnl-features",
                            label="Explanatory Variables",
                            placeholder="Select features...",
                            data=[],
                            searchable=True,
                        ),
                        dmc.Select(
                            id="mnl-solver",
                            label="Solver",
                            data=[
                                {
                                    "label": "lbfgs",
                                    "value": "lbfgs",
                                },
                                {
                                    "label": "newton-cg",
                                    "value": "newton-cg",
                                },
                                {"label": "sag", "value": "sag"},
                                {"label": "saga", "value": "saga"},
                            ],
                            value="lbfgs",
                        ),
                        dmc.NumberInput(
                            id="mnl-max-iter",
                            label="Maximum Iterations",
                            value=100,
                            min=10,
                            max=1000,
                            step=10,
                        ),
                        dmc.NumberInput(
                            id="mnl-test-size",
                            label="Test Set Size (%)",
                            value=20,
                            min=10,
                            max=50,
                            step=5,
                        ),
                        create_action_button(
                            button_id="mnl-train-btn",
                            label="Train Model",
                            icon="carbon:play",
                            size="lg",
                            color="green",
                        ),
                    ],
                ),
                # Right panel
                dmc.Tabs(
                    [
                        dmc.TabsList([
                            dmc.TabsTab(
                                "Summary",
                                value="summary",
                                leftSection=DashIconify(icon="carbon:report"),
                            ),
                            dmc.TabsTab(
                                "Confusion Matrix",
                                value="confusion",
                                leftSection=DashIconify(icon="carbon:table"),
                            ),
                            dmc.TabsTab(
                                "Class Probabilities",
                                value="probabilities",
                                leftSection=DashIconify(icon="carbon:chart-bar"),
                            ),
                        ]),
                        dmc.TabsPanel(
                            [
                                create_results_card(
                                    [
                                        html.Div(id="mnl-summary"),
                                    ],
                                ),
                            ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="mnl-confusion-plot"),
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
                                                html.Div(id="mnl-probabilities"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="probabilities",
                                ),
                            ],
                            value="summary",
                            id="mnl-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="mnl-model-store"),
            html.Div(id="mnl-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("mnl-dataset", "data"),
    Input("mnl-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = app_manager.data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [Output("mnl-target", "data"), Output("mnl-features", "data")],
    Input("mnl-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], []

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)
        columns = [{"label": col, "value": col} for col in df.columns]
        return columns, columns
    except Exception:
        return [], []


@callback(
    [
        Output("mnl-summary", "children"),
        Output("mnl-confusion-plot", "figure"),
        Output("mnl-probabilities", "children"),
        Output("mnl-model-store", "data"),
        Output("mnl-notification", "children"),
    ],
    Input("mnl-train-btn", "n_clicks"),
    [
        State("mnl-dataset", "value"),
        State("mnl-target", "value"),
        State("mnl-features", "value"),
        State("mnl-solver", "value"),
        State("mnl-max-iter", "value"),
        State("mnl-test-size", "value"),
    ],
    prevent_initial_call=True,
)
def train_model(n_clicks, dataset_name, target, features, solver, max_iter, test_size):
    """Train multinomial logistic regression model."""
    if not all([dataset_name, target, features]):
        return (
            dmc.Text("Please select dataset, target, and features.", c="red"),
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message="Missing required inputs",
                color="red",
                action="show",
            ),
        )

    try:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder

        # Get data
        df = app_manager.data_manager.get_dataset(dataset_name)
        X = df[features]
        y = df[target]

        # Encode categorical features
        X_encoded = pd.get_dummies(X, drop_first=True)

        # Encode target if categorical
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_encoded, test_size=test_size / 100, random_state=42
        )

        # Train model
        model = LogisticRegression(
            multi_class="multinomial",
            solver=solver,
            max_iter=max_iter,
            random_state=42,
        )
        model.fit(X_train, y_train)

        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        y_test_proba = model.predict_proba(X_test)

        # Metrics
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)

        # Summary
        summary = dmc.Stack(
            [
                dmc.Text("Multinomial Logistic Regression", fw=600, size="lg"),
                dmc.Divider(),
                dmc.Text(f"Number of Classes: {len(le.classes_)}"),
                dmc.Text(f"Classes: {', '.join(map(str, le.classes_))}"),
                dmc.Text(f"Features: {len(X_encoded.columns)}"),
                dmc.Divider(),
                dmc.Text(f"Training Accuracy: {train_acc:.4f}", c="blue"),
                dmc.Text(f"Test Accuracy: {test_acc:.4f}", c="green", fw=600),
                dmc.Divider(),
                dmc.Text("Classification Report:", fw=600),
                dmc.Code(
                    classification_report(y_test, y_test_pred, target_names=le.classes_.astype(str)),
                    block=True,
                ),
            ],
            gap="xs",
        )

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)
        confusion_fig = px.imshow(
            cm,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=le.classes_,
            y=le.classes_,
            title="Confusion Matrix",
            text_auto=True,
            color_continuous_scale="Blues",
        )

        # Class probabilities for first 10 test samples
        proba_df = pd.DataFrame(y_test_proba[:10], columns=le.classes_)
        proba_df["Actual"] = le.inverse_transform(y_test[:10])
        proba_df["Predicted"] = le.inverse_transform(y_test_pred[:10])

        probabilities = dag.AgGrid(
            rowData=proba_df.to_dict("records"),
            columnDefs=[{"field": col, "flex": 1} for col in proba_df.columns],
            defaultColDef={"sortable": True},
            style={"height": "400px"},
        )

        return (
            summary,
            confusion_fig,
            probabilities,
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
            {},
            "",
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )
