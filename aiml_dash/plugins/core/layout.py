"""Layouts for core plugin pages."""

import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from aiml_dash.plugins.core.components import (
    create_feature_card,
    create_resource_item,
    create_section_header,
    create_step_card,
)
from aiml_dash.plugins.core.styles import CONTAINER_SIZE, SECTION_GAP


def home_layout() -> dmc.Container:
    """Create the home page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                # Hero Section
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    DashIconify(icon="carbon:machine-learning", width=48, color="#339af0"),
                                    dmc.Title("AIML Dash", order=1),
                                ],
                                gap="md",
                            ),
                            dmc.Text(
                                "A comprehensive Dash application for Predictive Analytics and Machine Learning",
                                size="lg",
                                c="dimmed",
                            ),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Get Started",
                                        leftSection=DashIconify(icon="carbon:rocket"),
                                        variant="filled",
                                        href="/help",
                                    ),
                                    dmc.Button(
                                        "View on GitHub",
                                        leftSection=DashIconify(icon="carbon:logo-github"),
                                        variant="light",
                                        href="https://github.com/jeffmaxey/aiml-dash",
                                        target="_blank",
                                    ),
                                ],
                                gap="sm",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="xl",
                    style={"background": "linear-gradient(135deg, rgba(51, 154, 240, 0.1) 0%, rgba(51, 154, 240, 0.05) 100%)"},
                ),
                
                # Key Features
                create_section_header(
                    "Key Features",
                    "Discover what makes AIML Dash a powerful platform for data analysis",
                ),
                dmc.SimpleGrid(
                    [
                        create_feature_card(
                            "Plugin Framework",
                            "Modular architecture with dynamic plugin loading. Enable or disable features at runtime.",
                            "carbon:plugin",
                        ),
                        create_feature_card(
                            "Data Management",
                            "Import, transform, and visualize data from CSV, Excel, SQL databases, and more.",
                            "carbon:data-table",
                        ),
                        create_feature_card(
                            "Statistical Analysis",
                            "Hypothesis testing, correlation analysis, ANOVA, and experimental design tools.",
                            "carbon:chart-line",
                        ),
                        create_feature_card(
                            "Machine Learning",
                            "Build and evaluate models including regression, classification, clustering, and neural networks.",
                            "carbon:machine-learning",
                        ),
                        create_feature_card(
                            "Interactive Visualizations",
                            "Create rich, interactive charts and plots powered by Plotly and Dash Mantine Components.",
                            "carbon:chart-bubble",
                        ),
                        create_feature_card(
                            "State Management",
                            "Save and restore application state for reproducible analysis and collaboration.",
                            "carbon:save",
                        ),
                    ],
                    cols={"base": 1, "sm": 2, "md": 3},
                    spacing="md",
                    verticalSpacing="md",
                ),
                
                dmc.Divider(),
                
                # Quick Start
                create_section_header("Quick Start", "Get AIML Dash running in three simple steps"),
                dmc.Stack(
                    [
                        create_step_card(
                            "1",
                            "Clone the Repository",
                            "Download the source code from GitHub to your local machine.",
                            "git clone https://github.com/jeffmaxey/aiml-dash.git\ncd aiml-dash",
                        ),
                        create_step_card(
                            "2",
                            "Install Dependencies",
                            "Install all required packages using UV (recommended) or pip.",
                            "uv sync\n# or: pip install -e .",
                        ),
                        create_step_card(
                            "3",
                            "Launch the Application",
                            "Start the Dash server and open http://127.0.0.1:8050 in your browser.",
                            "uv run python aiml_dash/run.py\n# or: python aiml_dash/run.py",
                        ),
                    ],
                    gap="md",
                ),
                
                dmc.Divider(),
                
                # Available Sections
                create_section_header("Explore Features", "Navigate through different analysis sections"),
                dmc.SimpleGrid(
                    [
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:data-table", width=24), size="xl", radius="md", variant="light", color="blue"),
                                    dmc.Stack([
                                        dmc.Text("Data", fw=600, size="lg"),
                                        dmc.Text("Import, explore, transform, and visualize datasets", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:chart-line", width=24), size="xl", radius="md", variant="light", color="green"),
                                    dmc.Stack([
                                        dmc.Text("Basics", fw=600, size="lg"),
                                        dmc.Text("Statistical tests, correlation, and hypothesis testing", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:chemistry", width=24), size="xl", radius="md", variant="light", color="orange"),
                                    dmc.Stack([
                                        dmc.Text("Design", fw=600, size="lg"),
                                        dmc.Text("Experimental design, DOE, and sample size calculations", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:machine-learning-model", width=24), size="xl", radius="md", variant="light", color="violet"),
                                    dmc.Stack([
                                        dmc.Text("Model", fw=600, size="lg"),
                                        dmc.Text("Machine learning models and predictive analytics", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:chart-3d", width=24), size="xl", radius="md", variant="light", color="pink"),
                                    dmc.Stack([
                                        dmc.Text("Multivariate", fw=600, size="lg"),
                                        dmc.Text("Advanced multivariate analysis and clustering", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(DashIconify(icon="carbon:settings", width=24), size="xl", radius="md", variant="light", color="gray"),
                                    dmc.Stack([
                                        dmc.Text("Settings", fw=600, size="lg"),
                                        dmc.Text("Configure plugins and application preferences", size="sm", c="dimmed"),
                                    ], gap=4),
                                ], align="flex-start"),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    cols={"base": 1, "sm": 2, "md": 3},
                    spacing="md",
                ),
                
                dmc.Divider(),
                
                # Resources
                create_section_header("Resources", "Learn more about AIML Dash"),
                dmc.Card(
                    dmc.Stack(
                        [
                            create_resource_item(
                                "Documentation",
                                "Comprehensive guides, tutorials, and API reference",
                                "carbon:book",
                            ),
                            create_resource_item(
                                "GitHub Repository",
                                "Source code, issue tracking, and contribution guidelines",
                                "carbon:logo-github",
                            ),
                            create_resource_item(
                                "Plugin Development",
                                "Learn how to create custom plugins and extend functionality",
                                "carbon:code",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )


def help_layout() -> dmc.Container:
    """Create the help page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header(
                    "Help & Documentation",
                    "Comprehensive guides and resources for using AIML Dash",
                ),
                
                # Quick Help
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Quick Help", fw=600, size="lg"),
                            dmc.Divider(),
                            create_resource_item(
                                "Getting Started",
                                "New to AIML Dash? Start here to learn the basics of loading data and running your first analysis.",
                                "carbon:rocket",
                            ),
                            create_resource_item(
                                "Plugin Management",
                                "Enable, disable, and configure plugins from the Settings page to customize your workspace.",
                                "carbon:settings",
                            ),
                            create_resource_item(
                                "State Management",
                                "Export and import application state using the header menu to save your work and share with colleagues.",
                                "carbon:save",
                            ),
                            create_resource_item(
                                "Keyboard Shortcuts",
                                "Use arrow keys to navigate, Esc to close modals, and / to focus search (where available).",
                                "carbon:keyboard",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Documentation Links
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Documentation", fw=600, size="lg"),
                            dmc.Divider(),
                            dmc.Group([
                                dmc.Button(
                                    "Installation Guide",
                                    leftSection=DashIconify(icon="carbon:download"),
                                    variant="light",
                                    href="https://jeffmaxey.github.io/aiml-dash/getting-started/installation/",
                                    target="_blank",
                                ),
                                dmc.Button(
                                    "Quick Start",
                                    leftSection=DashIconify(icon="carbon:rocket"),
                                    variant="light",
                                    href="https://jeffmaxey.github.io/aiml-dash/getting-started/quick-start/",
                                    target="_blank",
                                ),
                                dmc.Button(
                                    "User Guide",
                                    leftSection=DashIconify(icon="carbon:book"),
                                    variant="light",
                                    href="https://jeffmaxey.github.io/aiml-dash/user-guide/overview/",
                                    target="_blank",
                                ),
                            ], gap="sm"),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Feature Overview
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Feature Overview", fw=600, size="lg"),
                            dmc.Divider(),
                            dmc.Accordion(
                                [
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Data Management", icon=DashIconify(icon="carbon:data-table", width=20)),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("Import data from CSV, Excel, JSON, or SQL databases", size="sm"),
                                                    dmc.Text("Transform and filter datasets with Python expressions", size="sm"),
                                                    dmc.Text("Create new variables and aggregate data", size="sm"),
                                                    dmc.Text("Export results in multiple formats", size="sm"),
                                                    dmc.Button(
                                                        "Learn More",
                                                        size="xs",
                                                        variant="subtle",
                                                        leftSection=DashIconify(icon="carbon:arrow-right", width=16),
                                                        href="https://jeffmaxey.github.io/aiml-dash/user-guide/data-management/",
                                                        target="_blank",
                                                    ),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="data",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Statistical Analysis", icon=DashIconify(icon="carbon:chart-line", width=20)),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("Hypothesis testing: t-tests, ANOVA, chi-square", size="sm"),
                                                    dmc.Text("Correlation and regression analysis", size="sm"),
                                                    dmc.Text("Probability calculations and distributions", size="sm"),
                                                    dmc.Text("Cross-tabulation and goodness-of-fit tests", size="sm"),
                                                    dmc.Button(
                                                        "Learn More",
                                                        size="xs",
                                                        variant="subtle",
                                                        leftSection=DashIconify(icon="carbon:arrow-right", width=16),
                                                        href="https://jeffmaxey.github.io/aiml-dash/user-guide/analysis-tools/",
                                                        target="_blank",
                                                    ),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="basics",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Machine Learning", icon=DashIconify(icon="carbon:machine-learning", width=20)),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("Linear and logistic regression", size="sm"),
                                                    dmc.Text("Decision trees and random forests", size="sm"),
                                                    dmc.Text("Neural networks and gradient boosting", size="sm"),
                                                    dmc.Text("Model evaluation and comparison", size="sm"),
                                                    dmc.Button(
                                                        "Learn More",
                                                        size="xs",
                                                        variant="subtle",
                                                        leftSection=DashIconify(icon="carbon:arrow-right", width=16),
                                                        href="https://jeffmaxey.github.io/aiml-dash/user-guide/analysis-tools/",
                                                        target="_blank",
                                                    ),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="model",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Visualization", icon=DashIconify(icon="carbon:chart-bubble", width=20)),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("Interactive scatter plots, line charts, and bar charts", size="sm"),
                                                    dmc.Text("Histograms, box plots, and violin plots", size="sm"),
                                                    dmc.Text("Heatmaps and correlation matrices", size="sm"),
                                                    dmc.Text("3D visualizations and custom plots", size="sm"),
                                                    dmc.Button(
                                                        "Learn More",
                                                        size="xs",
                                                        variant="subtle",
                                                        leftSection=DashIconify(icon="carbon:arrow-right", width=16),
                                                        href="https://jeffmaxey.github.io/aiml-dash/user-guide/visualization/",
                                                        target="_blank",
                                                    ),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="viz",
                                    ),
                                ],
                                variant="separated",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Troubleshooting
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Troubleshooting", fw=600, size="lg"),
                            dmc.Divider(),
                            dmc.Accordion(
                                [
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Data Import Issues"),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("• Check file format matches the extension", size="sm"),
                                                    dmc.Text("• Try different encoding options (UTF-8, Latin-1)", size="sm"),
                                                    dmc.Text("• Verify delimiter settings for CSV files", size="sm"),
                                                    dmc.Text("• Ensure file permissions are correct", size="sm"),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="import",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Performance Issues"),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("• Filter large datasets before visualization", size="sm"),
                                                    dmc.Text("• Use pagination for tables with many rows", size="sm"),
                                                    dmc.Text("• Sample data for initial exploration", size="sm"),
                                                    dmc.Text("• Convert string columns to categories", size="sm"),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="performance",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Plugin Problems"),
                                            dmc.AccordionPanel(
                                                dmc.Stack([
                                                    dmc.Text("• Check plugin is enabled in Settings", size="sm"),
                                                    dmc.Text("• Verify plugin dependencies are installed", size="sm"),
                                                    dmc.Text("• Review logs for error messages", size="sm"),
                                                    dmc.Text("• Try disabling and re-enabling the plugin", size="sm"),
                                                ], gap="xs"),
                                            ),
                                        ],
                                        value="plugins",
                                    ),
                                ],
                                variant="separated",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Support
                dmc.Alert(
                    dmc.Stack([
                        dmc.Text("Need additional help?", fw=600),
                        dmc.Text("File an issue on GitHub with logs, screenshots, and steps to reproduce.", size="sm"),
                        dmc.Button(
                            "Report an Issue",
                            leftSection=DashIconify(icon="carbon:logo-github"),
                            variant="outline",
                            href="https://github.com/jeffmaxey/aiml-dash/issues/new",
                            target="_blank",
                            mt="xs",
                        ),
                    ], gap="xs"),
                    title="Support",
                    color="blue",
                    icon=DashIconify(icon="carbon:chat"),
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )


def settings_layout() -> dmc.Container:
    """Create the plugin settings page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header("Settings", "Manage plugins and import configurations."),
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Enabled plugins", fw=600),
                            dmc.Stack(id="plugin-toggle-container", gap="sm"),
                        ],
                        gap="sm",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("Import plugin configuration", fw=600),
                            dmc.Text(
                                "Upload a JSON file with an enabled_plugins list to update active plugins.",
                                size="sm",
                                c="dimmed",
                            ),
                            dcc.Upload(
                                id="plugin-import-upload",
                                children=dmc.Button(
                                    "Upload plugin config",
                                    leftSection=DashIconify(icon="carbon:upload"),
                                    variant="light",
                                ),
                                multiple=False,
                            ),
                            dmc.Stack(id="plugin-import-status"),
                        ],
                        gap="sm",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )


def logs_layout() -> dmc.Container:
    """Create the application logs page layout."""

    return dmc.Container(
        dmc.Stack(
            [
                create_section_header(
                    "Application Logs",
                    "View system logs, errors, and diagnostic information",
                ),
                
                # Log Controls
                dmc.Card(
                    dmc.Group(
                        [
                            dmc.Select(
                                id="log-level-filter",
                                label="Log Level",
                                data=[
                                    {"label": "All", "value": "all"},
                                    {"label": "Debug", "value": "debug"},
                                    {"label": "Info", "value": "info"},
                                    {"label": "Warning", "value": "warning"},
                                    {"label": "Error", "value": "error"},
                                ],
                                value="all",
                                w=150,
                            ),
                            dmc.Select(
                                id="log-source-filter",
                                label="Source",
                                data=[
                                    {"label": "All", "value": "all"},
                                    {"label": "Core", "value": "core"},
                                    {"label": "Plugins", "value": "plugins"},
                                    {"label": "Data", "value": "data"},
                                    {"label": "Callbacks", "value": "callbacks"},
                                ],
                                value="all",
                                w=150,
                            ),
                            dmc.Button(
                                "Refresh",
                                id="log-refresh-button",
                                leftSection=DashIconify(icon="carbon:renew"),
                                variant="light",
                            ),
                            dmc.Button(
                                "Clear",
                                id="log-clear-button",
                                leftSection=DashIconify(icon="carbon:trash-can"),
                                variant="light",
                                color="red",
                            ),
                            dmc.Button(
                                "Download",
                                id="log-download-button",
                                leftSection=DashIconify(icon="carbon:download"),
                                variant="light",
                            ),
                        ],
                        gap="md",
                        align="flex-end",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Log Statistics
                dmc.SimpleGrid(
                    [
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(
                                        DashIconify(icon="carbon:information", width=20),
                                        size="lg",
                                        radius="md",
                                        variant="light",
                                        color="blue",
                                    ),
                                    dmc.Stack([
                                        dmc.Text("Info", size="sm", c="dimmed"),
                                        dmc.Text(id="log-count-info", children="0", fw=700, size="xl"),
                                    ], gap=0),
                                ]),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(
                                        DashIconify(icon="carbon:warning", width=20),
                                        size="lg",
                                        radius="md",
                                        variant="light",
                                        color="yellow",
                                    ),
                                    dmc.Stack([
                                        dmc.Text("Warnings", size="sm", c="dimmed"),
                                        dmc.Text(id="log-count-warning", children="0", fw=700, size="xl"),
                                    ], gap=0),
                                ]),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(
                                        DashIconify(icon="carbon:error", width=20),
                                        size="lg",
                                        radius="md",
                                        variant="light",
                                        color="red",
                                    ),
                                    dmc.Stack([
                                        dmc.Text("Errors", size="sm", c="dimmed"),
                                        dmc.Text(id="log-count-error", children="0", fw=700, size="xl"),
                                    ], gap=0),
                                ]),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                        dmc.Card(
                            [
                                dmc.Group([
                                    dmc.ThemeIcon(
                                        DashIconify(icon="carbon:debug", width=20),
                                        size="lg",
                                        radius="md",
                                        variant="light",
                                        color="gray",
                                    ),
                                    dmc.Stack([
                                        dmc.Text("Total Logs", size="sm", c="dimmed"),
                                        dmc.Text(id="log-count-total", children="0", fw=700, size="xl"),
                                    ], gap=0),
                                ]),
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    cols={"base": 2, "sm": 4},
                    spacing="md",
                ),
                
                # Log Display
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Group([
                                dmc.Text("Recent Logs", fw=600, size="lg"),
                                dmc.Badge(id="log-status-badge", children="Live", color="green", variant="light"),
                            ], justify="space-between"),
                            dmc.Divider(),
                            dmc.Stack(
                                id="log-entries-container",
                                children=[
                                    dmc.Text("No logs available yet. Logs will appear here as the application runs.", size="sm", c="dimmed", ta="center", py="xl"),
                                ],
                                gap="xs",
                                style={"maxHeight": "600px", "overflowY": "auto"},
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # System Information
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text("System Information", fw=600, size="lg"),
                            dmc.Divider(),
                            dmc.SimpleGrid(
                                [
                                    dmc.Stack([
                                        dmc.Text("Python Version", size="sm", c="dimmed"),
                                        dmc.Text(id="sys-python-version", children="—", size="sm", fw=500),
                                    ], gap=4),
                                    dmc.Stack([
                                        dmc.Text("Dash Version", size="sm", c="dimmed"),
                                        dmc.Text(id="sys-dash-version", children="—", size="sm", fw=500),
                                    ], gap=4),
                                    dmc.Stack([
                                        dmc.Text("Uptime", size="sm", c="dimmed"),
                                        dmc.Text(id="sys-uptime", children="—", size="sm", fw=500),
                                    ], gap=4),
                                    dmc.Stack([
                                        dmc.Text("Active Plugins", size="sm", c="dimmed"),
                                        dmc.Text(id="sys-plugin-count", children="—", size="sm", fw=500),
                                    ], gap=4),
                                ],
                                cols={"base": 2, "sm": 4},
                                spacing="md",
                            ),
                        ],
                        gap="md",
                    ),
                    withBorder=True,
                    radius="md",
                    p="md",
                ),
                
                # Download Component
                dcc.Download(id="log-download"),
                
                # Refresh Interval
                dcc.Interval(
                    id="log-refresh-interval",
                    interval=5000,  # 5 seconds
                    n_intervals=0,
                ),
                
                dmc.Alert(
                    "Logs are stored in memory and will be cleared when the application restarts. Use the Download button to save logs permanently.",
                    title="Note",
                    color="blue",
                    icon=DashIconify(icon="carbon:information"),
                ),
            ],
            gap=SECTION_GAP,
        ),
        size=CONTAINER_SIZE,
        py="xl",
    )
