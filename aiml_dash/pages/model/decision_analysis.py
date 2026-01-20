"""
Decision Analysis Page
======================

Build and analyze decision trees for decision making under uncertainty.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify


def layout():
    """Create the decision analysis page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Decision Analysis",
                "Build decision trees to analyze choices under uncertainty. Calculate expected values and determine optimal decisions.",
                icon="carbon:decision-tree",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Decision Tree", order=4),
                                        dmc.Textarea(
                                            id="dtree-input",
                                            label="Decision Tree Specification",
                                            description="Enter decision tree in YAML-like format",
                                            placeholder="""name: Investment Decision
type: decision
branches:
  - name: Invest
    cost: 10000
    type: chance
    branches:
      - name: Success
        prob: 0.6
        payoff: 50000
      - name: Failure
        prob: 0.4
        payoff: -5000
  - name: Don't Invest
    payoff: 0""",
                                            minRows=15,
                                            autosize=True,
                                        ),
                                        dmc.Button(
                                            "Analyze Decision",
                                            id="dtree-analyze-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="green",
                                        ),
                                        dmc.Divider(),
                                        dmc.Button(
                                            "Load Example",
                                            id="dtree-example-btn",
                                            leftSection=DashIconify(icon="carbon:document", width=20),
                                            variant="light",
                                            fullWidth=True,
                                        ),
                                        dmc.Button(
                                            "Export Results (CSV)",
                                            id="dtree-export-btn",
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
                # Right panel
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Results",
                                        value="results",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Expected Values",
                                        value="ev",
                                        leftSection=DashIconify(icon="carbon:table"),
                                    ),
                                    dmc.TabsTab(
                                        "Sensitivity",
                                        value="sensitivity",
                                        leftSection=DashIconify(icon="carbon:chart-line"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="dtree-results"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="results",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="dtree-ev-table"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="ev",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="dtree-sensitivity-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="sensitivity",
                                ),
                            ],
                            value="results",
                            id="dtree-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden components
            dcc.Store(id="dtree-data-store"),
            dcc.Download(id="dtree-download"),
            html.Div(id="dtree-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Helper functions
def calculate_ev(node):
    """Calculate expected value recursively."""
    if "payoff" in node:
        return node["payoff"]

    if node.get("type") == "chance":
        ev = sum(branch.get("prob", 1) * calculate_ev(branch) for branch in node.get("branches", []))
        return ev - node.get("cost", 0)
    else:  # decision node
        evs = [calculate_ev(branch) for branch in node.get("branches", [])]
        return max(evs) if evs else 0


def find_optimal_path(node, path=""):
    """Find the optimal decision path."""
    if "payoff" in node:
        return [(path, node["payoff"])]

    if node.get("type") == "chance":
        results = []
        for branch in node.get("branches", []):
            branch_path = f"{path} → {branch['name']}"
            results.extend(find_optimal_path(branch, branch_path))
        return results
    else:  # decision node
        best_branch = None
        best_ev = float("-inf")

        for branch in node.get("branches", []):
            ev = calculate_ev(branch)
            if ev > best_ev:
                best_ev = ev
                best_branch = branch

        if best_branch:
            branch_path = f"{path} → {best_branch['name']}"
            return find_optimal_path(best_branch, branch_path)
        return []


# Callbacks
@callback(
    Output("dtree-input", "value"),
    Input("dtree-example-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_example(n_clicks):
    """Load example decision tree."""
    example = """name: Product Launch Decision
type: decision
branches:
  - name: Launch Product
    cost: 50000
    type: chance
    branches:
      - name: High Demand
        prob: 0.3
        payoff: 200000
      - name: Medium Demand
        prob: 0.5
        payoff: 100000
      - name: Low Demand
        prob: 0.2
        payoff: 20000
  - name: Market Test First
    cost: 10000
    type: chance
    branches:
      - name: Positive Test
        prob: 0.7
        type: decision
        branches:
          - name: Launch
            cost: 50000
            type: chance
            branches:
              - name: Success
                prob: 0.8
                payoff: 180000
              - name: Failure
                prob: 0.2
                payoff: 30000
          - name: Don't Launch
            payoff: 0
      - name: Negative Test
        prob: 0.3
        payoff: 0
  - name: Don't Launch
    payoff: 0"""
    return example


@callback(
    [
        Output("dtree-results", "children"),
        Output("dtree-ev-table", "children"),
        Output("dtree-sensitivity-plot", "figure"),
        Output("dtree-data-store", "data"),
        Output("dtree-notification", "children"),
    ],
    Input("dtree-analyze-btn", "n_clicks"),
    State("dtree-input", "value"),
    prevent_initial_call=True,
)
def analyze_decision(n_clicks, tree_spec):
    """Analyze decision tree."""
    if not tree_spec:
        return (
            dmc.Text("Please enter a decision tree specification.", c="red"),
            "",
            {},
            None,
            dmc.Notification(
                title="Error",
                message="Missing decision tree",
                color="red",
                action="show",
            ),
        )

    try:
        # Parse YAML-like specification
        import yaml

        tree = yaml.safe_load(tree_spec)

        # Calculate expected values for each branch
        if tree.get("type") == "decision":
            branch_evs = []
            for branch in tree.get("branches", []):
                ev = calculate_ev(branch)
                branch_evs.append({
                    "Decision": branch["name"],
                    "Expected Value": ev,
                })

            # Find optimal decision
            optimal_idx = np.argmax([b["Expected Value"] for b in branch_evs])
            optimal_decision = branch_evs[optimal_idx]["Decision"]
            optimal_ev = branch_evs[optimal_idx]["Expected Value"]

            # Results summary
            results = dmc.Stack(
                [
                    dmc.Text(f"Decision: {tree['name']}", fw=600, size="xl"),
                    dmc.Divider(),
                    dmc.Text(
                        f"Optimal Decision: {optimal_decision}",
                        c="green",
                        fw=700,
                        size="lg",
                    ),
                    dmc.Text(
                        f"Expected Value: ${optimal_ev:,.2f}",
                        c="blue",
                        fw=600,
                        size="lg",
                    ),
                    dmc.Divider(),
                    dmc.Text("All Options:", fw=600),
                    *[
                        dmc.Text(f"• {b['Decision']}: ${b['Expected Value']:,.2f}")
                        for b in sorted(branch_evs, key=lambda x: x["Expected Value"], reverse=True)
                    ],
                ],
                gap="xs",
            )

            # EV table
            ev_table = dag.AgGrid(
                rowData=branch_evs,
                columnDefs=[
                    {"field": "Decision", "flex": 1},
                    {
                        "field": "Expected Value",
                        "flex": 1,
                        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
                    },
                ],
                defaultColDef={"sortable": True},
                style={"height": "300px"},
            )

            # Sensitivity analysis (vary probabilities)
            sensitivity_fig = go.Figure()

            # For first branch with chance node, vary probabilities
            first_branch = tree["branches"][0]
            if first_branch.get("type") == "chance":
                chance_branches = first_branch.get("branches", [])
                if len(chance_branches) >= 2:
                    # Vary first probability
                    prob_range = np.linspace(0, 1, 50)
                    evs = []

                    for p in prob_range:
                        # Adjust probabilities proportionally
                        temp_branch = first_branch.copy()
                        temp_branches = [b.copy() for b in chance_branches]
                        temp_branches[0]["prob"] = p
                        remaining_prob = 1 - p
                        original_remaining = sum(b.get("prob", 0) for b in chance_branches[1:])

                        if original_remaining > 0:
                            for i in range(1, len(temp_branches)):
                                temp_branches[i]["prob"] = (
                                    chance_branches[i].get("prob", 0) * remaining_prob / original_remaining
                                )

                        temp_branch["branches"] = temp_branches
                        ev = calculate_ev(temp_branch)
                        evs.append(ev)

                    sensitivity_fig.add_trace(
                        go.Scatter(
                            x=prob_range,
                            y=evs,
                            mode="lines",
                            name=f"{first_branch['name']} - {chance_branches[0]['name']}",
                            line=dict(width=2),
                        )
                    )

                    sensitivity_fig.update_layout(
                        title="Sensitivity Analysis: EV vs Probability",
                        xaxis_title=f"Probability of {chance_branches[0]['name']}",
                        yaxis_title="Expected Value ($)",
                    )

            if not sensitivity_fig.data:
                sensitivity_fig.add_annotation(
                    text="Sensitivity analysis not available for this decision tree structure",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            return (
                results,
                ev_table,
                sensitivity_fig,
                {"tree": tree, "evs": branch_evs},
                dmc.Notification(
                    title="Success",
                    message="Decision analysis complete",
                    color="green",
                    action="show",
                ),
            )
        else:
            return (
                dmc.Text("Root node must be a decision node", c="red"),
                "",
                {},
                None,
                dmc.Notification(
                    title="Error",
                    message="Invalid tree structure",
                    color="red",
                    action="show",
                ),
            )

    except Exception as e:
        return (
            dmc.Text(f"Error parsing decision tree: {e!s}", c="red"),
            "",
            {},
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("dtree-download", "data"),
    Input("dtree-export-btn", "n_clicks"),
    State("dtree-data-store", "data"),
    prevent_initial_call=True,
)
def export_results(n_clicks, data):
    """Export decision analysis results."""
    if not data:
        return None

    try:
        df = pd.DataFrame(data["evs"])
        return dcc.send_data_frame(df.to_csv, "decision_analysis.csv", index=False)
    except Exception:
        return None
