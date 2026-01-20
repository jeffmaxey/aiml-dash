"""Standalone plugin runner for AIML Dash.

This module allows plugins to be run independently of the main application
for development and testing purposes. It creates a minimal Dash app that
displays the plugin's layout.

Usage:
    python -m aiml_dash.plugins.standalone example
    python -m aiml_dash.plugins.standalone template
"""

import sys
from pathlib import Path

import dash
import dash_mantine_components as dmc
from dash import html

from aiml_dash.plugins.loader import load_plugin
from aiml_dash.plugins.models import Plugin


def create_standalone_app(plugin: Plugin) -> dash.Dash:
    """Create a standalone Dash app for a plugin.

    Args:
        plugin: The plugin to run standalone.

    Returns:
        dash.Dash: A configured Dash application with the plugin's layout.
    """
    app = dash.Dash(
        __name__,
        title=f"{plugin.name} - Standalone",
        external_stylesheets=["https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"],
    )

    # Create a simple layout with the plugin's first page
    if not plugin.pages:
        app.layout = dmc.MantineProvider(
            dmc.Container(
                dmc.Alert(
                    "This plugin has no pages defined.",
                    title="No Pages",
                    color="yellow",
                ),
                size="sm",
                py="xl",
            )
        )
    else:
        page = plugin.pages[0]

        app.layout = dmc.MantineProvider(
            theme={
                "fontFamily": "'Inter', sans-serif",
                "primaryColor": "blue",
            },
            children=dmc.Box(
                [
                    # Header
                    dmc.Paper(
                        dmc.Container(
                            dmc.Group(
                                [
                                    dmc.Title(f"{plugin.name} - Standalone Mode", order=3),
                                    dmc.Badge(f"v{plugin.version}", variant="light"),
                                ],
                                justify="space-between",
                            ),
                            size="xl",
                            py="md",
                        ),
                        shadow="sm",
                        mb="md",
                    ),
                    # Plugin content
                    html.Div(id="plugin-content", children=page.layout()),
                    # Footer
                    dmc.Paper(
                        dmc.Container(
                            dmc.Text(
                                f"Plugin: {plugin.id} | Page: {page.label}",
                                size="sm",
                                c="dimmed",
                                ta="center",
                            ),
                            size="xl",
                            py="sm",
                        ),
                        mt="xl",
                    ),
                ]
            ),
        )

    # Register plugin callbacks if available
    if plugin.register_callbacks:
        plugin.register_callbacks(app)

    return app


def run_plugin_standalone(plugin_id: str, debug: bool = True, port: int = 8050):
    """Run a plugin in standalone mode.

    Args:
        plugin_id: The ID of the plugin to run.
        debug: Whether to run in debug mode.
        port: The port to run the server on.
    """
    # Get the plugins directory
    plugins_path = Path(__file__).parent

    # Find the plugin directory
    plugin_dir = plugins_path / plugin_id

    if not plugin_dir.exists():
        print(f"Error: Plugin directory '{plugin_id}' not found at {plugin_dir}")
        print(f"\nAvailable plugins in {plugins_path}:")
        for item in plugins_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and (item / "__init__.py").exists():
                print(f"  - {item.name}")
        sys.exit(1)

    # Load the plugin
    print(f"Loading plugin: {plugin_id}")
    plugin = load_plugin(plugin_dir, "aiml_dash.plugins")

    if plugin is None:
        print(f"Error: Failed to load plugin '{plugin_id}'")
        print("Make sure the plugin has a valid get_plugin() function.")
        sys.exit(1)

    print(f"Successfully loaded: {plugin.name} v{plugin.version}")
    print(f"Description: {plugin.description}")
    print(f"Pages: {len(plugin.pages)}")

    # Create and run the app
    app = create_standalone_app(plugin)

    print(f"\nStarting standalone server on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server\n")

    app.run(debug=debug, host="127.0.0.1", port=port)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m aiml_dash.plugins.standalone <plugin_id> [--port PORT]")
        print("\nExample: python -m aiml_dash.plugins.standalone example")
        sys.exit(1)

    plugin_id = sys.argv[1]
    port = 8050

    # Parse optional arguments
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port") + 1
        if port_idx < len(sys.argv):
            try:
                port = int(sys.argv[port_idx])
            except ValueError:
                print(f"Error: Invalid port number '{sys.argv[port_idx]}'")
                sys.exit(1)

    run_plugin_standalone(plugin_id, debug=True, port=port)
