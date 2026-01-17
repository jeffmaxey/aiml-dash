"""
Landing Page Layout Module

This module provides the main landing page layout using Dash Mantine Components.
The landing page serves as the application's home page, displaying a welcome message
and action cards for key navigation options (Upload, Find, Explore).

Components:
    - Background image with welcome text
    - Three action cards for primary navigation
    - Responsive grid layout

Features:
    - Clickable action cards with icons
    - Hover effects on interactive elements
    - Responsive design adapting to screen sizes
    - Clean, centered layout with visual hierarchy

Author: AIML Dash Team
Date: 2026-01-07
"""

import dash_mantine_components as dmc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis


def get_layout():
    """
    Create the main landing page layout.

    The landing page displays:
    - A background image with welcome text at the top
    - Three action cards in a grid layout for primary navigation:
      * Upload data
      * Find sequences
      * Explore experiments

    The layout uses a responsive grid that adapts to different screen sizes,
    with cards stacking on smaller devices and displaying horizontally on larger screens.

    Returns:
        dmc.Container: The complete landing page layout with background and action cards
    """
    return dmc.Container(
        [
            # ==========================================
            # SECTION 1: Hero Section with Background Image
            # ==========================================
            dmc.Stack(
                [
                    # Background image (decorative)
                    html.Img(
                        src="/assets/bg.png",
                        className="bg-image-center bg-image-center-container bg-image-washed",
                    ),
                    # Main welcome title
                    dmc.Title(
                        gs.welcome,
                        order=1,
                        fw=700,
                        c="blue",
                        ta="center",
                    ),
                    # Welcome subtitle/description
                    dmc.Title(
                        gs.welcome_text,
                        order=5,
                        c="gray",
                        ta="center",
                    ),
                ],
                align="center",
                justify="center",
                p="xl",
            ),
            # ==========================================
            # SECTION 2: Action Cards Grid
            # ==========================================
            dmc.Grid(
                [
                    # Card 1: Upload Data
                    dmc.GridCol(
                        action_card(
                            icon=vis.icon_upload,
                            label=gs.nav_upload,
                            href=gs.nav_upload_path,
                            text_below=gs.small_text_upload,
                        ),
                        span={"base": 12, "sm": 6, "md": 4},  # Responsive: full width on mobile, 1/3 on desktop
                    ),
                    # Card 2: Find Sequences
                    dmc.GridCol(
                        action_card(
                            icon=vis.icon_search,
                            label=gs.nav_find_seq,
                            href=gs.nav_find_seq_path,
                            text_below=gs.small_text_find,
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                    # Card 3: Explore Database
                    dmc.GridCol(
                        action_card(
                            icon=vis.icon_database,
                            label=gs.nav_explore,
                            href=gs.nav_explore_path,
                            text_below=gs.small_text_explore,
                        ),
                        span={"base": 12, "sm": 6, "md": 4},
                    ),
                ],
                justify="center",
                gutter="lg",
            ),
        ],
        fluid=True,
        className=vis.main_page_class,
        py="xl",
        style={
            # Z-index ensures content appears above background image
            "zIndex": 1,
        },
    )


def action_card(icon: str, label: str, href: str, text_below: str):
    """
    Create a clickable action card with icon, title, and description.

    Action cards serve as the primary navigation elements on the landing page.
    Each card displays:
    - An icon representing the action
    - A title/label for the action
    - A brief description of what the action does

    The card is wrapped in a Link component to make the entire card clickable,
    providing better UX than just having text links.

    Args:
        icon: Icon identifier/class from the vis module (e.g., vis.icon_upload)
        label: Main title text displayed on the card (e.g., "Upload Data")
        href: URL path to navigate to when card is clicked (e.g., "/upload")
        text_below: Descriptive text shown below the label (e.g., "Upload your sequences")

    Returns:
        dcc.Link: A clickable link containing a Mantine card with the action content

    Example:
        >>> action_card(
        ...     icon=vis.icon_upload,
        ...     label="Upload Data",
        ...     href="/upload",
        ...     text_below="Upload your sequences"
        ... )
    """
    # Create the card component with icon, title, and description
    card = dmc.Card(
        dmc.Stack(
            [
                # Icon container with hover effect styling
                html.Div(
                    [vis.get_icon(icon, size=vis.LARGE)],
                    className="icon-style3",  # Custom class providing hover circle effect
                ),
                # Card title/label
                dmc.Title(
                    label,
                    order=4,
                    fw=600,
                    ta="center",
                    mt="md",
                ),
                # Card description text
                dmc.Text(
                    text_below,
                    size="sm",
                    c="dimmed",
                    ta="center",
                ),
            ],
            align="center",
            justify="center",
            gap="xs",
            p="lg",
        ),
        className="card-style",  # Custom styling class
        withBorder=True,
        shadow="sm",
        radius="md",
        p="lg",
        h="100%",  # Card takes full height of its container for consistent sizing
    )

    # Wrap card in a link to make entire card clickable
    return dcc.Link(
        card,
        href=href,
        style={"textDecoration": "none"},  # Remove default hyperlink underline
    )
