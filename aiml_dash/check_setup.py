#!/usr/bin/env python3
"""
Check that all dependencies and modules are properly installed
"""

import pkgutil
import sys
from importlib import import_module
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()


def _ensure_project_on_path() -> None:
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))


def check_imports() -> bool:
    """Verify required third-party packages can be imported."""
    required_packages = [
        ("dash", "Dash"),
        ("dash_mantine_components", "Dash Mantine Components"),
        ("dash_iconify", "Dash Iconify"),
        ("dash_ag_grid", "Dash AG Grid"),
        ("plotly", "Plotly"),
        ("pandas", "pandas"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("sqlalchemy", "SQLAlchemy"),
        ("flask_caching", "Flask-Caching"),
        ("flask_compress", "Flask-Compress"),
        ("flask_talisman", "Flask-Talisman"),
        ("pydantic", "Pydantic"),
        ("yaml", "PyYAML"),
        ("requests", "Requests"),
    ]

    print("Checking required packages...\n")
    all_ok = True

    for package, name in required_packages:
        try:
            import_module(package)
            print(f"✓ {name}")
        except ImportError as exc:
            print(f"✗ {name} - {exc}")
            all_ok = False

    return all_ok


def _discover_project_modules() -> list[str]:
    root_packages = ("components", "pages", "utils")
    discovered: list[str] = []

    for py_file in PROJECT_DIR.glob("*.py"):
        if py_file.stem != "__init__":
            discovered.append(py_file.stem)

    for package_name in root_packages:
        try:
            package = import_module(package_name)
            discovered.append(package_name)
        except Exception as exc:
            print(f"✗ Failed to import package '{package_name}' - {exc}")
            continue

        if hasattr(package, "__path__"):
            for _, module_name, _ in pkgutil.walk_packages(package.__path__, f"{package_name}."):
                discovered.append(module_name)

    seen: set[str] = set()
    ordered: list[str] = []
    for module_name in discovered:
        if module_name not in seen:
            seen.add(module_name)
            ordered.append(module_name)
    return ordered


def check_modules() -> bool:
    """Verify local modules can be imported."""
    print("\n\nChecking application modules...\n")
    all_ok = True

    for module_name in _discover_project_modules():
        try:
            import_module(module_name)
            print(f"✓ {module_name}")
        except Exception as exc:
            print(f"✗ {module_name} - {exc}")
            all_ok = False

    return all_ok


def main() -> int:
    """Run all checks."""
    _ensure_project_on_path()

    print("=" * 60)
    print("Radiant Dash - Dependency Check")
    print("=" * 60)

    packages_ok = check_imports()
    modules_ok = check_modules()

    print("\n" + "=" * 60)
    if packages_ok and modules_ok:
        print("✓ All checks passed!")
        print("\nYou can now run the application with:")
        print("  python run.py")
        return 0

    print("✗ Some checks failed.")
    print("\nPlease install missing dependencies:")
    print("  pip install -r requirements.txt")
    return 1


if __name__ == "__main__":
    sys.exit(main())
