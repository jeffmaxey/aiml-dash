#!/usr/bin/env python3
"""
Test script for AIML Dash application
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

if __name__ == "__main__":
    print("Starting AIML Dash application...")
    print("Navigate to: http://localhost:8050")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host="127.0.0.1", port=8050)
