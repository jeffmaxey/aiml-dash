"""Runtime behavior tests for plugin callback loading and hot reloading."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest

from aiml_dash.plugins.hot_reload import reload_plugin_module

CALLBACK_MODULE_CASES = [
    (
        "aiml_dash.plugins.data_plugin.callbacks",
        "aiml_dash.pages.data",
    ),
    (
        "aiml_dash.plugins.design_plugin.callbacks",
        "aiml_dash.pages.design",
    ),
    (
        "aiml_dash.plugins.model_plugin.callbacks",
        "aiml_dash.pages.model",
    ),
    (
        "aiml_dash.plugins.multivariate_plugin.callbacks",
        "aiml_dash.pages.multivariate",
    ),
]


@pytest.mark.parametrize(("module_path", "pages_package"), CALLBACK_MODULE_CASES)
def test_import_page_modules_uses_deterministic_order(
    module_path: str, pages_package: str
) -> None:
    """Ensure discovered callback modules are imported in sorted order."""
    module = importlib.import_module(module_path)

    fake_package = SimpleNamespace(__path__=["/tmp/pages"])
    discovered = [
        SimpleNamespace(name=f"{pages_package}.zeta"),
        SimpleNamespace(name=f"{pages_package}.alpha"),
        SimpleNamespace(name=f"{pages_package}.middle"),
    ]

    imported_modules: list[str] = []

    def fake_import_module(name: str) -> object:
        imported_modules.append(name)
        if name == pages_package:
            return fake_package
        return object()

    with (
        patch(f"{module_path}.import_module", side_effect=fake_import_module),
        patch(f"{module_path}.iter_modules", return_value=discovered),
    ):
        module._import_page_modules()

    assert imported_modules == [
        pages_package,
        f"{pages_package}.alpha",
        f"{pages_package}.middle",
        f"{pages_package}.zeta",
    ]


@pytest.mark.parametrize(("module_path", "_pages_package"), CALLBACK_MODULE_CASES)
def test_register_callbacks_invokes_page_import(
    module_path: str, _pages_package: str
) -> None:
    """Ensure register_callbacks triggers callback module import."""
    module = importlib.import_module(module_path)
    with patch.object(module, "_import_page_modules") as import_pages:
        module.register_callbacks(object())
    import_pages.assert_called_once_with()


def test_reload_plugin_module_reloads_loaded_page_modules() -> None:
    """Ensure hot reload includes loaded nested submodules."""
    plugin_id = "unit_test_plugin"
    plugins_package = "test.plugins"
    module_path = f"{plugins_package}.{plugin_id}"
    module_names = [
        module_path,
        f"{module_path}.callbacks",
        f"{module_path}.alpha",
        f"{module_path}.beta",
    ]

    created_modules: dict[str, ModuleType] = {}
    for name in module_names:
        module = ModuleType(name)
        sys.modules[name] = module
        created_modules[name] = module

    try:
        with patch("aiml_dash.plugins.hot_reload.importlib.reload") as mock_reload:
            assert reload_plugin_module(plugin_id, plugins_package=plugins_package)

        reloaded_names = [args[0].__name__ for args, _ in mock_reload.call_args_list]
        assert reloaded_names == [
            f"{module_path}.alpha",
            f"{module_path}.beta",
            f"{module_path}.callbacks",
            module_path,
        ]
    finally:
        for name in created_modules:
            sys.modules.pop(name, None)
