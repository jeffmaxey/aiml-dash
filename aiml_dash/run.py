#!/usr/bin/env python3
"""
Test script for AIML Dash application
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dash_aiml.app import app
from dash_aiml.core.settings import app_settings

if __name__ == "__main__":
    print(f"Starting {app_settings.APP_TITLE} application...")
    print(f"Navigate to: http://{app_settings.HOST}:{app_settings.PORT}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=app_settings.DEBUG, host=app_settings.HOST, port=app_settings.PORT)
