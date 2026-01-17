"""
Naive Bayes Page
================

Naive Bayes classification for categorical outcomes.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix
import plotly.graph_objects as go

from components.common import (
    create_page_header,
    create_control_card,
    create_results_card,
    create_action_button,
    create_two_column_layout,
)
from aiml_dash.managers.app_manager import app_manager


def layout():
    """Create the Naive Bayes page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Naive Bayes",
                "Probabilistic classifier based on Bayes' theorem with strong independence assumptions. Works well with categorical and continuous features.",
                icon="carbon:license",
            ),
            dmc.Tabs(
                [
                    dmc.TabsList([
                        dmc.TabsTab(
                            "Model",
                            value="model",
                            leftSection=DashIconify(icon="carbon:model", width=16),
                        ),
                        dmc.TabsTab(
                            "Summary",
                            value="summary",
                            leftSection=DashIconify(icon="carbon:document", width=16),
                        ),
                        dmc.TabsTab(
                            "Predict",
                            value="predict",
                            leftSection=DashIconify(icon="carbon:chart-bubble", width=16),
                        ),
                        dmc.TabsTab(
                            "Plot",
                            value="plot",
                            leftSection=DashIconify(icon="carbon:chart-scatter", width=16),
                        ),
                    ]),
                    # Model Tab
                    dmc.TabsPanel(
                        [
                            create_two_column_layout(
                                create_control_card(
                                    [
                                        dmc.Title(
                                            "Model Configuration",
                                            order=4,
                                        ),
                                        dmc.Select(
                                            id="nb-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="nb-response",
                                            label="Response variable",
                                            description="Categorical outcome to predict",
                                            placeholder="Select response variable...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.MultiSelect(
                                            id="nb-explanatory",
                                            label="Explanatory variables",
                                            description="Features to use for prediction",
                                            placeholder="Select explanatory variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="nb-type",
                                            label="Naive Bayes type",
                                            description="Gaussian for continuous, Multinomial for counts",
                                            data=[
                                                {
                                                    "label": "Gaussian",
                                                    "value": "gaussian",
                                                },
                                                {
                                                    "label": "Multinomial",
                                                    "value": "multinomial",
                                                },
                                            ],
                                            value="gaussian",
                                        ),
                                        dmc.NumberInput(
                                            id="nb-smoothing",
                                            label="Smoothing parameter (alpha)",
                                            description="Laplace smoothing (0 = no smoothing)",
                                            value=1.0,
                                            min=0,
                                            step=0.1,
                                        ),
                                        dmc.NumberInput(
                                            id="nb-train-split",
                                            label="Training data %",
                                            description="Percentage of data for training",
                                            value=80,
                                            min=50,
                                            max=95,
                                            step=5,
                                            suffix="%",
                                        ),
                                        dmc.NumberInput(
                                            id="nb-seed",
                                            label="Random seed",
                                            value=1234,
                                            min=0,
                                        ),
                                        create_action_button(
                                            button_id="nb-estimate-btn",
                                            label="Estimate Model",
                                            icon="carbon:play",
                                            size="lg",
                                            color="blue",
                                        ),
                                    ],
                                ),
                                create_results_card(
                                    [html.Div(id="nb-model-status")],
                                ),
                            ),
                        ],
                        value="model",
                    ),
                    # Summary Tab
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [
                                    dmc.Title("Model Summary", order=4),
                                    html.Div(id="nb-summary-output"),
                                ],
                            ),
                        ],
                        value="summary",
                    ),
                    # Predict Tab
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [html.Div(id="nb-predictions")],
                            ),
                        ],
                        value="predict",
                    ),
                    # Plot Tab
                    dmc.TabsPanel(
                        [
                            create_results_card(
                                [dcc.Graph(id="nb-plot", style={"height": "600px"})],
                            ),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="nb-tabs",
            ),
            dcc.Store(id="nb-model-store"),
            dcc.Store(id="nb-results-store"),
            html.Div(id="nb-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("nb-dataset", "data"),
    Output("nb-pred-dataset", "data"),
    Input("nb-tabs", "value"),
)
def update_dataset_list(_):
    """Update available datasets."""
    datasets = [{"label": name, "value": name} for name in app_manager.data_manager.get_dataset_names()]
    return datasets, datasets


@callback(
    Output("nb-response", "data"),
    Output("nb-explanatory", "data"),
    Input("nb-dataset", "value"),
)
def update_variable_lists(dataset_name):
    """Update variable lists based on selected dataset."""
    if not dataset_name:
        return [], []

    df = app_manager.data_manager.get_dataset(dataset_name)
    if df is None:
        return [], []

    # Response should be categorical
    response_vars = [
        {"label": col, "value": col} for col in df.columns if df[col].dtype == "object" or df[col].nunique() < 20
    ]

    all_vars = [{"label": col, "value": col} for col in df.columns]

    return response_vars, all_vars


@callback(
    Output("nb-model-store", "data"),
    Output("nb-results-store", "data"),
    Output("nb-model-status", "children"),
    Input("nb-estimate-btn", "n_clicks"),
    State("nb-dataset", "value"),
    State("nb-response", "value"),
    State("nb-explanatory", "value"),
    State("nb-type", "value"),
    State("nb-smoothing", "value"),
    State("nb-train-split", "value"),
    State("nb-seed", "value"),
    prevent_initial_call=True,
)
def estimate_naive_bayes(n_clicks, dataset_name, response, explanatory, nb_type, smoothing, train_split, seed):
    """Estimate Naive Bayes model."""
    if not all([dataset_name, response, explanatory]):
        return (
            None,
            None,
            dmc.Alert(
                "Please select dataset, response, and explanatory variables",
                color="red",
            ),
        )

    try:
        df = app_manager.data_manager.get_dataset(dataset_name)

        # Prepare data
        X = df[explanatory].copy()
        y = df[response].copy()

        # Handle categorical variables
        for col in X.select_dtypes(include=["object"]).columns:
            X[col] = pd.Categorical(X[col]).codes

        # Handle missing values
        X = X.fillna(X.mean() if nb_type == "gaussian" else 0)

        # Split data
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=train_split / 100, random_state=seed, stratify=y
        )

        # Train model
        if nb_type == "gaussian":
            model = GaussianNB(var_smoothing=smoothing)
        else:
            # Convert to non-negative for multinomial
            X_train = np.abs(X_train)
            X_test = np.abs(X_test)
            model = MultinomialNB(alpha=smoothing)

        model.fit(X_train, y_train)

        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        y_prob_test = model.predict_proba(X_test)

        # Metrics
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)

        # Store results
        results = {
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "n_train": len(y_train),
            "n_test": len(y_test),
            "n_features": len(explanatory),
            "classes": model.classes_.tolist(),
            "confusion_matrix": confusion_matrix(y_test, y_pred_test).tolist(),
            "y_test": y_test.tolist(),
            "y_pred": y_pred_test.tolist(),
            "y_prob": y_prob_test.tolist(),
        }

        status = dmc.Stack(
            [
                dmc.Alert(
                    "Model estimated successfully!",
                    title="Success",
                    color="green",
                ),
                dmc.Text(f"Training accuracy: {train_acc:.3f}"),
                dmc.Text(f"Test accuracy: {test_acc:.3f}"),
                dmc.Text(f"Training observations: {len(y_train)}"),
                dmc.Text(f"Test observations: {len(y_test)}"),
            ],
            gap="xs",
        )

        return (
            {
                "dataset": dataset_name,
                "response": response,
                "explanatory": explanatory,
                "nb_type": nb_type,
                "smoothing": smoothing,
            },
            results,
            status,
        )

    except Exception as e:
        return None, None, dmc.Alert(f"Error: {str(e)}", color="red")


@callback(
    Output("nb-summary-output", "children"),
    Input("nb-results-store", "data"),
    Input("nb-model-store", "data"),
)
def update_summary(results, model_config):
    """Display model summary."""
    if not results or not model_config:
        return dmc.Text("No model estimated yet. Go to Model tab to estimate.", c="dimmed")

    return dmc.Stack(
        [
            dmc.Title("Naive Bayes Classification", order=4),
            dmc.Divider(),
            dmc.Text(f"Dataset: {model_config['dataset']}", fw=500),
            dmc.Text(f"Response variable: {model_config['response']}", fw=500),
            dmc.Text(
                f"Explanatory variables: {', '.join(model_config['explanatory'])}",
                fw=500,
            ),
            dmc.Text(f"Type: {model_config['nb_type'].title()}", fw=500),
            dmc.Text(f"Smoothing: {model_config['smoothing']}", fw=500),
            dmc.Divider(),
            dmc.Title("Performance Metrics", order=5),
            dmc.Group(
                [
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text("Training Accuracy", size="sm", c="dimmed"),
                                    dmc.Title(f"{results['train_accuracy']:.3f}", order=3),
                                ],
                                gap=0,
                                align="center",
                            )
                        ],
                        withBorder=True,
                        p="md",
                    ),
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text("Test Accuracy", size="sm", c="dimmed"),
                                    dmc.Title(f"{results['test_accuracy']:.3f}", order=3),
                                ],
                                gap=0,
                                align="center",
                            )
                        ],
                        withBorder=True,
                        p="md",
                    ),
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text("Training N", size="sm", c="dimmed"),
                                    dmc.Title(str(results["n_train"]), order=3),
                                ],
                                gap=0,
                                align="center",
                            )
                        ],
                        withBorder=True,
                        p="md",
                    ),
                    dmc.Card(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text("Test N", size="sm", c="dimmed"),
                                    dmc.Title(str(results["n_test"]), order=3),
                                ],
                                gap=0,
                                align="center",
                            )
                        ],
                        withBorder=True,
                        p="md",
                    ),
                ],
                grow=True,
            ),
        ],
        gap="md",
    )


@callback(
    Output("nb-plot", "figure"),
    Input("nb-plot-type", "value"),
    Input("nb-results-store", "data"),
)
def update_plot(plot_type, results):
    """Update diagnostic plots."""
    if not results:
        return go.Figure().add_annotation(
            text="No model estimated yet",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    if plot_type == "confusion":
        cm = np.array(results["confusion_matrix"])
        classes = results["classes"]

        fig = go.Figure(
            data=go.Heatmap(
                z=cm,
                x=classes,
                y=classes,
                colorscale="Blues",
                text=cm,
                texttemplate="%{text}",
                textfont={"size": 16},
            )
        )

        fig.update_layout(
            title="Confusion Matrix",
            xaxis_title="Predicted",
            yaxis_title="Actual",
            height=600,
        )

    elif plot_type == "importance":
        fig = go.Figure().add_annotation(
            text="Feature importance not available for Naive Bayes",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    else:  # ROC curve
        fig = go.Figure().add_annotation(
            text="ROC curve available for binary classification only",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    return fig


@callback(
    Output("nb-predictions-output", "children"),
    Input("nb-predict-btn", "n_clicks"),
    State("nb-pred-dataset", "value"),
    State("nb-pred-name", "value"),
    State("nb-model-store", "data"),
    prevent_initial_call=True,
)
def generate_predictions(n_clicks, pred_dataset, pred_name, model_config):
    """Generate predictions on new data."""
    if not model_config:
        return dmc.Alert("No model available. Estimate a model first.", color="red")

    return dmc.Alert("Predictions functionality coming soon", color="blue")
