"""
Neural Network Page
===================

Multi-layer perceptron neural network for classification and regression.
"""

import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.metrics import accuracy_score, r2_score
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler
from utils.data_manager import data_manager


def layout():
    """Create the neural network page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Neural Network",
                "Multi-layer perceptron neural network. Flexible non-linear models for classification and regression tasks.",
                icon="carbon:network-3",
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
                            "Plot",
                            value="plot",
                            leftSection=DashIconify(icon="carbon:chart-line", width=16),
                        ),
                    ]),
                    # Model Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title(
                                                            "Model Configuration",
                                                            order=4,
                                                        ),
                                                        dmc.Select(
                                                            id="nn-dataset",
                                                            label="Dataset",
                                                            placeholder="Select dataset...",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="nn-response",
                                                            label="Response variable",
                                                            placeholder="Select response variable...",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.MultiSelect(
                                                            id="nn-explanatory",
                                                            label="Explanatory variables",
                                                            placeholder="Select explanatory variables...",
                                                            data=[],
                                                            searchable=True,
                                                        ),
                                                        dmc.Select(
                                                            id="nn-type",
                                                            label="Model type",
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
                                                        dmc.TextInput(
                                                            id="nn-hidden-layers",
                                                            label="Hidden layer sizes",
                                                            description="Comma-separated (e.g., 100,50,25)",
                                                            value="100,50",
                                                        ),
                                                        dmc.Select(
                                                            id="nn-activation",
                                                            label="Activation function",
                                                            data=[
                                                                {
                                                                    "label": "ReLU",
                                                                    "value": "relu",
                                                                },
                                                                {
                                                                    "label": "Tanh",
                                                                    "value": "tanh",
                                                                },
                                                                {
                                                                    "label": "Logistic",
                                                                    "value": "logistic",
                                                                },
                                                            ],
                                                            value="relu",
                                                        ),
                                                        dmc.NumberInput(
                                                            id="nn-learning-rate",
                                                            label="Learning rate",
                                                            value=0.001,
                                                            min=0.0001,
                                                            max=1,
                                                            step=0.0001,
                                                        ),
                                                        dmc.NumberInput(
                                                            id="nn-max-iter",
                                                            label="Maximum iterations",
                                                            value=200,
                                                            min=10,
                                                            max=1000,
                                                            step=10,
                                                        ),
                                                        dmc.NumberInput(
                                                            id="nn-seed",
                                                            label="Random seed",
                                                            value=1234,
                                                            min=0,
                                                        ),
                                                        dmc.Button(
                                                            "Train Network",
                                                            id="nn-train-btn",
                                                            leftSection=DashIconify(
                                                                icon="carbon:play",
                                                                width=20,
                                                            ),
                                                            fullWidth=True,
                                                            size="lg",
                                                            color="blue",
                                                        ),
                                                    ],
                                                    gap="sm",
                                                )
                                            ],
                                            withBorder=True,
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 4},
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Title("Training Status", order=4),
                                                html.Div(id="nn-status"),
                                            ],
                                            withBorder=True,
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 8},
                                ),
                            ]),
                        ],
                        value="model",
                    ),
                    # Summary Tab
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [
                                    html.Div(id="nn-summary"),
                                ],
                                withBorder=True,
                                p="md",
                            ),
                        ],
                        value="summary",
                    ),
                    # Plot Tab
                    dmc.TabsPanel(
                        [
                            dmc.Card(
                                [
                                    dmc.Stack(
                                        [
                                            dmc.SegmentedControl(
                                                id="nn-plot-type",
                                                data=[
                                                    {
                                                        "label": "Loss Curve",
                                                        "value": "loss",
                                                    },
                                                    {
                                                        "label": "Performance",
                                                        "value": "performance",
                                                    },
                                                ],
                                                value="loss",
                                                fullWidth=True,
                                            ),
                                            dcc.Graph(id="nn-plot", style={"height": "600px"}),
                                        ],
                                        gap="md",
                                    )
                                ],
                                withBorder=True,
                                p="md",
                            ),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="nn-tabs",
            ),
            dcc.Store(id="nn-model-store"),
            dcc.Store(id="nn-results-store"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


@callback(
    Output("nn-dataset", "data"),
    Input("nn-tabs", "value"),
)
def update_datasets(_):
    """Populate dataset dropdown with available datasets.

    Returns:
        List of dataset options for dropdown.
    """
    return [{"label": name, "value": name} for name in data_manager.get_dataset_names()]


@callback(
    Output("nn-response", "data"),
    Output("nn-explanatory", "data"),
    Input("nn-dataset", "value"),
)
def update_variables(dataset_name):
    """Update variable lists based on selected dataset.

    Args:
        dataset_name: Name of the selected dataset.

    Returns:
        Tuple of (response_options, explanatory_options).
    """
    if not dataset_name:
        return [], []
    df = data_manager.get_dataset(dataset_name)
    if df is None:
        return [], []
    vars_list = [{"label": col, "value": col} for col in df.columns]
    return vars_list, vars_list


@callback(
    Output("nn-model-store", "data"),
    Output("nn-results-store", "data"),
    Output("nn-status", "children"),
    Input("nn-train-btn", "n_clicks"),
    State("nn-dataset", "value"),
    State("nn-response", "value"),
    State("nn-explanatory", "value"),
    State("nn-type", "value"),
    State("nn-hidden-layers", "value"),
    State("nn-activation", "value"),
    State("nn-learning-rate", "value"),
    State("nn-max-iter", "value"),
    State("nn-seed", "value"),
    prevent_initial_call=True,
)
def train_network(
    n_clicks,
    dataset,
    response,
    explanatory,
    nn_type,
    hidden_layers,
    activation,
    lr,
    max_iter,
    seed,
):
    """Train a neural network model.

    Args:
        n_clicks: Number of button clicks.
        dataset: Name of the dataset to use.
        response: Response variable name.
        explanatory: List of explanatory variable names.
        nn_type: Type of problem (regression or classification).
        hidden_layers: Number of hidden layers.
        activation: Activation function.
        lr: Learning rate for optimization.
        max_iter: Maximum number of iterations.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (model_config, results, status_message).
    """
    if not all([dataset, response, explanatory]):
        return None, None, dmc.Alert("Please select all required fields", color="red")

    try:
        df = data_manager.get_dataset(dataset)
        X = df[explanatory].select_dtypes(include=[np.number]).fillna(0)
        y = df[response]

        # Parse hidden layers
        layers = tuple(int(x.strip()) for x in hidden_layers.split(","))

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train model
        if nn_type == "classification":
            model = MLPClassifier(
                hidden_layer_sizes=layers,
                activation=activation,
                learning_rate_init=lr,
                max_iter=max_iter,
                random_state=seed,
            )
        else:
            model = MLPRegressor(
                hidden_layer_sizes=layers,
                activation=activation,
                learning_rate_init=lr,
                max_iter=max_iter,
                random_state=seed,
            )

        model.fit(X_scaled, y)

        # Results
        if nn_type == "classification":
            score = accuracy_score(y, model.predict(X_scaled))
            metric_name = "Accuracy"
        else:
            score = r2_score(y, model.predict(X_scaled))
            metric_name = "R²"

        results = {
            "score": score,
            "metric": metric_name,
            "n_iter": model.n_iter_,
            "loss_curve": model.loss_curve_.tolist() if hasattr(model, "loss_curve_") else [],
        }

        status = dmc.Stack([
            dmc.Alert("Model trained successfully!", color="green"),
            dmc.Text(f"{metric_name}: {score:.3f}"),
            dmc.Text(f"Iterations: {model.n_iter_}"),
        ])

        return (
            {
                "dataset": dataset,
                "response": response,
                "explanatory": explanatory,
                "type": nn_type,
            },
            results,
            status,
        )

    except Exception as e:
        return None, None, dmc.Alert(f"Error: {e!s}", color="red")


@callback(
    Output("nn-summary", "children"),
    Input("nn-results-store", "data"),
    Input("nn-model-store", "data"),
)
def update_summary(results, model_config):
    """Update the model summary display.

    Args:
        results: Dictionary containing training results.
        model_config: Dictionary containing model configuration.

    Returns:
        Component with model summary or placeholder text.
    """
    if not results or not model_config:
        return dmc.Text("No model trained yet.", c="dimmed")

    return dmc.Stack(
        [
            dmc.Title("Neural Network Model", order=4),
            dmc.Text(f"Type: {model_config['type'].title()}"),
            dmc.Text(f"{results['metric']}: {results['score']:.3f}", fw=700, size="xl"),
            dmc.Text(f"Training iterations: {results['n_iter']}"),
        ],
        gap="md",
    )


@callback(
    Output("nn-plot", "figure"),
    Input("nn-plot-type", "value"),
    Input("nn-results-store", "data"),
)
def update_plot(plot_type, results):
    """Update the visualization plot.

    Args:
        plot_type: Type of plot to display.
        results: Dictionary containing training results.

    Returns:
        Plotly figure object.
    """
    if not results or not results.get("loss_curve"):
        return go.Figure().add_annotation(
            text="No model trained yet",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    if plot_type == "loss":
        fig = go.Figure(go.Scatter(y=results["loss_curve"], mode="lines", name="Training Loss"))
        fig.update_layout(
            title="Training Loss Curve",
            xaxis_title="Iteration",
            yaxis_title="Loss",
            height=600,
        )
    else:
        fig = go.Figure().add_annotation(
            text="Performance plot coming soon",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    return fig
