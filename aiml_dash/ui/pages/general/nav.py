"""
Navigation Components - Top Bar and Sidebar

This module provides the main navigation components for the application:
- Top navigation bar (navbar) with branding and menu toggle
- Side navigation menu (sidebar) with page links

The navigation uses Dash Mantine Components for a modern, responsive UI with:
- Fixed top bar with logos and application title
- Collapsible sidebar with icon-based navigation
- Active link highlighting
- Responsive layout with flexbox alignment

Components:
    - get_navbar(): Top navigation bar with logos, title, and menu icon
    - get_sidebar(): Collapsible side navigation menu with page links

Layout Structure:
    Navbar: [Menu Icon] [Caltech Logo] [App Title] [SSEC Logo]
    Sidebar: Vertical list of navigation links with icons and labels

Features:
    - Hamburger menu icon for sidebar toggle
    - Institutional branding (Caltech and SSEC logos)
    - Active route highlighting
    - Icon-based navigation with text labels
    - Smooth transitions and hover effects
    - Consistent styling with custom CSS classes

Author: Conversion to Mantine Components
Date: January 7, 2026
"""

import dash_mantine_components as dmc
from dash import html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis


def get_navbar():
    """
    Create the top navigation bar.

    Builds a fixed-position top bar containing:
    1. Hamburger menu icon (left) - toggles sidebar visibility
    2. Caltech logo - institutional branding
    3. Application title (center) - main heading
    4. SSEC logo (right) - lab branding

    The navbar uses a grid layout with four columns for proper alignment
    and spacing. Each element is positioned with flexbox utilities.

    Layout:
        - Column 1 (span=1): Menu icon, left-aligned
        - Column 2 (span=2): Caltech logo, left-aligned
        - Column 3 (span=auto): App title, center-aligned
        - Column 4 (span=3): SSEC logo, right-aligned

    Returns:
        html.Div: Top navigation bar container with all elements

    Component IDs:
        - id-menu-icon: Hamburger menu icon (clickable)

    Styling:
        - Primary background color
        - Bottom shadow for depth
        - Light text on dark background
        - Custom navbar height and padding
        - Responsive fluid container

    CSS Classes:
        - bg-primary: Primary theme background
        - custom_navbar: Application-specific navbar styling
        - text-light: Light text color
        - hamburger_menu: Menu icon styling
        - app-title: Application title styling
    """
    # Top navigation bar container
    return html.Div(
        dmc.Container(
            [
                # Main navigation grid with four columns
                dmc.Grid(
                    [
                        # Column 1: Hamburger menu icon (sidebar toggle)
                        dmc.GridCol(
                            [
                                html.Span(vis.get_icon(vis.icon_menu), id="id-menu-icon", className="hamburger_menu"),
                            ],
                            span=1,
                            style=vis.border_column,
                            # Left-align menu icon
                            className="d-flex align-items-center justify-content-start",
                        ),
                        # Column 2: Caltech institutional logo
                        dmc.GridCol(
                            [
                                html.Img(
                                    src="../../assets/Caltech Logo 2017/LOGO-WHITE/LOGO-WHITE-RGB/Caltech_LOGO-WHITE"
                                    "-RGB.png",
                                    width="80%",
                                ),
                            ],
                            span=2,
                            style=vis.border_column,
                            # Left-align within column
                            className="d-flex align-items-center justify-content-start",
                        ),
                        # Column 3: Application title (center)
                        dmc.GridCol(
                            [html.Div(gs.web_title, className="app-title")],
                            span="auto",
                            style=vis.border_column,
                            # Center the title text
                            className="display-4 d-flex align-items-center justify-content-center",
                        ),
                        # Column 4: SSEC lab logo
                        dmc.GridCol(
                            [html.Img(src="../../assets/SSEC_horizontal_white_cropped.png", width="60%")],
                            span=3,
                            style=vis.border_column,
                            # Right-align logo
                            className="d-flex align-items-center justify-content-end",
                        ),
                    ],
                    gutter=0,  # No gutters - tight layout
                    style=vis.border_row,
                ),
            ],
            fluid=True,  # Full-width container
        ),
        style={"box-shadow": "0 5px 5px -5px #333"},  # Bottom shadow
        className="bg-primary custom_navbar text-light p-1 text-center fs-1 fw-light border-bottom",
    )


def get_sidebar():
    """
    Create the collapsible side navigation menu.

    Builds a vertical navigation sidebar with links to all main pages:
    1. Home/Landing page
    2. Upload page - data submission
    3. Find Sequences page - sequence search
    4. Explore page - experiment browsing
    5. About page - documentation

    Each navigation link includes:
    - Icon (left) - visual identifier for page
    - Label text (right) - page name
    - Active highlighting - shows current page
    - Hover effects - visual feedback

    The sidebar can collapse to show only icons or expand to show
    icons with labels. The state is controlled by the menu icon
    in the top navbar via callback functionality.

    Returns:
        html.Div: Sidebar container with navigation links

    Component IDs:
        - id-sidebar: Main sidebar container (for collapse/expand control)

    Navigation Links:
        - /: Home/Landing page
        - gs.nav_upload_path: Upload experiment data
        - gs.nav_find_seq_path: Find similar sequences
        - gs.nav_explore_path: Explore experiments
        - gs.nav_about_path: About/documentation

    Link Properties:
        - active="exact": Exact path matching for active state
        - href: Target page URL
        - className="custom-nav-item": Custom styling

    Styling:
        - thin-sidebar: Narrow width for sidebar
        - collapsed: Initial collapsed state (icons only)
        - custom-nav-icon: Icon styling
        - custom-nav-text: Label text styling
        - custom-nav-item: Individual link styling

    Behavior:
        - Clicking menu icon toggles sidebar width
        - Active link automatically highlighted
        - Smooth transitions between states
        - Icons remain visible when collapsed
    """
    # Sidebar navigation container
    return html.Div(
        [
            # Navigation links container
            html.Div(
                [
                    # Home/Landing page link
                    dmc.Anchor(
                        [
                            html.Span(vis.get_icon(vis.icon_home), className="custom-nav-icon"),
                            html.Span(gs.nav_lab, className="custom-nav-text"),
                        ],
                        href="/",
                        className="custom-nav-item",
                        underline=False,
                    ),
                    # Upload page link
                    dmc.Anchor(
                        [
                            html.Span(vis.get_icon(vis.icon_upload), className="custom-nav-icon"),
                            html.Span(gs.nav_upload, className="custom-nav-text"),
                        ],
                        href=gs.nav_upload_path,
                        className="custom-nav-item",
                        underline=False,
                    ),
                    # Find Sequences page link
                    dmc.Anchor(
                        [
                            html.Span(vis.get_icon(vis.icon_search), className="custom-nav-icon"),
                            html.Span(gs.nav_find_seq, className="custom-nav-text"),
                        ],
                        href=gs.nav_find_seq_path,
                        className="custom-nav-item",
                        underline=False,
                    ),
                    # Explore Experiments page link
                    dmc.Anchor(
                        [
                            html.Span(vis.get_icon(vis.icon_database), className="custom-nav-icon"),
                            html.Span(gs.nav_explore, className="custom-nav-text"),
                        ],
                        href=gs.nav_explore_path,
                        className="custom-nav-item",
                        underline=False,
                    ),
                    # About/Documentation page link
                    dmc.Anchor(
                        [
                            html.Span(vis.get_icon(vis.icon_about), className="custom-nav-icon"),
                            html.Span(gs.nav_about, className="custom-nav-text"),
                        ],
                        href=gs.nav_about_path,
                        className="custom-nav-item",
                        underline=False,
                    ),
                ],
            ),
        ],
        id="id-sidebar",
        className="thin-sidebar collapsed",
    )
