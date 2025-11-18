"""
Conjoint Analysis Page
======================

Perform conjoint analysis to measure consumer preferences for product attributes
and estimate part-worth utilities.
"""

from dash import html, dcc, Input, Output, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from itertools import combinations
import plotly.graph_objects as go

from components.common import create_page_header
from utils.data_manager import data_manager


def layout():
    """Create the conjoint analysis page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Conjoint Analysis",
                "Analyze consumer preferences for product attributes and estimate part-worth utilities using conjoint analysis.",
                icon="carbon:analytics",
            ),
            dmc.Grid([
                # Left panel - configuration
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Data Selection", order=4),
                                        dmc.Select(
                                            id="conjoint-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="conjoint-id-var",
                                            label="ID Variable (Optional)",
                                            description="Respondent or profile ID",
                                            placeholder="Select ID variable...",
                                            data=[],
                                            clearable=True,
                                        ),
                                        dmc.Select(
                                            id="conjoint-response",
                                            label="Response Variable",
                                            description="Rating or preference score",
                                            placeholder="Select response...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="conjoint-attributes",
                                            label="Product Attributes",
                                            description="Categorical attributes (factors)",
                                            placeholder="Select attributes...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Divider(
                                            label="Analysis Options",
                                            labelPosition="center",
                                        ),
                                        dmc.Text("Estimation Method", size="sm", fw=500),
                                        dmc.SegmentedControl(
                                            id="conjoint-method",
                                            data=[
                                                {
                                                    "label": "Part-Worth",
                                                    "value": "partworth",
                                                },
                                                {
                                                    "label": "Vector",
                                                    "value": "vector",
                                                },
                                            ],
                                            value="partworth",
                                        ),
                                        dmc.Switch(
                                            id="conjoint-interactions",
                                            label="Include Two-Way Interactions",
                                            description="Model attribute interactions",
                                            checked=False,
                                        ),
                                        dmc.Switch(
                                            id="conjoint-by-respondent",
                                            label="Individual-Level Analysis",
                                            description="Estimate utilities per respondent",
                                            checked=False,
                                        ),
                                        dmc.Button(
                                            "Run Analysis",
                                            id="conjoint-run-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
                                        ),
                                        dmc.Divider(),
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Export Options",
                                                    size="sm",
                                                    fw=500,
                                                ),
                                                dmc.Button(
                                                    "Download Utilities (CSV)",
                                                    id="conjoint-download-utils",
                                                    leftSection=DashIconify(
                                                        icon="carbon:download",
                                                        width=16,
                                                    ),
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm",
                                                ),
                                                dmc.Button(
                                                    "Download Importance (CSV)",
                                                    id="conjoint-download-importance",
                                                    leftSection=DashIconify(
                                                        icon="carbon:download",
                                                        width=16,
                                                    ),
                                                    variant="light",
                                                    fullWidth=True,
                                                    size="sm",
                                                ),
                                            ],
                                            gap="xs",
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
                                        "Part-Worths",
                                        value="partworths",
                                        leftSection=DashIconify(icon="carbon:chart-bar"),
                                    ),
                                    dmc.TabsTab(
                                        "Importance",
                                        value="importance",
                                        leftSection=DashIconify(icon="carbon:chart-pie"),
                                    ),
                                    dmc.TabsTab(
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Predictions",
                                        value="predictions",
                                        leftSection=DashIconify(icon="carbon:chart-line"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(
                                                    id="conjoint-partworths-plot",
                                                    style={"height": "600px"},
                                                ),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="partworths",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(
                                                    id="conjoint-importance-plot",
                                                    style={"height": "500px"},
                                                ),
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
                                                html.Div(id="conjoint-summary"),
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
                                                html.Div(id="conjoint-predictions"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="predictions",
                                ),
                            ],
                            value="partworths",
                            id="conjoint-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="conjoint-results-store"),
            dcc.Download(id="conjoint-download-utils-data"),
            dcc.Download(id="conjoint-download-importance-data"),
            html.Div(id="conjoint-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("conjoint-dataset", "data"),
    Input("conjoint-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("conjoint-id-var", "data"),
        Output("conjoint-response", "data"),
        Output("conjoint-attributes", "data"),
    ],
    Input("conjoint-dataset", "value"),
)
def update_variables(dataset_name):
    """Update available variables when dataset changes."""
    if not dataset_name:
        return [], [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        return all_cols, numeric_cols, all_cols
    except Exception:
        return [], [], []


@callback(
    [
        Output("conjoint-partworths-plot", "figure"),
        Output("conjoint-importance-plot", "figure"),
        Output("conjoint-summary", "children"),
        Output("conjoint-predictions", "children"),
        Output("conjoint-results-store", "data"),
        Output("conjoint-notification", "children"),
    ],
    Input("conjoint-run-btn", "n_clicks"),
    [
        State("conjoint-dataset", "value"),
        State("conjoint-id-var", "value"),
        State("conjoint-response", "value"),
        State("conjoint-attributes", "value"),
        State("conjoint-method", "value"),
        State("conjoint-interactions", "checked"),
        State("conjoint-by-respondent", "checked"),
    ],
    prevent_initial_call=True,
)
def run_conjoint_analysis(
    n_clicks,
    dataset_name,
    id_var,
    response_var,
    attributes,
    method,
    include_interactions,
    by_respondent,
):
    """Run conjoint analysis."""
    if not all([dataset_name, response_var, attributes]):
        return (
            {},
            {},
            dmc.Text("Please select dataset, response variable, and attributes.", c="red"),
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
        # Get data
        df = data_manager.get_dataset(dataset_name).copy()

        # Prepare data
        y = df[response_var]

        # Create dummy variables for categorical attributes
        X_dummies = pd.get_dummies(df[attributes], drop_first=True, prefix_sep="_")

        # Add interactions if requested
        if include_interactions and len(attributes) >= 2:
            for attr1, attr2 in combinations(attributes, 2):
                interaction_col = f"{attr1}_x_{attr2}"
                X_dummies[interaction_col] = df[attr1].astype(str) + "_" + df[attr2].astype(str)
                interaction_dummies = pd.get_dummies(
                    X_dummies[interaction_col], prefix=interaction_col, drop_first=True
                )
                X_dummies = pd.concat([X_dummies, interaction_dummies], axis=1)
                X_dummies = X_dummies.drop(interaction_col, axis=1)

        # Fit regression model
        model = LinearRegression()
        model.fit(X_dummies, y)

        # Get coefficients (part-worths)
        coefficients = pd.Series(model.coef_, index=X_dummies.columns)
        intercept = model.intercept_

        # Calculate R-squared
        y_pred = model.predict(X_dummies)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Calculate part-worths for each attribute level
        partworths = {}
        for attr in attributes:
            # Find columns related to this attribute
            attr_cols = [col for col in coefficients.index if col.startswith(f"{attr}_")]

            if attr_cols:
                # Get part-worths (include base level = 0)
                attr_partworths = {col.replace(f"{attr}_", ""): coefficients[col] for col in attr_cols}

                # Add base level
                levels = df[attr].unique()
                base_level = [lvl for lvl in levels if f"{attr}_{lvl}" not in X_dummies.columns]
                if base_level:
                    attr_partworths[str(base_level[0])] = 0.0

                partworths[attr] = attr_partworths

        # Calculate attribute importance
        importance = {}
        for attr, pw in partworths.items():
            if pw:
                importance[attr] = max(pw.values()) - min(pw.values())

        # Normalize importance to sum to 100
        total_importance = sum(importance.values())
        if total_importance > 0:
            importance_pct = {k: (v / total_importance) * 100 for k, v in importance.items()}
        else:
            importance_pct = {k: 0 for k in importance.keys()}

        # Create part-worths plot
        partworths_fig = go.Figure()

        for i, (attr, pw) in enumerate(partworths.items()):
            levels = list(pw.keys())
            values = list(pw.values())

            partworths_fig.add_trace(
                go.Bar(
                    name=attr,
                    x=levels,
                    y=values,
                    text=[f"{v:.3f}" for v in values],
                    textposition="auto",
                )
            )

        partworths_fig.update_layout(
            title="Part-Worth Utilities by Attribute",
            xaxis_title="Attribute Levels",
            yaxis_title="Part-Worth Utility",
            barmode="group",
            hovermode="x unified",
        )

        # Create importance plot
        importance_fig = go.Figure()

        importance_fig.add_trace(
            go.Pie(
                labels=list(importance_pct.keys()),
                values=list(importance_pct.values()),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Importance: %{value:.1f}%<extra></extra>",
            )
        )

        importance_fig.update_layout(
            title="Relative Attribute Importance",
        )

        # Summary statistics
        summary = dmc.Stack(
            [
                dmc.Text("Conjoint Analysis Summary", fw=600, size="lg"),
                dmc.Divider(),
                dmc.Text(f"Response Variable: {response_var}"),
                dmc.Text(f"Number of Attributes: {len(attributes)}"),
                dmc.Text(f"Number of Observations: {len(df)}"),
                dmc.Text(f"Method: {method.title()}"),
                dmc.Divider(),
                dmc.Text(f"R-squared: {r_squared:.4f}", fw=600, c="blue"),
                dmc.Text(f"Intercept: {intercept:.4f}"),
                dmc.Divider(),
                dmc.Text("Attribute Importance:", fw=600),
                *[
                    dmc.Text(f"{attr}: {imp:.1f}%")
                    for attr, imp in sorted(importance_pct.items(), key=lambda x: x[1], reverse=True)
                ],
            ],
            gap="xs",
        )

        # Create part-worths table
        partworths_data = []
        for attr, pw in partworths.items():
            for level, value in pw.items():
                partworths_data.append({
                    "Attribute": attr,
                    "Level": level,
                    "Part-Worth": f"{value:.4f}",
                })

        partworths_table = dag.AgGrid(
            rowData=partworths_data,
            columnDefs=[
                {"field": "Attribute", "flex": 1},
                {"field": "Level", "flex": 1},
                {"field": "Part-Worth", "flex": 1},
            ],
            defaultColDef={"sortable": True, "filter": True, "resizable": True},
            dashGridOptions={"pagination": True, "paginationPageSize": 20},
            style={"height": "500px"},
        )

        predictions_section = dmc.Stack(
            [
                dmc.Text("Model Fit", fw=600, size="lg"),
                dmc.Text(f"R-squared: {r_squared:.4f}"),
                dmc.Text(f"RMSE: {np.sqrt(ss_res / len(df)):.4f}"),
                dmc.Divider(),
                dmc.Text("Part-Worth Utilities:", fw=600),
                partworths_table,
            ],
            gap="md",
        )

        # Store results
        results = {
            "partworths": {k: list(v.items()) for k, v in partworths.items()},
            "importance": importance_pct,
            "r_squared": r_squared,
            "intercept": intercept,
        }

        return (
            partworths_fig,
            importance_fig,
            summary,
            predictions_section,
            results,
            dmc.Notification(
                title="Success",
                message=f"Conjoint analysis complete (R² = {r_squared:.3f})",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            {},
            {},
            dmc.Text(f"Error: {str(e)}", c="red"),
            "",
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("conjoint-download-utils-data", "data"),
    Input("conjoint-download-utils", "n_clicks"),
    State("conjoint-results-store", "data"),
    prevent_initial_call=True,
)
def download_utilities(n_clicks, results):
    """Download part-worth utilities as CSV."""
    if not results:
        return None

    try:
        partworths_data = []
        for attr, levels in results["partworths"].items():
            for level, value in levels:
                partworths_data.append({
                    "Attribute": attr,
                    "Level": level,
                    "PartWorth": value,
                })

        df = pd.DataFrame(partworths_data)
        return dcc.send_data_frame(df.to_csv, "conjoint_partworths.csv", index=False)
    except Exception:
        return None


@callback(
    Output("conjoint-download-importance-data", "data"),
    Input("conjoint-download-importance", "n_clicks"),
    State("conjoint-results-store", "data"),
    prevent_initial_call=True,
)
def download_importance(n_clicks, results):
    """Download attribute importance as CSV."""
    if not results:
        return None

    try:
        importance_df = pd.DataFrame(
            list(results["importance"].items()),
            columns=["Attribute", "Importance_Percent"],
        )
        return dcc.send_data_frame(importance_df.to_csv, "conjoint_importance.csv", index=False)
    except Exception:
        return None
