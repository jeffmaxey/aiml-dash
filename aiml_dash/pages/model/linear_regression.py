"""
Linear Regression (OLS) Page
=============================

Ordinary Least Squares regression for continuous outcomes.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from utils.data_manager import data_manager


def layout():
    """Create the linear regression page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Linear Regression (OLS)",
                "Estimate linear regression models using Ordinary Least Squares. Model continuous outcomes as a function of explanatory variables.",
                icon="carbon:chart-line",
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
                                                            id="lr-dataset",
                                                            label="Dataset",
                                                            data=[],
                                                            placeholder="Select dataset",
                                                        ),
                                                        dmc.Select(
                                                            id="lr-response",
                                                            label="Response variable",
                                                            description="Dependent variable (must be numeric)",
                                                            data=[],
                                                            placeholder="Select response variable",
                                                            searchable=True,
                                                        ),
                                                        dmc.MultiSelect(
                                                            id="lr-explanatory",
                                                            label="Explanatory variables",
                                                            description="Independent variables (predictors)",
                                                            data=[],
                                                            placeholder="Select explanatory variables",
                                                            searchable=True,
                                                        ),
                                                        dmc.CheckboxGroup(
                                                            id="lr-options",
                                                            label="Options",
                                                            children=[
                                                                dmc.Checkbox(
                                                                    label="Standardize",
                                                                    value="standardize",
                                                                ),
                                                                dmc.Checkbox(
                                                                    label="Center",
                                                                    value="center",
                                                                ),
                                                                dmc.Checkbox(
                                                                    label="Robust standard errors",
                                                                    value="robust",
                                                                ),
                                                            ],
                                                            value=[],
                                                        ),
                                                        dmc.Select(
                                                            id="lr-interactions",
                                                            label="Interactions",
                                                            description="Include interaction terms",
                                                            data=[
                                                                {
                                                                    "label": "None",
                                                                    "value": "none",
                                                                },
                                                                {
                                                                    "label": "2-way",
                                                                    "value": "2way",
                                                                },
                                                                {
                                                                    "label": "3-way",
                                                                    "value": "3way",
                                                                },
                                                            ],
                                                            value="none",
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                dmc.Button(
                                                                    "Estimate",
                                                                    id="lr-estimate-btn",
                                                                    leftSection=DashIconify(
                                                                        icon="carbon:play",
                                                                        width=20,
                                                                    ),
                                                                    color="blue",
                                                                    fullWidth=True,
                                                                ),
                                                                dmc.Button(
                                                                    "Store Model",
                                                                    id="lr-store-btn",
                                                                    leftSection=DashIconify(
                                                                        icon="carbon:save",
                                                                        width=20,
                                                                    ),
                                                                    variant="light",
                                                                    fullWidth=True,
                                                                ),
                                                            ],
                                                            grow=True,
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
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title("Model Formula", order=4),
                                                        dmc.Code(
                                                            id="lr-formula",
                                                            block=True,
                                                            children="response ~ explanatory",
                                                        ),
                                                    ],
                                                    gap="xs",
                                                )
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        ),
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title(
                                                            "Model Information",
                                                            order=4,
                                                        ),
                                                        html.Div(id="lr-model-info"),
                                                    ],
                                                    gap="xs",
                                                )
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
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
                                    dmc.Stack(
                                        [
                                            dmc.Group(
                                                [
                                                    dmc.Title("Model Summary", order=4),
                                                    dmc.Group([
                                                        dmc.Checkbox(
                                                            label="RMSE",
                                                            value="rmse",
                                                            id="lr-sum-rmse",
                                                            checked=True,
                                                        ),
                                                        dmc.Checkbox(
                                                            label="VIF",
                                                            value="vif",
                                                            id="lr-sum-vif",
                                                        ),
                                                        dmc.Checkbox(
                                                            label="Confidence Intervals",
                                                            value="ci",
                                                            id="lr-sum-ci",
                                                        ),
                                                    ]),
                                                ],
                                                justify="space-between",
                                            ),
                                            html.Div(id="lr-summary-output"),
                                            dmc.Button(
                                                "Download Summary",
                                                id="lr-download-summary",
                                                leftSection=DashIconify(icon="carbon:download", width=20),
                                                variant="light",
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
                        value="summary",
                    ),
                    # Predict Tab
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
                                                            "Prediction Settings",
                                                            order=4,
                                                        ),
                                                        dmc.RadioGroup(
                                                            id="lr-pred-type",
                                                            label="Prediction input",
                                                            children=[
                                                                dmc.Radio(
                                                                    label="None",
                                                                    value="none",
                                                                ),
                                                                dmc.Radio(
                                                                    label="Data",
                                                                    value="data",
                                                                ),
                                                                dmc.Radio(
                                                                    label="Command",
                                                                    value="cmd",
                                                                ),
                                                            ],
                                                            value="none",
                                                        ),
                                                        dmc.Select(
                                                            id="lr-pred-dataset",
                                                            label="Prediction dataset",
                                                            data=[],
                                                            placeholder="Select dataset",
                                                        ),
                                                        dmc.Textarea(
                                                            id="lr-pred-cmd",
                                                            label="Prediction command",
                                                            description="Format: var1=value1; var2=value2",
                                                            placeholder="price=100; age=25",
                                                            minRows=3,
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                dmc.Button(
                                                                    "Generate Predictions",
                                                                    id="lr-predict-btn",
                                                                    leftSection=DashIconify(
                                                                        icon="carbon:chart-bubble",
                                                                        width=20,
                                                                    ),
                                                                    color="green",
                                                                    fullWidth=True,
                                                                ),
                                                                dmc.Button(
                                                                    "Save Predictions",
                                                                    id="lr-save-pred-btn",
                                                                    leftSection=DashIconify(
                                                                        icon="carbon:save",
                                                                        width=20,
                                                                    ),
                                                                    variant="light",
                                                                    fullWidth=True,
                                                                ),
                                                            ],
                                                            grow=True,
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
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title("Predictions", order=4),
                                                        html.Div(id="lr-predictions-output"),
                                                    ],
                                                    gap="xs",
                                                )
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 8},
                                ),
                            ]),
                        ],
                        value="predict",
                    ),
                    # Plot Tab
                    dmc.TabsPanel(
                        [
                            dmc.Grid([
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title("Plot Settings", order=4),
                                                        dmc.Select(
                                                            id="lr-plot-type",
                                                            label="Plot type",
                                                            data=[
                                                                {
                                                                    "label": "Residuals vs Fitted",
                                                                    "value": "resid_fitted",
                                                                },
                                                                {
                                                                    "label": "Residuals vs Explanatory",
                                                                    "value": "resid_pred",
                                                                },
                                                                {
                                                                    "label": "Q-Q Plot",
                                                                    "value": "qq",
                                                                },
                                                                {
                                                                    "label": "Scale-Location",
                                                                    "value": "scale_location",
                                                                },
                                                                {
                                                                    "label": "Coefficient Plot",
                                                                    "value": "coef",
                                                                },
                                                                {
                                                                    "label": "Actual vs Predicted",
                                                                    "value": "actual_pred",
                                                                },
                                                                {
                                                                    "label": "Correlation Matrix",
                                                                    "value": "corr",
                                                                },
                                                            ],
                                                            value="resid_fitted",
                                                        ),
                                                        dmc.NumberInput(
                                                            id="lr-plot-nobs",
                                                            label="Number of observations",
                                                            description="For residual plots",
                                                            value=1000,
                                                            min=100,
                                                            max=10000,
                                                            step=100,
                                                        ),
                                                        dmc.Button(
                                                            "Generate Plot",
                                                            id="lr-plot-btn",
                                                            leftSection=DashIconify(
                                                                icon="carbon:chart-area",
                                                                width=20,
                                                            ),
                                                            color="blue",
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
                                    span={"base": 12, "md": 3},
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Card(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title("Visualization", order=4),
                                                        dcc.Graph(
                                                            id="lr-plot-output",
                                                            config={"displayModeBar": True},
                                                        ),
                                                    ],
                                                    gap="xs",
                                                )
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                        ),
                                    ],
                                    span={"base": 12, "md": 9},
                                ),
                            ]),
                        ],
                        value="plot",
                    ),
                ],
                value="model",
                id="lr-tabs",
            ),
            # Hidden components
            dcc.Store(id="lr-model-store"),
            dcc.Download(id="lr-download-summary-data"),
            html.Div(id="lr-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("lr-dataset", "data"),
    Input("lr-dataset", "id"),
)
def populate_datasets(_):
    """Populate dataset dropdown."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("lr-response", "data"),
        Output("lr-explanatory", "data"),
        Output("lr-pred-dataset", "data"),
    ],
    Input("lr-dataset", "value"),
)
def update_variable_lists(dataset_name):
    """Update variable dropdowns based on selected dataset."""
    if not dataset_name:
        return [], [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = df.columns.tolist()

        numeric_options = [{"label": col, "value": col} for col in numeric_cols]
        all_options = [{"label": col, "value": col} for col in all_cols]

        datasets = data_manager.get_dataset_names()
        dataset_options = [{"label": name, "value": name} for name in datasets]

        return numeric_options, all_options, dataset_options
    except Exception:
        return [], [], []


@callback(
    Output("lr-formula", "children"),
    [
        Input("lr-response", "value"),
        Input("lr-explanatory", "value"),
        Input("lr-interactions", "value"),
    ],
)
def update_formula(response, explanatory, interactions):
    """Update the model formula display."""
    if not response or not explanatory:
        return "response ~ explanatory"

    terms = list(explanatory)

    if interactions == "2way" and len(explanatory) > 1:
        for i in range(len(explanatory)):
            for j in range(i + 1, len(explanatory)):
                terms.append(f"{explanatory[i]}:{explanatory[j]}")
    elif interactions == "3way" and len(explanatory) > 2:
        for i in range(len(explanatory)):
            for j in range(i + 1, len(explanatory)):
                terms.append(f"{explanatory[i]}:{explanatory[j]}")
                for k in range(j + 1, len(explanatory)):
                    terms.append(f"{explanatory[i]}:{explanatory[j]}:{explanatory[k]}")

    formula = f"{response} ~ {' + '.join(terms)}"
    return formula


@callback(
    [
        Output("lr-model-store", "data"),
        Output("lr-model-info", "children"),
        Output("lr-notification", "children"),
    ],
    Input("lr-estimate-btn", "n_clicks"),
    [
        State("lr-dataset", "value"),
        State("lr-response", "value"),
        State("lr-explanatory", "value"),
        State("lr-options", "value"),
        State("lr-interactions", "value"),
    ],
    prevent_initial_call=True,
)
def estimate_model(n_clicks, dataset_name, response, explanatory, options, interactions):
    """Estimate the linear regression model."""
    if not all([dataset_name, response, explanatory]):
        return (
            None,
            dmc.Alert(
                "Please select dataset, response, and explanatory variables",
                color="red",
            ),
            None,
        )

    try:
        df = data_manager.get_dataset(dataset_name)

        # Prepare data
        X = df[explanatory].copy()
        y = df[response].copy()

        # Remove missing values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]

        # Add interactions
        if interactions != "none" and len(explanatory) > 1:
            interaction_cols = []
            if interactions == "2way":
                for i in range(len(explanatory)):
                    for j in range(i + 1, len(explanatory)):
                        col_name = f"{explanatory[i]}:{explanatory[j]}"
                        X[col_name] = X[explanatory[i]] * X[explanatory[j]]
                        interaction_cols.append(col_name)

        # Standardize or center
        if "standardize" in options:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        elif "center" in options:
            X = X - X.mean()

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Calculate metrics
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)
        n_obs = len(y)
        n_vars = X.shape[1]
        adj_r2 = 1 - (1 - r2) * (n_obs - 1) / (n_obs - n_vars - 1)

        # Store model data
        model_data = {
            "model": "linear_regression",
            "dataset": dataset_name,
            "response": response,
            "explanatory": list(X.columns),
            "coefficients": dict(
                zip(
                    ["intercept"] + list(X.columns),
                    [model.intercept_] + list(model.coef_),
                )
            ),
            "r2": r2,
            "adj_r2": adj_r2,
            "rmse": rmse,
            "mae": mae,
            "n_obs": n_obs,
            "n_vars": n_vars,
            "options": options,
        }

        # Create info display
        info = dmc.Stack(
            [
                dmc.Group([
                    dmc.Badge(f"R²: {r2:.4f}", color="blue"),
                    dmc.Badge(f"Adj. R²: {adj_r2:.4f}", color="cyan"),
                    dmc.Badge(f"RMSE: {rmse:.4f}", color="orange"),
                    dmc.Badge(f"n={n_obs}", color="gray"),
                ]),
                dmc.Text(
                    f"Model successfully estimated with {n_vars} variables",
                    size="sm",
                    c="dimmed",
                ),
            ],
            gap="xs",
        )

        notification = dmc.Notification(
            title="Success",
            message="Linear regression model estimated successfully",
            color="green",
            action="show",
            autoClose=3000,
        )

        return model_data, info, notification

    except Exception as e:
        return None, dmc.Alert(f"Error: {e!s}", color="red"), None


@callback(
    Output("lr-summary-output", "children"),
    [
        Input("lr-model-store", "data"),
        Input("lr-sum-rmse", "checked"),
        Input("lr-sum-vif", "checked"),
        Input("lr-sum-ci", "checked"),
    ],
)
def update_summary(model_data, show_rmse, show_vif, show_ci):
    """Update the summary display."""
    if not model_data:
        return dmc.Alert("No model estimated yet. Go to Model tab to estimate.", color="yellow")

    # Create coefficient table
    coef_data = []
    for var, coef in model_data["coefficients"].items():
        coef_data.append({"Variable": var, "Coefficient": f"{coef:.6f}"})

    coef_df = pd.DataFrame(coef_data)

    summary_parts = [
        dmc.Group([
            dmc.Badge(f"R² = {model_data['r2']:.4f}", color="blue", size="lg"),
            dmc.Badge(f"Adj. R² = {model_data['adj_r2']:.4f}", color="cyan", size="lg"),
            dmc.Badge(f"n = {model_data['n_obs']}", color="gray", size="lg"),
        ]),
        dmc.Space(h="md"),
        dmc.Text("Coefficients", fw=500, size="lg"),
        dag.AgGrid(
            rowData=coef_df.to_dict("records"),
            columnDefs=[{"field": col} for col in coef_df.columns],
            defaultColDef={"sortable": True, "filter": True, "resizable": True},
            dashGridOptions={"pagination": False},
            style={"height": "400px"},
        ),
    ]

    if show_rmse:
        summary_parts.extend([
            dmc.Space(h="md"),
            dmc.Alert(
                f"RMSE: {model_data['rmse']:.6f}",
                title="Root Mean Squared Error",
                color="blue",
            ),
        ])

    return dmc.Stack(summary_parts, gap="sm")


@callback(
    Output("lr-predictions-output", "children"),
    Input("lr-predict-btn", "n_clicks"),
    [
        State("lr-model-store", "data"),
        State("lr-pred-type", "value"),
        State("lr-pred-dataset", "value"),
        State("lr-pred-cmd", "value"),
    ],
    prevent_initial_call=True,
)
def generate_predictions(n_clicks, model_data, pred_type, pred_dataset, pred_cmd):
    """Generate predictions from the model."""
    if not model_data:
        return dmc.Alert("No model estimated yet", color="yellow")

    if pred_type == "none":
        return dmc.Alert("Select a prediction input method", color="yellow")

    try:
        if pred_type == "data":
            if not pred_dataset:
                return dmc.Alert("Select a prediction dataset", color="red")

            pred_df = data_manager.get_dataset(pred_dataset)
            X_pred = pred_df[model_data["explanatory"]]

            # Simple prediction (would need to recreate model)
            return dmc.Alert("Prediction from dataset completed (placeholder)", color="green")

        elif pred_type == "cmd":
            if not pred_cmd:
                return dmc.Alert("Enter prediction command", color="red")

            # Parse command: var1=val1; var2=val2
            pred_values = {}
            for pair in pred_cmd.split(";"):
                if "=" in pair:
                    var, val = pair.split("=")
                    pred_values[var.strip()] = float(val.strip())

            return dmc.Stack([
                dmc.Text("Prediction from command:", fw=500),
                dmc.Code(str(pred_values), block=True),
                dmc.Alert("Prediction calculation: (placeholder)", color="blue"),
            ])

    except Exception as e:
        return dmc.Alert(f"Error: {e!s}", color="red")


@callback(
    Output("lr-plot-output", "figure"),
    Input("lr-plot-btn", "n_clicks"),
    [
        State("lr-model-store", "data"),
        State("lr-dataset", "value"),
        State("lr-plot-type", "value"),
        State("lr-plot-nobs", "value"),
    ],
    prevent_initial_call=True,
)
def generate_plot(n_clicks, model_data, dataset_name, plot_type, nobs):
    """Generate diagnostic plots."""
    if not model_data or not dataset_name:
        return go.Figure()

    try:
        df = data_manager.get_dataset(dataset_name)
        X = df[model_data["explanatory"]]
        y = df[model_data["response"]]

        # Remove missing values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask].iloc[:nobs]
        y = y[mask].iloc[:nobs]

        # Refit model for plotting
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        residuals = y - y_pred

        if plot_type == "resid_fitted":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=y_pred,
                    y=residuals,
                    mode="markers",
                    marker=dict(color="blue", opacity=0.6),
                    name="Residuals",
                )
            )
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.update_layout(
                title="Residuals vs Fitted Values",
                xaxis_title="Fitted Values",
                yaxis_title="Residuals",
                template="plotly_white",
            )

        elif plot_type == "actual_pred":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=y,
                    y=y_pred,
                    mode="markers",
                    marker=dict(color="blue", opacity=0.6),
                    name="Predictions",
                )
            )
            min_val, max_val = min(y.min(), y_pred.min()), max(y.max(), y_pred.max())
            fig.add_trace(
                go.Scatter(
                    x=[min_val, max_val],
                    y=[min_val, max_val],
                    mode="lines",
                    line=dict(color="red", dash="dash"),
                    name="Perfect Fit",
                )
            )
            fig.update_layout(
                title="Actual vs Predicted Values",
                xaxis_title="Actual",
                yaxis_title="Predicted",
                template="plotly_white",
            )

        elif plot_type == "coef":
            coef_names = list(model_data["coefficients"].keys())[1:]  # Skip intercept
            coef_values = list(model_data["coefficients"].values())[1:]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=coef_values,
                    y=coef_names,
                    orientation="h",
                    marker=dict(color="blue"),
                )
            )
            fig.update_layout(
                title="Coefficient Plot",
                xaxis_title="Coefficient Value",
                yaxis_title="Variable",
                template="plotly_white",
            )

        else:
            fig = go.Figure()
            fig.add_annotation(
                text="Plot type not yet implemented",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {e!s}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig
