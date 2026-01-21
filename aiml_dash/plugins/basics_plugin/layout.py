"""Layout module for basics plugin.

This module provides layout functions for all basics plugin pages.
Each layout function creates the UI structure for a specific statistical analysis page.

All layouts have been extracted from pages/basics/ and refactored into this plugin module.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
from components.common import create_page_header
from dash import dcc, html
from dash.development.base_component import Component
from dash_iconify import DashIconify


def single_mean_layout():
    """Create the single mean test page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Single Mean",
                "One-sample t-test to compare a sample mean against a hypothesized population value.",
                icon="carbon:chart-average",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Test Settings", order=4),
                                        dmc.Select(
                                            id="smean-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="smean-variable",
                                            label="Variable",
                                            placeholder="Select variable...",
                                            data=[],
                                        ),
                                        dmc.NumberInput(
                                            id="smean-comparison",
                                            label="Comparison Value",
                                            description="Hypothesized population mean",
                                            value=0,
                                            step=0.1,
                                        ),
                                        dmc.Select(
                                            id="smean-alternative",
                                            label="Alternative Hypothesis",
                                            value="two-sided",
                                            data=[
                                                {
                                                    "label": "Two-sided (≠)",
                                                    "value": "two-sided",
                                                },
                                                {
                                                    "label": "Greater than (>)",
                                                    "value": "greater",
                                                },
                                                {
                                                    "label": "Less than (<)",
                                                    "value": "less",
                                                },
                                            ],
                                        ),
                                        dmc.NumberInput(
                                            id="smean-confidence",
                                            label="Confidence Level",
                                            value=0.95,
                                            min=0.5,
                                            max=0.99,
                                            step=0.01,
                                            decimalScale=2,
                                        ),
                                        dmc.Button(
                                            "Run Test",
                                            id="smean-run-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
                                        ),
                                        dmc.Divider(),
                                        dmc.Button(
                                            "Export Results (CSV)",
                                            id="smean-export-btn",
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
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Plot",
                                        value="plot",
                                        leftSection=DashIconify(icon="carbon:chart-histogram"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="smean-summary"),
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
                                                dcc.Graph(id="smean-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="plot",
                                ),
                            ],
                            value="summary",
                            id="smean-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden components
            dcc.Store(id="smean-results-store"),
            dcc.Download(id="smean-download"),
            html.Div(id="smean-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks

def compare_means_layout() -> Component:
    """Create the compare means test page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Compare Means",
                "Two-sample t-test to compare means between two independent groups.",
                icon="carbon:compare",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Test Settings", order=4),
                                        dmc.Select(
                                            id="cmean-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="cmean-variable",
                                            label="Numeric Variable",
                                            placeholder="Select variable...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="cmean-group",
                                            label="Grouping Variable",
                                            placeholder="Select group variable...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="cmean-alternative",
                                            label="Alternative Hypothesis",
                                            value="two-sided",
                                            data=[
                                                {
                                                    "label": "Two-sided (≠)",
                                                    "value": "two-sided",
                                                },
                                                {
                                                    "label": "Greater than (>)",
                                                    "value": "greater",
                                                },
                                                {
                                                    "label": "Less than (<)",
                                                    "value": "less",
                                                },
                                            ],
                                        ),
                                        dmc.Switch(
                                            id="cmean-equal-var",
                                            label="Assume Equal Variances",
                                            description="Use pooled variance estimate",
                                            checked=True,
                                        ),
                                        dmc.NumberInput(
                                            id="cmean-confidence",
                                            label="Confidence Level",
                                            value=0.95,
                                            min=0.5,
                                            max=0.99,
                                            step=0.01,
                                            decimalScale=2,
                                        ),
                                        dmc.Button(
                                            "Run Test",
                                            id="cmean-run-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
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
                                        "Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Plot",
                                        value="plot",
                                        leftSection=DashIconify(icon="carbon:chart-box-plot"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="cmean-summary"),
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
                                                dcc.Graph(id="cmean-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="plot",
                                ),
                            ],
                            value="summary",
                            id="cmean-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="cmean-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks

def single_prop_layout():
    """Create layout for single proportion test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:percent", width=32),
                            dmc.Title("Single Proportion Test", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Test whether a sample proportion differs significantly from a hypothesized value",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Data Selection", fw=500, size="lg"),
                                            # Dataset selector
                                            dmc.Select(
                                                id="single-prop-dataset",
                                                label="Select Dataset",
                                                placeholder="Choose dataset...",
                                                data=[],
                                                searchable=True,
                                                clearable=False,
                                            ),
                                            # Variable selector
                                            dmc.Select(
                                                id="single-prop-variable",
                                                label="Variable",
                                                placeholder="Choose variable...",
                                                description="Select binary variable (0/1, TRUE/FALSE, Yes/No, etc.)",
                                                data=[],
                                                searchable=True,
                                            ),
                                            # Success level selector
                                            dmc.Select(
                                                id="single-prop-success",
                                                label="Success Level",
                                                placeholder="Choose success level...",
                                                description="Level representing 'success'",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Test Parameters", fw=500, size="lg"),
                                            # Comparison proportion
                                            dmc.NumberInput(
                                                id="single-prop-p0",
                                                label="Comparison Proportion (p₀)",
                                                description="Hypothesized population proportion",
                                                value=0.5,
                                                min=0,
                                                max=1,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            # Alternative hypothesis
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text(
                                                        "Alternative Hypothesis",
                                                        size="sm",
                                                        fw=500,
                                                    ),
                                                    dmc.SegmentedControl(
                                                        id="single-prop-alternative",
                                                        data=[
                                                            {
                                                                "label": "Two-sided",
                                                                "value": "two-sided",
                                                            },
                                                            {
                                                                "label": "Greater",
                                                                "value": "greater",
                                                            },
                                                            {
                                                                "label": "Less",
                                                                "value": "less",
                                                            },
                                                        ],
                                                        value="two-sided",
                                                        fullWidth=True,
                                                    ),
                                                ],
                                            ),
                                            # Confidence level
                                            dmc.NumberInput(
                                                id="single-prop-confidence",
                                                label="Confidence Level",
                                                description="For confidence interval",
                                                value=0.95,
                                                min=0.5,
                                                max=0.999,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            # Run test button
                                            dmc.Button(
                                                "Run Test",
                                                id="single-prop-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    # Results summary
                                    dmc.Paper(
                                        id="single-prop-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Configure test parameters and click 'Run Test' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    # Visualization
                                    dmc.Paper(
                                        id="single-prop-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="single-prop-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



def compare_props_layout():
    """Create layout for compare proportions test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:percent-box-outline", width=32),
                            dmc.Title("Compare Proportions Test", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Test whether proportions differ significantly between two independent groups",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Data Selection", fw=500, size="lg"),
                                            dmc.Select(
                                                id="compare-props-dataset",
                                                label="Select Dataset",
                                                placeholder="Choose dataset...",
                                                data=[],
                                                searchable=True,
                                                clearable=False,
                                            ),
                                            dmc.Select(
                                                id="compare-props-variable",
                                                label="Variable",
                                                placeholder="Choose variable...",
                                                description="Binary variable to test",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Select(
                                                id="compare-props-success",
                                                label="Success Level",
                                                placeholder="Choose success level...",
                                                description="Level representing 'success'",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Select(
                                                id="compare-props-group",
                                                label="Group Variable",
                                                placeholder="Choose grouping variable...",
                                                description="Variable with exactly 2 groups",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Test Parameters", fw=500, size="lg"),
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text(
                                                        "Alternative Hypothesis",
                                                        size="sm",
                                                        fw=500,
                                                    ),
                                                    dmc.SegmentedControl(
                                                        id="compare-props-alternative",
                                                        data=[
                                                            {
                                                                "label": "Two-sided",
                                                                "value": "two-sided",
                                                            },
                                                            {
                                                                "label": "Greater",
                                                                "value": "greater",
                                                            },
                                                            {
                                                                "label": "Less",
                                                                "value": "less",
                                                            },
                                                        ],
                                                        value="two-sided",
                                                        fullWidth=True,
                                                    ),
                                                ],
                                            ),
                                            dmc.NumberInput(
                                                id="compare-props-confidence",
                                                label="Confidence Level",
                                                description="For confidence interval",
                                                value=0.95,
                                                min=0.5,
                                                max=0.999,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            dmc.Button(
                                                "Run Test",
                                                id="compare-props-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="compare-props-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Configure test parameters and click 'Run Test' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="compare-props-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="compare-props-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



def correlation_layout():
    """Create the correlation analysis page layout.

    Returns:
        Container with correlation settings and output area.
    """
    return dmc.Container(
        [
            create_page_header(
                "Correlation",
                "Correlation matrix and significance tests",
                icon="carbon:connection-signal",
            ),
            dmc.Grid([
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Settings", order=4),
                                        dmc.Select(
                                            id="corr-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.MultiSelect(
                                            id="corr-variables",
                                            label="Variables",
                                            placeholder="Select variables...",
                                            data=[],
                                            searchable=True,
                                        ),
                                        dmc.Select(
                                            id="corr-method",
                                            label="Method",
                                            value="pearson",
                                            data=[
                                                {
                                                    "label": "Pearson",
                                                    "value": "pearson",
                                                },
                                                {
                                                    "label": "Spearman",
                                                    "value": "spearman",
                                                },
                                                {
                                                    "label": "Kendall",
                                                    "value": "kendall",
                                                },
                                            ],
                                        ),
                                        dmc.Button(
                                            "Calculate",
                                            id="corr-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            color="blue",
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
                dmc.GridCol(
                    [
                        dmc.Card(
                            [html.Div(id="corr-output")],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            html.Div(id="corr-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )



def cross_tabs_layout():
    """Create layout for cross-tabs analysis page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:table-large", width=32),
                            dmc.Title("Cross-Tabs: Chi-Square Test", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Test for independence between two categorical variables",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Data Selection", fw=500, size="lg"),
                                            dmc.Select(
                                                id="crosstabs-dataset",
                                                label="Select Dataset",
                                                placeholder="Choose dataset...",
                                                data=[],
                                                searchable=True,
                                                clearable=False,
                                            ),
                                            dmc.Select(
                                                id="crosstabs-row-var",
                                                label="Row Variable",
                                                placeholder="Choose row variable...",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Select(
                                                id="crosstabs-col-var",
                                                label="Column Variable",
                                                placeholder="Choose column variable...",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Display Options", fw=500, size="lg"),
                                            dmc.Switch(
                                                id="crosstabs-show-percentages",
                                                label="Show percentages",
                                                checked=True,
                                            ),
                                            dmc.Switch(
                                                id="crosstabs-show-expected",
                                                label="Show expected frequencies",
                                                checked=False,
                                            ),
                                            dmc.NumberInput(
                                                id="crosstabs-confidence",
                                                label="Confidence Level",
                                                value=0.95,
                                                min=0.5,
                                                max=0.999,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            dmc.Button(
                                                "Run Analysis",
                                                id="crosstabs-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="crosstabs-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Select variables and click 'Run Analysis' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="crosstabs-table-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dmc.Text("Contingency Table", fw=500, mb="sm"),
                                            html.Div(id="crosstabs-table"),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="crosstabs-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="crosstabs-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



def goodness_layout():
    """Create layout for goodness of fit test page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:chart-bell-curve", width=32),
                            dmc.Title("Goodness of Fit Test", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Test whether observed frequencies match an expected distribution",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Data Selection", fw=500, size="lg"),
                                            dmc.Select(
                                                id="goodness-dataset",
                                                label="Select Dataset",
                                                placeholder="Choose dataset...",
                                                data=[],
                                                searchable=True,
                                                clearable=False,
                                            ),
                                            dmc.Select(
                                                id="goodness-variable",
                                                label="Variable",
                                                placeholder="Choose categorical variable...",
                                                data=[],
                                                searchable=True,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text(
                                                "Expected Distribution",
                                                fw=500,
                                                size="lg",
                                            ),
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text(
                                                        "Distribution Type",
                                                        size="sm",
                                                        fw=500,
                                                    ),
                                                    dmc.SegmentedControl(
                                                        id="goodness-dist-type",
                                                        data=[
                                                            {
                                                                "label": "Uniform",
                                                                "value": "uniform",
                                                            },
                                                            {
                                                                "label": "Custom",
                                                                "value": "custom",
                                                            },
                                                        ],
                                                        value="uniform",
                                                        fullWidth=True,
                                                    ),
                                                ],
                                            ),
                                            dmc.Textarea(
                                                id="goodness-expected-input",
                                                label="Custom Expected Proportions",
                                                description="Enter comma-separated proportions (e.g., 0.25,0.25,0.5)",
                                                placeholder="0.25,0.25,0.5",
                                                minRows=2,
                                                style={"display": "none"},
                                            ),
                                            dmc.NumberInput(
                                                id="goodness-confidence",
                                                label="Confidence Level",
                                                value=0.95,
                                                min=0.5,
                                                max=0.999,
                                                step=0.01,
                                                decimalScale=3,
                                            ),
                                            dmc.Button(
                                                "Run Test",
                                                id="goodness-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="goodness-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Select variable and click 'Run Test' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="goodness-table-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dmc.Text(
                                                "Observed vs Expected Frequencies",
                                                fw=500,
                                                mb="sm",
                                            ),
                                            html.Div(id="goodness-table"),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="goodness-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="goodness-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



def prob_calc_layout():
    """Create layout for probability calculator page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:calculator", width=32),
                            dmc.Title("Probability Calculator", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Calculate probabilities and critical values for various distributions",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text("Distribution", fw=500, size="lg"),
                                            dmc.Select(
                                                id="prob-distribution",
                                                label="Distribution Type",
                                                data=[
                                                    {
                                                        "label": "Normal",
                                                        "value": "normal",
                                                    },
                                                    {
                                                        "label": "t (Student's)",
                                                        "value": "t",
                                                    },
                                                    {
                                                        "label": "Chi-square (χ²)",
                                                        "value": "chi2",
                                                    },
                                                    {"label": "F", "value": "f"},
                                                    {
                                                        "label": "Binomial",
                                                        "value": "binomial",
                                                    },
                                                    {
                                                        "label": "Poisson",
                                                        "value": "poisson",
                                                    },
                                                ],
                                                value="normal",
                                                clearable=False,
                                            ),
                                            # Distribution parameters
                                            html.Div(id="prob-params-container"),
                                            dmc.Divider(),
                                            dmc.Text("Calculation", fw=500, size="lg"),
                                            dmc.Stack(
                                                gap=5,
                                                children=[
                                                    dmc.Text("Calculate", size="sm", fw=500),
                                                    dmc.SegmentedControl(
                                                        id="prob-calc-type",
                                                        data=[
                                                            {
                                                                "label": "Probability",
                                                                "value": "probability",
                                                            },
                                                            {
                                                                "label": "Critical Value",
                                                                "value": "critical",
                                                            },
                                                        ],
                                                        value="probability",
                                                        fullWidth=True,
                                                    ),
                                                ],
                                            ),
                                            html.Div(id="prob-input-container"),
                                            dmc.Button(
                                                "Calculate",
                                                id="prob-calculate",
                                                leftSection=DashIconify(icon="mdi:calculator"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="prob-results",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Select distribution and parameters, then click 'Calculate'",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="prob-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="prob-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



def clt_layout() -> Component:
    """Create layout for CLT simulation page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:chart-bell-curve-cumulative", width=32),
                            dmc.Title("Central Limit Theorem", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Visualize how sample means converge to a normal distribution",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text(
                                                "Population Distribution",
                                                fw=500,
                                                size="lg",
                                            ),
                                            dmc.Select(
                                                id="clt-distribution",
                                                label="Distribution Type",
                                                data=[
                                                    {
                                                        "label": "Uniform",
                                                        "value": "uniform",
                                                    },
                                                    {
                                                        "label": "Normal",
                                                        "value": "normal",
                                                    },
                                                    {
                                                        "label": "Exponential",
                                                        "value": "exponential",
                                                    },
                                                    {
                                                        "label": "Binomial",
                                                        "value": "binomial",
                                                    },
                                                    {
                                                        "label": "Poisson",
                                                        "value": "poisson",
                                                    },
                                                    {
                                                        "label": "Beta (Skewed)",
                                                        "value": "beta",
                                                    },
                                                ],
                                                value="uniform",
                                                clearable=False,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Sampling Parameters", fw=500, size="lg"),
                                            dmc.NumberInput(
                                                id="clt-sample-size",
                                                label="Sample Size (n)",
                                                description="Number of observations per sample",
                                                value=30,
                                                min=2,
                                                max=200,
                                                step=1,
                                            ),
                                            dmc.NumberInput(
                                                id="clt-num-samples",
                                                label="Number of Samples",
                                                description="How many samples to draw",
                                                value=1000,
                                                min=100,
                                                max=10000,
                                                step=100,
                                            ),
                                            dmc.NumberInput(
                                                id="clt-seed",
                                                label="Random Seed",
                                                description="For reproducibility (optional)",
                                                value=42,
                                                min=0,
                                                max=9999,
                                                step=1,
                                            ),
                                            dmc.Button(
                                                "Run Simulation",
                                                id="clt-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                            dmc.Divider(),
                                            dmc.Alert(
                                                title="About CLT",
                                                color="blue",
                                                icon=DashIconify(icon="mdi:information"),
                                                children=dmc.Text(
                                                    "The Central Limit Theorem states that the distribution of "
                                                    "sample means approaches a normal distribution as sample size increases, "
                                                    "regardless of the population distribution.",
                                                    size="sm",
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="clt-stats",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Set parameters and click 'Run Simulation' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="clt-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="clt-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================



__all__ = ['single_mean_layout', 'compare_means_layout', 'single_prop_layout', 'compare_props_layout', 'correlation_layout', 'cross_tabs_layout', 'goodness_layout', 'prob_calc_layout', 'clt_layout']
