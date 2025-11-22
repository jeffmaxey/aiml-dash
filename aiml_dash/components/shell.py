"""
App Shell Components
====================

Reusable components for the AIML Dash AppShell structure.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from aiml_dash.utils.constants import APP_TITLE, GITHUB_URL


theme_toggle = dmc.Switch(
    offLabel=DashIconify(icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]),
    onLabel=DashIconify(icon="radix-icons:moon", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][6]),
    id="docs-color-scheme-switch",
    persistence=True,
    color="gray",
    size="md",
)

rtl_toggle = dmc.Tooltip(
    dmc.ActionIcon(
        DashIconify(icon="tabler:text-direction-rtl", width=18, id="rtl-icon"),
        id="rtl-toggle",
        variant="light",
        color="gray",
        visibleFrom="sm",
    ),
    label="Text Direction",
)


def create_header():
    """
    Create application header for AppShellHeader.

    Returns
    -------
    dmc.Group
        Header content with branding, toggle buttons, and status
    """
    return dmc.Group(
        [
            dmc.Group(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="carbon:menu", width=20),
                        id="navbar-toggle",
                        variant="subtle",
                        size="lg",
                    ),
                    DashIconify(icon="carbon:analytics", width=32, height=32, color="#1971c2"),
                    dmc.Title(children=APP_TITLE, order=3),
                ],
                gap="xs",
            ),
            dmc.Group(
                [
                    rtl_toggle,
                    theme_toggle,
                    dmc.Text(id="active-dataset-display", size="sm", c="dimmed"),
                    dmc.Badge(
                        "Python Version",
                        color="blue",
                        variant="light",
                    ),
                    dmc.Menu([
                        dmc.MenuTarget(
                            dmc.ActionIcon(
                                DashIconify(icon="carbon:save", width=20),
                                variant="subtle",
                                size="lg",
                            )
                        ),
                        dmc.MenuDropdown([
                            dmc.MenuItem(
                                "Export State",
                                leftSection=DashIconify(icon="carbon:download", width=16),
                                id="export-state-btn",
                            ),
                            dmc.MenuItem(
                                "Import State",
                                leftSection=DashIconify(icon="carbon:upload", width=16),
                                id="import-state-btn",
                            ),
                        ]),
                    ]),
                    dmc.ActionIcon(
                        DashIconify(icon="carbon:side-panel-close", width=20),
                        id="aside-toggle",
                        variant="subtle",
                        size="lg",
                    ),
                ],
                gap="md",
            ),
        ],
        justify="space-between",
        style={"width": "100%"},
    )


def create_navigation():
    """
    Create navigation sidebar for AppShellNavbar.

    Returns
    -------
    dmc.Accordion
        Navigation links in collapsible sections
    """
    # Data pages
    data_items = [
        {"value": "manage", "label": "Manage", "icon": "carbon:data-table"},
        {"value": "view", "label": "View", "icon": "carbon:view"},
        {"value": "explore", "label": "Explore", "icon": "carbon:explore"},
        {"value": "transform", "label": "Transform", "icon": "carbon:settings-adjust"},
        {"value": "visualize", "label": "Visualize", "icon": "carbon:chart-scatter"},
        {"value": "pivot", "label": "Pivot", "icon": "carbon:data-reference"},
        {"value": "combine", "label": "Combine", "icon": "carbon:data-connected"},
        {"value": "report", "label": "Report", "icon": "carbon:document"},
    ]

    # Design pages
    design_items = [
        {"value": "doe", "label": "DOE", "icon": "carbon:chemistry"},
        {"value": "sampling", "label": "Sampling", "icon": "carbon:diagram-reference"},
        {"value": "sample_size", "label": "Sample Size", "icon": "carbon:calculator"},
        {
            "value": "sample_size_comp",
            "label": "Sample Size Comparison",
            "icon": "carbon:comparison",
        },
        {"value": "randomizer", "label": "Randomizer", "icon": "carbon:shuffle"},
    ]

    # Model pages
    model_estimate_items = [
        {
            "value": "linear-regression",
            "label": "Linear Regression",
            "icon": "carbon:chart-line",
        },
        {
            "value": "logistic-regression",
            "label": "Logistic Regression",
            "icon": "carbon:operations-record",
        },
        {
            "value": "multinomial-logit",
            "label": "Multinomial Logit",
            "icon": "carbon:flow",
        },
        {"value": "naive-bayes", "label": "Naive Bayes", "icon": "carbon:calculation"},
        {
            "value": "neural-network",
            "label": "Neural Network",
            "icon": "carbon:network-3",
        },
    ]

    model_trees_items = [
        {
            "value": "decision-tree",
            "label": "Decision Tree",
            "icon": "carbon:tree-view",
        },
        {"value": "random-forest", "label": "Random Forest", "icon": "carbon:trees"},
        {
            "value": "gradient-boosting",
            "label": "Gradient Boosting",
            "icon": "carbon:chart-stacked",
        },
    ]

    model_evaluate_items = [
        {
            "value": "evaluate-regression",
            "label": "Evaluate Regression",
            "icon": "carbon:chart-evaluation",
        },
        {
            "value": "evaluate-classification",
            "label": "Evaluate Classification",
            "icon": "carbon:chart-custom",
        },
    ]

    model_other_items = [
        {
            "value": "collaborative-filtering",
            "label": "Collaborative Filtering",
            "icon": "carbon:recommend",
        },
        {
            "value": "decision-analysis",
            "label": "Decision Analysis",
            "icon": "carbon:decision-tree",
        },
        {"value": "simulator", "label": "Simulate", "icon": "carbon:chart-scatter"},
    ]

    # Multivariate pages
    multivariate_items = [
        {"value": "pre-factor", "label": "Pre-Factor", "icon": "carbon:chart-radar"},
        {
            "value": "full-factor",
            "label": "Full Factor",
            "icon": "carbon:analytics-custom",
        },
        {
            "value": "kmeans-cluster",
            "label": "K-Means Clustering",
            "icon": "carbon:chart-cluster-bar",
        },
        {
            "value": "hierarchical-cluster",
            "label": "Hierarchical Clustering",
            "icon": "carbon:tree-view-alt",
        },
        {
            "value": "perceptual-map",
            "label": "Perceptual Map",
            "icon": "carbon:chart-bubble-packed",
        },
        {"value": "mds", "label": "MDS", "icon": "carbon:chart-3d"},
        {"value": "conjoint", "label": "Conjoint Analysis", "icon": "carbon:analytics"},
    ]

    # Basics pages
    basics_means_items = [
        {
            "value": "single-mean",
            "label": "Single Mean",
            "icon": "carbon:chart-average",
        },
        {"value": "compare-means", "label": "Compare Means", "icon": "carbon:compare"},
    ]

    basics_props_items = [
        {
            "value": "single-prop",
            "label": "Single Proportion",
            "icon": "carbon:percentage",
        },
        {
            "value": "compare-props",
            "label": "Compare Proportions",
            "icon": "carbon:percentage",
        },
    ]

    basics_tables_items = [
        {"value": "cross-tabs", "label": "Cross Tabs", "icon": "carbon:table-split"},
        {
            "value": "goodness",
            "label": "Goodness of Fit",
            "icon": "carbon:fit-to-screen",
        },
    ]

    basics_other_items = [
        {
            "value": "correlation",
            "label": "Correlation",
            "icon": "carbon:connection-signal",
        },
        {"value": "clt", "label": "CLT", "icon": "carbon:chart-line-data"},
        {
            "value": "prob-calc",
            "label": "Probability Calc",
            "icon": "carbon:calculator-check",
        },
    ]

    def create_nav_links(items):
        """Helper to create navigation links."""
        links = []
        for item in items:
            links.append(
                dmc.NavLink(
                    label=item["label"],
                    leftSection=DashIconify(icon=item["icon"], width=20, height=20),
                    active=False,
                    variant="subtle",
                    id={"type": "nav-link", "index": item["value"]},
                    n_clicks=0,
                    href=f"#{item['value']}",
                )
            )
        return links

    # Create collapsible accordion with sections
    return dmc.Accordion(
        children=[
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        "Data",
                        icon=DashIconify(icon="carbon:data-base", width=20, height=20),
                    ),
                    dmc.AccordionPanel(dmc.Stack(create_nav_links(data_items), gap="xs")),
                ],
                value="data",
            ),
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        "Design",
                        icon=DashIconify(icon="carbon:chemistry", width=20, height=20),
                    ),
                    dmc.AccordionPanel(dmc.Stack(create_nav_links(design_items), gap="xs")),
                ],
                value="design",
            ),
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        "Model",
                        icon=DashIconify(icon="carbon:machine-learning", width=20, height=20),
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack(
                            [
                                dmc.Text("Estimate", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(model_estimate_items),
                                dmc.Divider(my="xs"),
                                dmc.Text("Trees", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(model_trees_items),
                                dmc.Divider(my="xs"),
                                dmc.Text("Evaluate", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(model_evaluate_items),
                                dmc.Divider(my="xs"),
                                dmc.Text(
                                    "Recommend & Decide",
                                    size="xs",
                                    fw=600,
                                    c="dimmed",
                                    pl="xs",
                                ),
                                *create_nav_links(model_other_items),
                            ],
                            gap="xs",
                        )
                    ),
                ],
                value="model",
            ),
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        "Multivariate",
                        icon=DashIconify(icon="carbon:chart-multitype", width=20, height=20),
                    ),
                    dmc.AccordionPanel(dmc.Stack(create_nav_links(multivariate_items), gap="xs")),
                ],
                value="multivariate",
            ),
            dmc.AccordionItem(
                children=[
                    dmc.AccordionControl(
                        "Basics",
                        icon=DashIconify(icon="carbon:calculator", width=20, height=20),
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack(
                            [
                                dmc.Text("Means", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(basics_means_items),
                                dmc.Divider(my="xs"),
                                dmc.Text(
                                    "Proportions",
                                    size="xs",
                                    fw=600,
                                    c="dimmed",
                                    pl="xs",
                                ),
                                *create_nav_links(basics_props_items),
                                dmc.Divider(my="xs"),
                                dmc.Text("Tables", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(basics_tables_items),
                                dmc.Divider(my="xs"),
                                dmc.Text("Other", size="xs", fw=600, c="dimmed", pl="xs"),
                                *create_nav_links(basics_other_items),
                            ],
                            gap="xs",
                        )
                    ),
                ],
                value="basics",
            ),
        ],
        value=["data"],  # Start with data section expanded
        chevronPosition="right",
        multiple=True,  # Allow multiple sections to be open
    )


def create_aside():
    """
    Create aside panel for dataset selector.

    Returns
    -------
    dmc.Stack
        Aside content with dataset selector
    """
    return dmc.Stack(
        [
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Active Dataset", fw=500, size="sm"),
                            dmc.Select(
                                id="dataset-selector",
                                data=[],
                                placeholder="Select dataset...",
                                searchable=True,
                                clearable=False,
                                leftSection=DashIconify(icon="carbon:data-table"),
                            ),
                            dmc.Group(
                                [
                                    dmc.Badge(
                                        id="dataset-rows-badge",
                                        children="0 rows",
                                        color="blue",
                                        variant="light",
                                    ),
                                    dmc.Badge(
                                        id="dataset-cols-badge",
                                        children="0 cols",
                                        color="green",
                                        variant="light",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                        gap="xs",
                    )
                ],
                withBorder=True,
                radius="md",
                p="sm",
            ),
            dmc.Card(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Quick Stats", fw=500, size="sm"),
                            dmc.Text(id="dataset-memory", size="xs", c="dimmed"),
                        ],
                        gap="xs",
                    )
                ],
                withBorder=True,
                radius="md",
                p="sm",
            ),
        ],
        gap="md",
    )


def create_footer():
    """
    Create application footer.

    Returns
    -------
    dmc.Group
        Footer content with credits and links
    """
    return dmc.Group(
        [
            dmc.Text(APP_TITLE, size="sm", c="dimmed"),
            dmc.Group(
                [
                    dmc.Anchor("Documentation", href="#", size="sm", c="dimmed"),
                    dmc.Text("•", size="sm", c="dimmed"),
                    dmc.Anchor(
                        "GitHub",
                        href=GITHUB_URL,
                        size="sm",
                        c="dimmed",
                        target="_blank",
                    ),
                    dmc.Text("•", size="sm", c="dimmed"),
                    dmc.Anchor("Report Issue", href="#", size="sm", c="dimmed"),
                ],
                gap="xs",
            ),
        ],
        justify="space-between",
        style={"width": "100%"},
    )
