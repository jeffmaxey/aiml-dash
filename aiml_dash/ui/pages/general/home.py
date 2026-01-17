"""
Home Page - Landing Page

This module provides the main landing page for the AIML Dash application.
Users are greeted with a welcome message and quick action cards for navigation.

Author: AIML Dash Team
Date: 2026-01-07
"""

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def layout():
    """
    Create the home landing page layout.

    The home page displays:
    - Hero section with welcome message and description
    - Quick action cards for primary navigation:
      * Projects - Manage your projects and experiments
      * Data - Upload and manage your datasets
      * Analysis - Run statistical analyses
      * Models - Build predictive models
      * About - Learn more about the application

    Returns:
        dmc.Container: The complete home page layout
    """
    return dmc.Container(
        [
            # ==========================================
            # SECTION 1: Hero Section
            # ==========================================
            dmc.Stack(
                [
                    # Main welcome title
                    dmc.Title(
                        "Welcome to AIML Dash",
                        order=1,
                        fw=700,
                        c="blue",
                        ta="center",
                        mb="md",
                    ),
                    # Welcome subtitle/description
                    dmc.Text(
                        "A comprehensive data analysis platform for AI/ML workflows",
                        size="lg",
                        c="gray",
                        ta="center",
                        mb="xl",
                    ),
                    dmc.Text(
                        "Get started by selecting one of the options below or use the navigation menu to explore all features",
                        size="sm",
                        c="dimmed",
                        ta="center",
                    ),
                ],
                align="center",
                justify="center",
                py="xl",
                mb="lg",
            ),
            # ==========================================
            # SECTION 2: Action Cards Grid
            # ==========================================
            dmc.Grid(
                [
                    # Card 1: Projects
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:application",
                            label="Projects",
                            description="Manage your projects and experiments",
                            page_id="projects",
                            color="blue",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 2: Data Management
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:data-table",
                            label="Data",
                            description="Upload, view, and manage datasets",
                            page_id="manage",
                            color="green",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 3: Analysis
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:analytics",
                            label="Analysis",
                            description="Statistical analysis and testing",
                            page_id="single-mean",
                            color="violet",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 4: Models
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:machine-learning",
                            label="Models",
                            description="Build and evaluate ML models",
                            page_id="linear-regression",
                            color="orange",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 5: Visualization
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:chart-scatter",
                            label="Visualize",
                            description="Create interactive visualizations",
                            page_id="visualize",
                            color="pink",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 6: About
                    dmc.GridCol(
                        create_action_card(
                            icon="carbon:information",
                            label="About",
                            description="Learn about AIML Dash features",
                            page_id="about",
                            color="cyan",
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                ],
                justify="center",
                gutter="lg",
                mb="xl",
            ),
            # ==========================================
            # SECTION 3: Quick Stats or Info
            # ==========================================
            dmc.Card(
                [
                    dmc.Group(
                        [
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            DashIconify(
                                                icon="carbon:data-base",
                                                width=24,
                                                color="#1971c2",
                                            ),
                                            dmc.Text("Data Management", fw=500, size="sm"),
                                        ],
                                        gap="xs",
                                    ),
                                    dmc.Text(
                                        "Upload, transform, and explore your data",
                                        size="xs",
                                        c="dimmed",
                                    ),
                                ],
                                gap="xs",
                            ),
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            DashIconify(
                                                icon="carbon:calculator",
                                                width=24,
                                                color="#1971c2",
                                            ),
                                            dmc.Text("Statistical Analysis", fw=500, size="sm"),
                                        ],
                                        gap="xs",
                                    ),
                                    dmc.Text(
                                        "Comprehensive statistical testing tools",
                                        size="xs",
                                        c="dimmed",
                                    ),
                                ],
                                gap="xs",
                            ),
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            DashIconify(
                                                icon="carbon:machine-learning-model",
                                                width=24,
                                                color="#1971c2",
                                            ),
                                            dmc.Text("Machine Learning", fw=500, size="sm"),
                                        ],
                                        gap="xs",
                                    ),
                                    dmc.Text(
                                        "Build and evaluate predictive models",
                                        size="xs",
                                        c="dimmed",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                        grow=True,
                        wrap="wrap",
                        align="flex-start",
                    )
                ],
                withBorder=True,
                shadow="sm",
                radius="md",
                p="lg",
            ),
        ],
        size="xl",
        py="xl",
    )


def create_action_card(icon, label, description, page_id, color="blue"):
    """
    Create a clickable action card with icon, title, and description.

    Args:
        icon: DashIconify icon name
        label: Main title text displayed on the card
        description: Descriptive text shown below the label
        page_id: Page identifier for navigation
        color: Mantine color for theming

    Returns:
        dmc.Card: A clickable card component
    """
    return dmc.Card(
        dmc.Stack(
            [
                # Icon container
                dmc.Center(
                    dmc.ThemeIcon(
                        DashIconify(icon=icon, width=32),
                        size=64,
                        radius="md",
                        variant="light",
                        color=color,
                    )
                ),
                # Card title/label
                dmc.Text(
                    label,
                    size="lg",
                    fw=600,
                    ta="center",
                ),
                # Card description text
                dmc.Text(
                    description,
                    size="sm",
                    c="dimmed",
                    ta="center",
                ),
                # Navigation button
                dmc.Button(
                    "Go",
                    variant="light",
                    color=color,
                    fullWidth=True,
                    id={"type": "nav-link", "index": page_id},
                    n_clicks=0,
                ),
            ],
            align="center",
            justify="center",
            gap="md",
            p="lg",
        ),
        withBorder=True,
        shadow="sm",
        radius="md",
        h="100%",
        style={"cursor": "pointer", "transition": "transform 0.2s"},
        className="hover-card",
    )
