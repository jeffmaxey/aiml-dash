#!/usr/bin/env python3
"""Runtime entrypoint for AIML Dash."""

from aiml_dash.app import create_app
from aiml_dash.utils.config import get_settings


def main() -> None:
    """Start the AIML Dash application."""
    settings = get_settings()
    app = create_app(settings=settings)

    print("Starting AIML Dash application...")
    print(f"Navigate to: http://{settings.host}:{settings.port}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=settings.debug, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()

