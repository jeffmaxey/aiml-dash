"""Cross-Tabulation (Chi-Square) analysis callbacks.

This module is part of the basics plugin callback suite.
Callbacks are registered automatically via ``@callback`` decorators on import.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback
from dash_iconify import DashIconify
from scipy import stats

from aiml_dash.utils.data_manager import data_manager


@callback(
    Output("crosstabs-dataset", "data"),
    Input("crosstabs-dataset", "id"),
)
def update_cross_tabs_datasets(_):
    """Populate dataset dropdown.

    Parameters
    ----------
    _ : Any
        Value provided for this parameter."""
    datasets = data_manager.get_dataset_names()
    return [{"label": ds, "value": ds} for ds in datasets]


@callback(
    [
        Output("crosstabs-row-var", "data"),
        Output("crosstabs-row-var", "value"),
        Output("crosstabs-col-var", "data"),
        Output("crosstabs-col-var", "value"),
    ],
    Input("crosstabs-dataset", "value"),
)
def update_cross_tabs_variables(dataset):
    """Populate variable dropdowns.

    Parameters
    ----------
    dataset : Any
        Value provided for this parameter."""
    if not dataset:
        return [], None, [], None

    df = data_manager.get_dataset(dataset)
    columns = df.columns.tolist()
    options = [{"label": col, "value": col} for col in columns]

    return options, None, options, None


@callback(
    [
        Output("crosstabs-results", "children"),
        Output("crosstabs-table-container", "style"),
        Output("crosstabs-table", "children"),
        Output("crosstabs-plot-container", "style"),
        Output("crosstabs-plot", "figure"),
    ],
    Input("crosstabs-run", "n_clicks"),
    [
        State("crosstabs-dataset", "value"),
        State("crosstabs-row-var", "value"),
        State("crosstabs-col-var", "value"),
        State("crosstabs-show-percentages", "checked"),
        State("crosstabs-show-expected", "checked"),
        State("crosstabs-confidence", "value"),
    ],
    prevent_initial_call=True,
)
def run_crosstabs_analysis(
    n_clicks, dataset, row_var, col_var, show_pct, show_expected, confidence
):
    """Run chi-square test of independence.

    Parameters
    ----------
    n_clicks : Any
        Input value for ``n_clicks``.
    dataset : Any
        Input value for ``dataset``.
    row_var : Any
        Input value for ``row_var``.
    col_var : Any
        Input value for ``col_var``.
    show_pct : Any
        Input value for ``show_pct``.
    show_expected : Any
        Input value for ``show_expected``.
    confidence : Any
        Value provided for this parameter."""
    if not all([dataset, row_var, col_var]):
        return (
            [
                dmc.Alert(
                    "Please select dataset and both variables",
                    title="Missing inputs",
                    color="yellow",
                    icon=DashIconify(icon="mdi:alert"),
                )
            ],
            {"display": "none"},
            None,
            {"display": "none"},
            {},
        )

    try:
        df = data_manager.get_dataset(dataset)

        if row_var not in df.columns or col_var not in df.columns:
            return (
                [
                    dmc.Alert(
                        "Selected variables not found in dataset",
                        title="Error",
                        color="red",
                        icon=DashIconify(icon="mdi:alert-circle"),
                    )
                ],
                {"display": "none"},
                None,
                {"display": "none"},
                {},
            )

        # Create contingency table
        contingency_table = pd.crosstab(df[row_var], df[col_var])

        # Run chi-square test
        chi2, p_value, dof, _expected_freq = stats.chi2_contingency(contingency_table)

        # Calculate Cramér's V (effect size)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape[0], contingency_table.shape[1]) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        is_significant = p_value < (1 - confidence)

        # Create results display
        results_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            dmc.Text(
                                "Chi-Square Test of Independence", fw=600, size="lg"
                            ),
                            dmc.Badge(
                                "Significant" if is_significant else "Not Significant",
                                color="green" if is_significant else "gray",
                                variant="filled",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 4},
                        spacing="md",
                        children=[
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("χ² Statistic", size="xs", c="dimmed"),
                                    dmc.Text(f"{chi2:.4f}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("df", size="xs", c="dimmed"),
                                    dmc.Text(f"{dof}", fw=600, size="xl"),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("P-value", size="xs", c="dimmed"),
                                    dmc.Text(
                                        f"{p_value:.4f}",
                                        fw=600,
                                        size="xl",
                                        c="green" if is_significant else "gray",
                                    ),
                                ],
                            ),
                            dmc.Stack(
                                gap=4,
                                children=[
                                    dmc.Text("Cramér's V", size="xs", c="dimmed"),
                                    dmc.Text(f"{cramers_v:.4f}", fw=600, size="xl"),
                                ],
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Interpretation",
                        color="blue",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"There {'is' if is_significant else 'is no'} statistically significant association "
                            f"between {row_var} and {col_var} (χ² = {chi2:.2f}, df = {dof}, p = {p_value:.4f}). "
                            f"Cramér's V = {cramers_v:.3f} indicates a "
                            f"{'weak' if cramers_v < 0.3 else 'moderate' if cramers_v < 0.5 else 'strong'} "
                            f"effect size.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create contingency table display
        if show_pct:
            # Show percentages
            pct_table = contingency_table / contingency_table.sum().sum() * 100
            display_table = pct_table.round(2).astype(str) + "%"
        else:
            display_table = contingency_table.astype(str)

        # Add row and column totals
        display_df = display_table.copy()
        display_df["Total"] = contingency_table.sum(axis=1).astype(str)
        totals_row = pd.Series(
            [*contingency_table.sum(axis=0).astype(str).tolist(), str(n)],
            index=list(display_df.columns),
            name="Total",
        )
        display_df = pd.concat(
            [display_df, pd.DataFrame([totals_row])], ignore_index=False
        )

        # Create AG Grid
        display_df = display_df.reset_index()
        display_df.rename(columns={"index": row_var}, inplace=True)

        table_component = dag.AgGrid(
            rowData=display_df.to_dict("records"),
            columnDefs=[
                {"field": col, "headerName": col} for col in display_df.columns
            ],
            defaultColDef={"resizable": True, "sortable": True, "filter": False},
            style={"height": "300px"},
        )

        # Create grouped bar chart
        fig = go.Figure()

        for col in contingency_table.columns:
            fig.add_trace(
                go.Bar(
                    name=str(col),
                    x=contingency_table.index.astype(str),
                    y=contingency_table[col],
                    text=contingency_table[col],
                    textposition="auto",
                )
            )

        fig.update_layout(
            title=f"{row_var} by {col_var}",
            xaxis_title=row_var,
            yaxis_title="Count",
            barmode="group",
            template="plotly_white",
            height=400,
            legend={"title": col_var},
        )

        return (
            results_content,
            {"display": "block"},
            table_component,
            {"display": "block"},
            fig,
        )

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            None,
            {"display": "none"},
            {},
        )


