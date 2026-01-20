"""Plugin-related controller logic."""

from __future__ import annotations

import base64
import binascii
import json


def get_locked_plugins(metadata: list[dict[str, object]] | None) -> set[str]:
    """
    Return a set of locked plugin identifiers.
    
    Args:
        metadata: List of plugin metadata dictionaries
        
    Returns:
        Set of locked plugin IDs
    """
    return {
        plugin.get("id")
        for plugin in (metadata or [])
        if plugin.get("id") and plugin.get("locked")
    }


def is_plugin_enabled(plugin_id: str, enabled_plugins: list[str] | None, metadata: list[dict[str, object]] | None) -> bool:
    """
    Check if a plugin is enabled.
    
    Args:
        plugin_id: Plugin identifier
        enabled_plugins: List of enabled plugin IDs
        metadata: List of plugin metadata
        
    Returns:
        True if plugin is enabled or locked
    """
    enabled = set(enabled_plugins or [])
    
    # Check if plugin is in enabled list
    if plugin_id in enabled:
        return True
        
    # Check if plugin is locked
    if metadata:
        for plugin in metadata:
            if plugin.get("id") == plugin_id and plugin.get("locked"):
                return True
                
    return False


def process_plugin_metadata(metadata: list[dict[str, object]] | None, enabled_plugins: list[str] | None) -> list[dict[str, object]]:
    """
    Process plugin metadata and add enabled status.
    
    Args:
        metadata: List of plugin metadata dictionaries
        enabled_plugins: List of enabled plugin IDs
        
    Returns:
        Processed metadata with enabled status
    """
    if not metadata:
        return []
        
    enabled = set(enabled_plugins or [])
    
    return [
        {
            **plugin.copy(),
            "enabled": plugin.get("id") in enabled or bool(plugin.get("locked"))
        }
        for plugin in metadata
    ]


def decode_enabled_plugins(encoded_data: str | None) -> list[str] | None:
    """
    Decode base64 encoded plugin list.
    
    Args:
        encoded_data: Base64 encoded JSON string
        
    Returns:
        List of plugin IDs or None if decoding fails
    """
    if not encoded_data:
        return None
        
    try:
        decoded = base64.b64decode(encoded_data)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError, binascii.Error):
        return None


def encode_enabled_plugins(plugins: list[str]) -> str:
    """
    Encode plugin list to base64.
    
    Args:
        plugins: List of plugin IDs
        
    Returns:
        Base64 encoded JSON string
    """
    return base64.b64encode(json.dumps(plugins).encode()).decode()
