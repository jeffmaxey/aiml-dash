#!/usr/bin/env python3
"""
Automated refactoring script to update all pages to use common components.
"""

import re
import os
from pathlib import Path


def refactor_file(filepath):
    """Refactor a single file to use common components."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    changes_made = []

    # 1. Check and update imports
    if "from components.common import" in content or "from aiml_dash.components.common import" in content:
        # File already imports from common, check if we need to add more imports
        import_additions = []

        if "create_control_card" not in content and "withBorder=True" in content:
            import_additions.append("create_control_card")
        if "create_results_card" not in content and "withBorder=True" in content:
            import_additions.append("create_results_card")
        if "create_action_button" not in content and "dmc.Button(" in content and "leftSection=" in content:
            import_additions.append("create_action_button")
        if "create_empty_state" not in content and "No dataset selected" in content:
            import_additions.append("create_empty_state")
        if "create_two_column_layout" not in content and "dmc.GridCol" in content:
            import_additions.append("create_two_column_layout")

        if import_additions:
            # Find the import statement and add new imports
            import_pattern = r"from (aiml_dash\.)?components\.common import \((.*?)\)"
            match = re.search(import_pattern, content, re.DOTALL)
            if match:
                prefix = match.group(1) or ""
                existing_imports = match.group(2)
                # Parse existing imports
                existing_list = [imp.strip() for imp in existing_imports.split(",") if imp.strip()]
                # Add new imports
                all_imports = sorted(set(existing_list + import_additions))
                new_import = f"from {prefix}components.common import (\n    " + ",\n    ".join(all_imports) + ",\n)"
                content = content.replace(match.group(0), new_import)
                changes_made.append(f"Added imports: {', '.join(import_additions)}")

    # 2. Replace data_manager with app_manager.data_manager (if not already done)
    if "from utils.data_manager import data_manager" in content:
        content = content.replace(
            "from utils.data_manager import data_manager", "from utils.app_manager import app_manager"
        )
        # Replace all data_manager. calls with app_manager.data_manager.
        content = re.sub(r"([^_])data_manager\.", r"\1app_manager.data_manager.", content)
        changes_made.append("Updated data_manager to app_manager")

    # 3. Replace simple empty state patterns
    # Pattern: dmc.Center with "No dataset selected" or similar
    empty_pattern = r'dmc\.Center\(\s*dmc\.Text\(([\'"](No .*?|Select .*?)[\'"])[^)]*\)[^)]*style=\{[^}]*\}[^)]*\)'
    if re.search(empty_pattern, content):

        def replace_empty(match):
            message = match.group(2)
            return f'create_empty_state(message="{message}")'

        content = re.sub(empty_pattern, replace_empty, content)
        changes_made.append("Replaced empty state patterns")

    # Save if changes were made
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, changes_made

    return False, []


def main():
    """Refactor all pages."""
    pages_dir = Path("/workspaces/aiml-dash/aiml_dash/pages")

    total_files = 0
    modified_files = 0

    print(f"Scanning {pages_dir}...")
    print()

    for py_file in pages_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        total_files += 1
        try:
            modified, changes = refactor_file(py_file)

            if modified:
                modified_files += 1
                print(f"✓ {py_file.relative_to(pages_dir)}")
                for change in changes:
                    print(f"  - {change}")
            else:
                print(f"- {py_file.relative_to(pages_dir)} (no changes)")
        except Exception as e:
            print(f"✗ {py_file.relative_to(pages_dir)} ERROR: {e}")

    print()
    print(f"Summary: {modified_files}/{total_files} files modified")


if __name__ == "__main__":
    main()
