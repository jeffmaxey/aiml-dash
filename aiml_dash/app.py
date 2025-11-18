"""
AIML Dash - Dash Application
================================

Main application file for the AIML Data Dash app.
A comprehensive data analysis web application mirroring R Shiny AIML.

Author: Converted from aiml.data R package
License: AGPL-3
"""

import dash
from dash import Dash, html, dcc, Input, Output, State, callback, ALL, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import json
import base64
from datetime import datetime

# Import constants
from utils.constants import APP_TITLE

# Import utilities
from utils.data_manager import data_manager

# Import shell components
from components.shell import (
    create_header,
    create_navigation,
    create_aside,
    create_footer,
)

# Import all pages
from pages.data import (
    manage,
    view,
    explore,
    transform,
    visualize,
    pivot,
    combine,
    report,
)
from pages.design import doe, sampling, sample_size, sample_size_comp, randomizer
from pages.model import (
    linear_regression,
    logistic_regression,
    multinomial_logit,
    naive_bayes,
    neural_network,
    decision_tree,
    random_forest,
    gradient_boosting,
    evaluate_regression,
    evaluate_classification,
    collaborative_filtering,
    decision_analysis,
    simulator,
)
from pages.multivariate import (
    pre_factor,
    full_factor,
    kmeans_cluster,
    hierarchical_cluster,
    perceptual_map,
    mds,
    conjoint,
)
from pages.basics import (
    single_mean,
    compare_means,
    single_prop,
    compare_props,
    cross_tabs,
    goodness,
    correlation,
    clt,
    prob_calc,
)

# Initialize app
app = Dash(
    __name__,
    title=APP_TITLE,
    suppress_callback_exceptions=True,
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"],
)

server = app.server

# ==============================================================================
# MAIN LAYOUT WITH APPSHELL
# ==============================================================================

app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": "'Inter', sans-serif",
        "primaryColor": "blue",
        "components": {
            "Button": {"defaultProps": {"fw": 400}},
            "Alert": {"styles": {"title": {"fontWeight": 500}}},
            "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
        },
    },
    children=dmc.Box(
        [
            dmc.AppShell(
                [
                    # Header
                    dmc.AppShellHeader(
                        create_header(),
                        px="md",
                        id="app-header",
                    ),
                    # Navbar
                    dmc.AppShellNavbar(
                        dmc.ScrollArea(
                            offsetScrollbars=True,
                            type="scroll",
                            children=create_navigation(),
                            p="md",
                        ),
                        id="app-navbar",
                    ),
                    # Aside (dataset selector)
                    dmc.AppShellAside(
                        create_aside(),
                        p="md",
                        id="app-aside",
                    ),
                    # Main content
                    dmc.AppShellMain(html.Div(id="page-content"), id="app-main"),
                    # Footer
                    dmc.AppShellFooter(
                        create_footer(),
                        px="md",
                        py="sm",
                        id="app-footer",
                    ),
                ],
                header={"height": 60},
                navbar={
                    "width": 250,
                    "breakpoint": "sm",
                    "collapsed": {"mobile": False, "desktop": False},
                },
                aside={
                    "width": 300,
                    "breakpoint": "md",
                    "collapsed": {"mobile": False, "desktop": False},
                },
                footer={"height": 50},
                padding="md",
                id="app-shell",
            ),
            # Location component for URL routing
            dcc.Location(id="url", refresh="callback-nav"),
            # Notification container
            dmc.NotificationContainer(id="notification-container"),
            dcc.Store(id="color-scheme-storage", storage_type="local"),
            # Store for application state
            dcc.Store(id="app-state", storage_type="session"),
            # Store for active page
            dcc.Store(id="active-page", data="manage"),
            # Store for navbar collapsed state
            dcc.Store(id="navbar-collapsed", data=False),
            # Store for aside collapsed state
            dcc.Store(id="aside-collapsed", data=False),
            # Download component for exporting state
            dcc.Download(id="download-state"),
            # Upload component for importing state
            dcc.Upload(
                id="upload-state",
                children=html.Div(id="upload-state-trigger"),
                style={"display": "none"},
            ),
            # Modal for import confirmation
            dmc.Modal(
                id="import-modal",
                title="Import Application State",
                children=[
                    dmc.Stack(
                        [
                            dmc.Text("Click or drag and drop a state file to import:"),
                            dcc.Upload(
                                id="upload-state-file",
                                children=dmc.Card(
                                    [
                                        dmc.Center(
                                            [
                                                dmc.Stack(
                                                    [
                                                        DashIconify(
                                                            icon="carbon:upload",
                                                            width=48,
                                                            height=48,
                                                            color="gray",
                                                        ),
                                                        dmc.Text("Click or Drag & Drop", fw=500),
                                                        dmc.Text(
                                                            "Upload .json state file",
                                                            size="sm",
                                                            c="dimmed",
                                                        ),
                                                    ],
                                                    align="center",
                                                    gap="xs",
                                                )
                                            ],
                                            style={"height": 150},
                                        )
                                    ],
                                    withBorder=True,
                                    radius="md",
                                    style={"cursor": "pointer"},
                                ),
                                multiple=False,
                            ),
                            html.Div(id="import-status"),
                        ],
                        gap="md",
                    )
                ],
                size="lg",
            ),
        ],
    ),
)


# ==============================================================================
# NAVBAR AND ASIDE TOGGLE CALLBACKS
# ==============================================================================


@callback(
    Output("navbar-collapsed", "data"),
    Input("navbar-toggle", "n_clicks"),
    State("navbar-collapsed", "data"),
    prevent_initial_call=True,
)
def toggle_navbar(n_clicks, collapsed):
    """Toggle navbar collapsed state."""
    if n_clicks:
        return not collapsed
    return collapsed


@callback(
    Output("aside-collapsed", "data"),
    Input("aside-toggle", "n_clicks"),
    State("aside-collapsed", "data"),
    prevent_initial_call=True,
)
def toggle_aside(n_clicks, collapsed):
    """Toggle aside collapsed state."""
    if n_clicks:
        return not collapsed
    return collapsed


@callback(
    Output("app-shell", "navbar"),
    Input("navbar-collapsed", "data"),
)
def update_navbar_state(collapsed):
    """Update navbar collapsed state in AppShell."""
    return {
        "width": 250,
        "breakpoint": "sm",
        "collapsed": {"mobile": collapsed, "desktop": collapsed},
    }


@callback(
    Output("app-shell", "aside"),
    Input("aside-collapsed", "data"),
)
def update_aside_state(collapsed):
    """Update aside collapsed state in AppShell."""
    return {
        "width": 300,
        "breakpoint": "md",
        "collapsed": {"mobile": collapsed, "desktop": collapsed},
    }


# ==============================================================================
# PAGE CONTENT LOADER
# ==============================================================================


@callback(
    Output("page-content", "children"),
    Input("active-page", "data"),
)
def load_page_content(page):
    """Load content for the selected page."""
    # Data pages
    if page == "manage":
        return manage.layout()
    elif page == "view":
        return view.layout()
    elif page == "explore":
        return explore.layout()
    elif page == "transform":
        return transform.layout()
    elif page == "visualize":
        return visualize.layout()
    elif page == "pivot":
        return pivot.layout()
    elif page == "combine":
        return combine.layout()
    elif page == "report":
        return report.layout()
    # Design pages
    elif page == "doe":
        return doe.layout()
    elif page == "sampling":
        return sampling.layout()
    elif page == "sample_size":
        return sample_size.layout()
    elif page == "sample_size_comp":
        return sample_size_comp.layout()
    elif page == "randomizer":
        return randomizer.layout()
    # Model pages - Estimate
    elif page == "linear-regression":
        return linear_regression.layout()
    elif page == "logistic-regression":
        return logistic_regression.layout()
    elif page == "multinomial-logit":
        return multinomial_logit.layout()
    elif page == "naive-bayes":
        return naive_bayes.layout()
    elif page == "neural-network":
        return neural_network.layout()
    # Model pages - Trees
    elif page == "decision-tree":
        return decision_tree.layout()
    elif page == "random-forest":
        return random_forest.layout()
    elif page == "gradient-boosting":
        return gradient_boosting.layout()
    # Model pages - Evaluate
    elif page == "evaluate-regression":
        return evaluate_regression.layout()
    elif page == "evaluate-classification":
        return evaluate_classification.layout()
    # Model pages - Other
    elif page == "collaborative-filtering":
        return collaborative_filtering.layout()
    elif page == "decision-analysis":
        return decision_analysis.layout()
    elif page == "simulator":
        return simulator.layout()
    # Multivariate pages
    elif page == "pre-factor":
        return pre_factor.layout()
    elif page == "full-factor":
        return full_factor.layout()
    elif page == "kmeans-cluster":
        return kmeans_cluster.layout()
    elif page == "hierarchical-cluster":
        return hierarchical_cluster.layout()
    elif page == "perceptual-map":
        return perceptual_map.layout()
    elif page == "mds":
        return mds.layout()
    elif page == "conjoint":
        return conjoint.layout()
    # Basics pages
    elif page == "single-mean":
        return single_mean.layout()
    elif page == "compare-means":
        return compare_means.layout()
    elif page == "single-prop":
        return single_prop.layout()
    elif page == "compare-props":
        return compare_props.layout()
    elif page == "cross-tabs":
        return cross_tabs.layout()
    elif page == "goodness":
        return goodness.layout()
    elif page == "correlation":
        return correlation.layout()
    elif page == "clt":
        return clt.layout()
    elif page == "prob-calc":
        return prob_calc.layout()
    else:
        return dmc.Center(dmc.Text("Page not found", size="xl", c="dimmed"), style={"height": "50vh"})


@callback(
    Output("active-page", "data"),
    Input({"type": "nav-link", "index": ALL}, "n_clicks"),
    State({"type": "nav-link", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def update_active_page(n_clicks, ids):
    """Update active page based on navigation clicks."""
    if not ctx.triggered or not any(n_clicks):
        return dash.no_update

    # Find which button was clicked
    button_id = ctx.triggered_id
    if button_id and "index" in button_id:
        return button_id["index"]

    return dash.no_update


@callback(
    Output("dataset-selector", "data"),
    Output("dataset-selector", "value"),
    Input("app-state", "modified_timestamp"),
    State("dataset-selector", "value"),
)
def update_dataset_selector(ts, current_value):
    """Update dataset selector dropdown options."""
    datasets = data_manager.get_dataset_names()
    data = [{"label": name, "value": name} for name in datasets]

    # Set value to active dataset or current selection
    active = data_manager.get_active_dataset_name()
    value = current_value if current_value in datasets else active

    return data, value


@callback(
    Output("dataset-rows-badge", "children"),
    Output("dataset-cols-badge", "children"),
    Output("active-dataset-display", "children"),
    Output("dataset-memory", "children"),
    Input("dataset-selector", "value"),
)
def update_dataset_info(dataset_name):
    """Update dataset information display."""
    if not dataset_name:
        return "0 rows", "0 cols", "No dataset selected", ""

    data_manager.set_active_dataset(dataset_name)
    info = data_manager.get_dataset_info(dataset_name)

    rows = info.get("rows", 0)
    cols = info.get("columns", 0)
    memory = info.get("memory_usage", 0)

    return (
        f"{rows:,} rows",
        f"{cols} cols",
        f"Dataset: {dataset_name}",
        f"Memory: {memory:.2f} MB",
    )


# ==============================================================================
# STATE EXPORT/IMPORT
# ==============================================================================


@callback(
    Output("download-state", "data"),
    Input("export-state-btn", "n_clicks"),
    State("app-state", "data"),
    State("active-page", "data"),
    State("navbar-collapsed", "data"),
    State("aside-collapsed", "data"),
    State("dataset-selector", "value"),
    prevent_initial_call=True,
)
def export_state(n_clicks, app_state, active_page, navbar_collapsed, aside_collapsed, active_dataset):
    """Export complete application state including all datasets to JSON file."""
    if not n_clicks:
        return dash.no_update

    # Get complete data manager state (includes all datasets)
    data_state = data_manager.export_all_state()

    # Collect all UI state information
    state = {
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "ui_state": {
            "app_state": app_state or {},
            "active_page": active_page,
            "navbar_collapsed": navbar_collapsed,
            "aside_collapsed": aside_collapsed,
            "active_dataset": active_dataset,
        },
        "data_state": data_state,
        "page_count": 8,
        "feature_flags": {
            "collapsible_panels": True,
            "state_export_import": True,
        },
    }

    # Create filename with timestamp
    filename = f"aiml_complete_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return dict(
        content=json.dumps(state, indent=2),
        filename=filename,
    )


@callback(
    Output("import-modal", "opened"),
    Input("import-state-btn", "n_clicks"),
    State("import-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_import_modal(n_clicks, is_open):
    """Toggle the import modal."""
    if n_clicks:
        return not is_open
    return dash.no_update


@callback(
    Output("app-state", "data", allow_duplicate=True),
    Output("active-page", "data", allow_duplicate=True),
    Output("navbar-collapsed", "data", allow_duplicate=True),
    Output("aside-collapsed", "data", allow_duplicate=True),
    Output("dataset-selector", "value", allow_duplicate=True),
    Output("import-status", "children"),
    Output("import-modal", "opened", allow_duplicate=True),
    Input("upload-state-file", "contents"),
    State("upload-state-file", "filename"),
    prevent_initial_call=True,
)
def import_state(contents, filename):
    """Import complete application state including all datasets from JSON file."""
    if not contents:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            "",
            dash.no_update,
        )

    try:
        # Decode the uploaded file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        state = json.loads(decoded.decode("utf-8"))

        # Validate state structure
        version = state.get("version", "1.0")

        # Handle both old (v1.0) and new (v2.0) formats
        if version.startswith("2."):
            # New format with complete data state
            ui_state = state.get("ui_state", {})
            data_state = state.get("data_state", {})

            # Restore all datasets
            success, msg = data_manager.import_all_state(data_state)
            if not success:
                raise ValueError(msg)

            # Extract UI state components
            app_state = ui_state.get("app_state", {})
            active_page = ui_state.get("active_page", "manage")
            navbar_collapsed = ui_state.get("navbar_collapsed", False)
            aside_collapsed = ui_state.get("aside_collapsed", False)
            active_dataset = ui_state.get("active_dataset")

        elif version.startswith("1."):
            # Old format - basic state only
            app_state = state.get("app_state", {})
            active_page = state.get("active_page", "manage")
            navbar_collapsed = state.get("navbar_collapsed", False)
            aside_collapsed = state.get("aside_collapsed", False)
            active_dataset = state.get("active_dataset")
            msg = "Imported state (v1.0 - datasets not included)"
        else:
            raise ValueError(f"Unknown state version: {version}")

        # Validate dataset exists
        available_datasets = data_manager.get_dataset_names()
        if active_dataset and active_dataset not in available_datasets:
            active_dataset = available_datasets[0] if available_datasets else None

        dataset_count = len(available_datasets)
        success_msg = dmc.Alert(
            [
                dmc.Text("State imported successfully!", fw=500),
                dmc.Text(f"Restored {dataset_count} dataset(s)", size="sm"),
                dmc.Text(f"Version: {version}", size="xs", c="gray"),
            ],
            title="Import Successful",
            color="green",
            icon=DashIconify(icon="carbon:checkmark"),
        )

        # Close modal and restore state
        return (
            app_state,
            active_page,
            navbar_collapsed,
            aside_collapsed,
            active_dataset,
            success_msg,
            False,
        )

    except Exception as e:
        error_msg = dmc.Alert(
            [
                dmc.Text("Failed to import state", fw=500),
                dmc.Text(f"Error: {str(e)}", size="sm"),
                dmc.Text(
                    "Please ensure you're importing a valid AIML state file",
                    size="xs",
                    c="gray",
                ),
            ],
            title="Import Failed",
            color="red",
            icon=DashIconify(icon="carbon:warning"),
        )
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            error_msg,
            dash.no_update,
        )


# ==============================================================================
# RUN APPLICATION
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AIML Data - Python Dash Application")
    print("=" * 70)
    print("\nStarting application...")
    print(f"Available datasets: {', '.join(data_manager.get_dataset_names())}")
    print("\nNavigate to: http://localhost:8050")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    app.run(debug=True, host="0.0.0.0", port=8050)
