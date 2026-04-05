#!/usr/bin/env python3
"""Runtime entrypoint for AIML Dash."""

from pathlib import Path

from aiml_dash.app import create_app
from aiml_dash.utils.config import get_settings


def main() -> None:
    """Start the AIML Dash application."""
    settings = get_settings()
    app = create_app(settings=settings)

    print("Starting AIML Dash application...")
    print(f"Navigate to: http://{settings.host}:{settings.port}")
    print("\nPress Ctrl+C to stop the server\n")

    plugins_path = Path(__file__).resolve().parent / "plugins"

    if settings.debug:
        from aiml_dash.plugins.hot_reload import create_hot_reloader

        reloader = create_hot_reloader(plugins_path)
        if reloader is not None:
            with reloader:
                app.run(debug=settings.debug, host=settings.host, port=settings.port)
            return

    app.run(debug=settings.debug, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()

