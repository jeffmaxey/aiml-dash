"""Tests for common components module."""

import pytest
from dash import html, dcc
import dash_mantine_components as dmc

from aiml_dash.components.common import (
    create_page_header,
    create_filter_section,
    create_variable_selector,
    create_function_selector,
    create_download_button,
    create_notification,
    create_code_display,
    create_tabs,
    create_info_card,
)


class TestCreatePageHeader:
    """Test create_page_header function."""

    def test_create_page_header_basic(self):
        """Test creating basic page header."""
        result = create_page_header("Test Page", "Test description")
        assert isinstance(result, dmc.Stack)

    def test_create_page_header_with_icon(self):
        """Test creating page header with custom icon."""
        result = create_page_header("Test Page", "Test description", icon="carbon:analytics")
        assert isinstance(result, dmc.Stack)


class TestCreateFilterSection:
    """Test create_filter_section function."""

    def test_create_filter_section(self):
        """Test creating filter section."""
        result = create_filter_section()
        assert isinstance(result, dmc.Accordion)


class TestCreateVariableSelector:
    """Test create_variable_selector function."""

    def test_create_variable_selector_multiple(self):
        """Test creating multi-select variable selector."""
        result = create_variable_selector("test-var", "Test Variable", multiple=True)
        assert isinstance(result, dmc.MultiSelect)
        assert result.id == "test-var"

    def test_create_variable_selector_single(self):
        """Test creating single-select variable selector."""
        result = create_variable_selector("test-var", "Test Variable", multiple=False)
        assert isinstance(result, dmc.Select)
        assert result.id == "test-var"

    def test_create_variable_selector_required(self):
        """Test creating required variable selector."""
        result = create_variable_selector("test-var", "Test Variable", required=True)
        assert result.required is True
        assert result.withAsterisk is True

    def test_create_variable_selector_with_description(self):
        """Test creating variable selector with description."""
        result = create_variable_selector("test-var", "Test Variable", description="Help text")
        assert result.description == "Help text"


class TestCreateFunctionSelector:
    """Test create_function_selector function."""

    def test_create_function_selector_basic(self):
        """Test creating basic function selector."""
        functions = {
            "mean": ("Mean", "Average value"),
            "sum": ("Sum", "Total sum"),
        }
        result = create_function_selector("test-func", functions)
        assert isinstance(result, dmc.MultiSelect)
        assert result.id == "test-func"

    def test_create_function_selector_with_defaults(self):
        """Test creating function selector with default values."""
        functions = {
            "mean": ("Mean", "Average value"),
            "sum": ("Sum", "Total sum"),
        }
        result = create_function_selector("test-func", functions, default=["mean"])
        assert result.value == ["mean"]

    def test_create_function_selector_custom_label(self):
        """Test creating function selector with custom label."""
        functions = {"mean": ("Mean", "Average value")}
        result = create_function_selector("test-func", functions, label="Custom Label")
        assert result.label == "Custom Label"


class TestCreateDownloadButton:
    """Test create_download_button function."""

    def test_create_download_button_basic(self):
        """Test creating basic download button."""
        result = create_download_button("test-btn")
        assert isinstance(result, dmc.Group)

    def test_create_download_button_custom_label(self):
        """Test creating download button with custom label."""
        result = create_download_button("test-btn", label="Export Data")
        assert isinstance(result, dmc.Group)

    def test_create_download_button_custom_icon(self):
        """Test creating download button with custom icon."""
        result = create_download_button("test-btn", icon="carbon:save")
        assert isinstance(result, dmc.Group)


class TestCreateNotification:
    """Test create_notification function."""

    def test_create_notification(self):
        """Test creating notification container."""
        result = create_notification("test-notif")
        assert isinstance(result, html.Div)
        assert result.id == "test-notif"


class TestCreateCodeDisplay:
    """Test create_code_display function."""

    def test_create_code_display_basic(self):
        """Test creating basic code display."""
        result = create_code_display("test-code")
        assert isinstance(result, dmc.Code)
        assert result.id == "test-code"

    def test_create_code_display_custom_language(self):
        """Test creating code display with custom language."""
        result = create_code_display("test-code", language="javascript")
        assert isinstance(result, dmc.Code)


class TestCreateTabs:
    """Test create_tabs function."""

    def test_create_tabs_basic(self):
        """Test creating basic tabs."""
        tabs_data = [
            {"value": "tab1", "label": "Tab 1", "children": html.Div("Content 1")},
            {"value": "tab2", "label": "Tab 2", "children": html.Div("Content 2")},
        ]
        result = create_tabs("test-tabs", tabs_data)
        assert isinstance(result, dmc.Tabs)
        assert result.id == "test-tabs"

    def test_create_tabs_with_icons(self):
        """Test creating tabs with icons."""
        tabs_data = [
            {"value": "tab1", "label": "Tab 1", "icon": "carbon:data-table", "children": html.Div("Content 1")},
            {"value": "tab2", "label": "Tab 2", "icon": "carbon:chart-line", "children": html.Div("Content 2")},
        ]
        result = create_tabs("test-tabs", tabs_data)
        assert isinstance(result, dmc.Tabs)

    def test_create_tabs_empty(self):
        """Test creating tabs with empty data."""
        result = create_tabs("test-tabs", [])
        assert isinstance(result, dmc.Tabs)
        assert result.value is None


class TestCreateInfoCard:
    """Test create_info_card function."""

    def test_create_info_card_basic(self):
        """Test creating basic info card."""
        result = create_info_card("Total", 100, "carbon:data-table")
        assert isinstance(result, dmc.Card)

    def test_create_info_card_with_color(self):
        """Test creating info card with custom color."""
        result = create_info_card("Total", 100, "carbon:data-table", color="red")
        assert isinstance(result, dmc.Card)

    def test_create_info_card_various_values(self):
        """Test creating info cards with various value types."""
        # Test with integer
        result1 = create_info_card("Count", 42, "carbon:number")
        assert isinstance(result1, dmc.Card)

        # Test with float
        result2 = create_info_card("Average", 3.14, "carbon:number")
        assert isinstance(result2, dmc.Card)

        # Test with string
        result3 = create_info_card("Status", "Active", "carbon:status")
        assert isinstance(result3, dmc.Card)
