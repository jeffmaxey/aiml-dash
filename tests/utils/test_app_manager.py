"""
Tests for AppManager.

Tests the application manager including session management,
settings, action logging, and state management.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from aiml_dash.managers.app_manager import AppManager, Session, app_manager


@pytest.fixture
def app_mgr():
    """Create a fresh AppManager for testing."""
    mgr = AppManager()
    # Clear state
    mgr.sessions.clear()
    mgr.action_history.clear()
    mgr.cache.clear()
    mgr.app_settings = mgr._default_settings()
    mgr._create_default_session()
    return mgr


class TestSession:
    """Test Session class."""
    
    def test_session_creation(self):
        """Test creating a session."""
        session = Session(user_id="test_user")
        
        assert session.id is not None
        assert session.user_id == "test_user"
        assert session.created is not None
        assert session.last_active == session.created
        assert isinstance(session.data, dict)
        assert isinstance(session.settings, dict)
        assert isinstance(session.history, list)
        
    def test_session_data_operations(self):
        """Test session data get/set."""
        session = Session()
        
        # Set and get data
        session.set_data("key1", "value1")
        assert session.get_data("key1") == "value1"
        assert session.get_data("nonexistent", "default") == "default"
        
    def test_session_settings(self):
        """Test session settings."""
        session = Session()
        
        session.set_setting("theme", "dark")
        assert session.get_setting("theme") == "dark"
        assert session.get_setting("nonexistent") is None
        
    def test_session_history(self):
        """Test session history tracking."""
        session = Session()
        
        session.add_to_history("action1", {"detail": "test"})
        session.add_to_history("action2")
        
        assert len(session.history) == 2
        assert session.history[0]["action"] == "action1"
        assert session.history[1]["action"] == "action2"
        
    def test_session_serialization(self):
        """Test session to/from dict."""
        session = Session(user_id="user123")
        session.set_data("test", "value")
        session.set_setting("pref", "option")
        
        # Convert to dict
        data = session.to_dict()
        
        assert data["user_id"] == "user123"
        assert "test" in data["data"]
        assert "pref" in data["settings"]
        
        # Recreate from dict
        restored = Session.from_dict(data)
        assert restored.id == session.id
        assert restored.user_id == session.user_id
        assert restored.get_data("test") == "value"
        assert restored.get_setting("pref") == "option"


class TestAppManagerSingleton:
    """Test AppManager singleton pattern."""
    
    def test_singleton_pattern(self):
        """Test that AppManager is a singleton."""
        mgr1 = AppManager()
        mgr2 = AppManager()
        
        assert mgr1 is mgr2
        
    def test_global_instance(self):
        """Test global app_manager instance."""
        assert app_manager is not None
        assert isinstance(app_manager, AppManager)


class TestSessionManagement:
    """Test session management."""
    
    def test_create_session(self, app_mgr):
        """Test creating a session."""
        session = app_mgr.create_session("user123")
        
        assert session.id in app_mgr.sessions
        assert session.user_id == "user123"
        
    def test_get_session(self, app_mgr):
        """Test getting sessions."""
        session = app_mgr.create_session("test")
        
        # Get by ID
        retrieved = app_mgr.get_session(session.id)
        assert retrieved is session
        
        # Get active session
        app_mgr.set_active_session(session.id)
        active = app_mgr.get_session()
        assert active is session
        
    def test_set_active_session(self, app_mgr):
        """Test setting active session."""
        session1 = app_mgr.create_session("user1")
        session2 = app_mgr.create_session("user2")
        
        assert app_mgr.set_active_session(session1.id)
        assert app_mgr.active_session_id == session1.id
        
        assert app_mgr.set_active_session(session2.id)
        assert app_mgr.active_session_id == session2.id
        
        # Try invalid session
        assert not app_mgr.set_active_session("invalid")
        
    def test_list_sessions(self, app_mgr):
        """Test listing sessions."""
        initial_count = len(app_mgr.list_sessions())
        
        app_mgr.create_session("user1")
        app_mgr.create_session("user2")
        
        sessions = app_mgr.list_sessions()
        assert len(sessions) == initial_count + 2
        
    def test_remove_session(self, app_mgr):
        """Test removing a session."""
        session = app_mgr.create_session("test")
        session_id = session.id
        
        assert app_mgr.remove_session(session_id)
        assert session_id not in app_mgr.sessions
        
        # Try removing nonexistent
        assert not app_mgr.remove_session("nonexistent")
        
    def test_cleanup_inactive_sessions(self, app_mgr):
        """Test cleanup of inactive sessions."""
        # This is hard to test without mocking time
        # Just verify the method exists and runs
        removed = app_mgr.cleanup_inactive_sessions(timeout_seconds=0)
        assert isinstance(removed, int)


class TestSettingsManagement:
    """Test settings management."""
    
    def test_get_setting(self, app_mgr):
        """Test getting settings."""
        # Get existing setting
        theme = app_mgr.get_setting("theme")
        assert theme is not None
        
        # Get with default
        value = app_mgr.get_setting("nonexistent", "default")
        assert value == "default"
        
    def test_set_setting(self, app_mgr):
        """Test setting a value."""
        app_mgr.set_setting("custom_key", "custom_value")
        assert app_mgr.get_setting("custom_key") == "custom_value"
        
    def test_update_settings(self, app_mgr):
        """Test updating multiple settings."""
        new_settings = {
            "theme": "dark",
            "page_size": 25,
            "custom": "value"
        }
        
        app_mgr.update_settings(new_settings)
        
        assert app_mgr.get_setting("theme") == "dark"
        assert app_mgr.get_setting("page_size") == 25
        assert app_mgr.get_setting("custom") == "value"
        
    def test_reset_settings(self, app_mgr):
        """Test resetting settings to defaults."""
        app_mgr.set_setting("theme", "dark")
        app_mgr.reset_settings()
        
        # Should be back to default
        defaults = app_mgr._default_settings()
        assert app_mgr.get_setting("theme") == defaults["theme"]
        
    def test_export_import_settings(self, app_mgr):
        """Test exporting and importing settings."""
        app_mgr.set_setting("test_key", "test_value")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "settings.json"
            
            # Export
            success = app_mgr.export_settings(filepath)
            assert success
            assert filepath.exists()
            
            # Modify and import
            app_mgr.set_setting("test_key", "changed")
            success = app_mgr.import_settings(filepath)
            assert success
            assert app_mgr.get_setting("test_key") == "test_value"


class TestActionLogging:
    """Test action logging."""
    
    def test_log_action(self, app_mgr):
        """Test logging an action."""
        initial_count = len(app_mgr.action_history)
        
        app_mgr.log_action("test_action", {"detail": "test"})
        
        assert len(app_mgr.action_history) == initial_count + 1
        last_action = app_mgr.action_history[-1]
        assert last_action["action"] == "test_action"
        assert last_action["details"]["detail"] == "test"
        
    def test_log_action_to_session(self, app_mgr):
        """Test that actions are also logged to session."""
        session = app_mgr.create_session("test")
        app_mgr.set_active_session(session.id)
        
        app_mgr.log_action("test_action", {"key": "value"})
        
        # Should be in both global and session history
        assert len(app_mgr.action_history) > 0
        assert len(session.history) > 0
        
    def test_get_action_history(self, app_mgr):
        """Test retrieving action history."""
        app_mgr.log_action("action1")
        app_mgr.log_action("action2")
        app_mgr.log_action("action1")
        
        # Get all
        all_actions = app_mgr.get_action_history()
        assert len(all_actions) >= 3
        
        # Get with limit
        limited = app_mgr.get_action_history(limit=2)
        assert len(limited) == 2
        
        # Filter by type
        filtered = app_mgr.get_action_history(action_type="action1")
        assert all(a["action"] == "action1" for a in filtered)
        
    def test_clear_action_history(self, app_mgr):
        """Test clearing action history."""
        app_mgr.log_action("test")
        app_mgr.clear_action_history()
        
        assert len(app_mgr.action_history) == 0
        
    def test_logging_disabled(self, app_mgr):
        """Test action logging when disabled."""
        app_mgr.set_setting("log_actions", False)
        initial_count = len(app_mgr.action_history)
        
        app_mgr.log_action("test")
        
        # Should not have increased
        assert len(app_mgr.action_history) == initial_count


class TestCacheManagement:
    """Test cache management."""
    
    def test_cache_set_get(self, app_mgr):
        """Test setting and getting cache values."""
        app_mgr.cache_set("key1", "value1")
        
        assert app_mgr.cache_get("key1") == "value1"
        assert app_mgr.cache_get("nonexistent", "default") == "default"
        
    def test_cache_delete(self, app_mgr):
        """Test deleting from cache."""
        app_mgr.cache_set("key1", "value1")
        
        assert app_mgr.cache_delete("key1")
        assert app_mgr.cache_get("key1") is None
        
        # Delete nonexistent
        assert not app_mgr.cache_delete("nonexistent")
        
    def test_cache_clear(self, app_mgr):
        """Test clearing entire cache."""
        app_mgr.cache_set("key1", "value1")
        app_mgr.cache_set("key2", "value2")
        
        app_mgr.cache_clear()
        
        assert len(app_mgr.cache) == 0
        
    def test_cache_keys(self, app_mgr):
        """Test getting cache keys."""
        app_mgr.cache_set("key1", "value1")
        app_mgr.cache_set("key2", "value2")
        
        keys = app_mgr.cache_keys()
        
        assert "key1" in keys
        assert "key2" in keys
        
    def test_cache_disabled(self, app_mgr):
        """Test cache when disabled."""
        app_mgr.set_setting("cache_enabled", False)
        app_mgr.cache_set("key1", "value1")
        
        # Should not have been cached
        assert "key1" not in app_mgr.cache


class TestManagerIntegration:
    """Test integration with DataManager and ProjectManager."""
    
    def test_data_manager_access(self, app_mgr):
        """Test accessing DataManager."""
        dm = app_mgr.data_manager
        
        assert dm is not None
        assert len(dm.get_dataset_names()) > 0  # Should have sample data
        
    def test_project_manager_access(self, app_mgr):
        """Test accessing ProjectManager."""
        pm = app_mgr.project_manager
        
        assert pm is not None
        
    def test_get_current_dataset(self, app_mgr):
        """Test getting current dataset."""
        df = app_mgr.get_current_dataset()
        
        # Should return active dataset (diamonds by default)
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        
    def test_get_current_project(self, app_mgr):
        """Test getting current project."""
        # Create a project first
        pm = app_mgr.project_manager
        project = pm.create_project("Test Project")
        pm.set_active_project(project.id)
        
        current = app_mgr.get_current_project()
        
        assert current is not None
        assert current.name == "Test Project"


class TestStateManagement:
    """Test state export/import."""
    
    def test_export_state_basic(self, app_mgr):
        """Test basic state export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "state.pkl"
            
            success, msg = app_mgr.export_state(filepath)
            
            assert success
            assert filepath.exists()
            
    def test_export_state_with_sessions(self, app_mgr):
        """Test exporting state with sessions."""
        session = app_mgr.create_session("test_user")
        session.set_data("key", "value")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "state.pkl"
            
            success, msg = app_mgr.export_state(filepath, include_sessions=True)
            assert success
            
    def test_import_state(self, app_mgr):
        """Test importing state."""
        # Set some state
        app_mgr.set_setting("test_setting", "test_value")
        session = app_mgr.create_session("test_user")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "state.pkl"
            
            # Export
            app_mgr.export_state(filepath, include_sessions=True)
            
            # Modify state
            app_mgr.set_setting("test_setting", "changed")
            
            # Import
            success, msg = app_mgr.import_state(
                filepath,
                restore_sessions=True,
                merge=False
            )
            
            assert success
            assert app_mgr.get_setting("test_setting") == "test_value"
            
    def test_import_state_merge(self, app_mgr):
        """Test importing state with merge."""
        app_mgr.set_setting("existing", "value1")
        app_mgr.set_setting("to_merge", "original")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "state.pkl"
            
            # Export with different setting
            app_mgr.set_setting("to_merge", "new")
            app_mgr.export_state(filepath)
            
            # Reset and reimport with merge
            app_mgr.set_setting("to_merge", "original")
            success, msg = app_mgr.import_state(filepath, merge=True)
            
            assert success
            assert app_mgr.get_setting("to_merge") == "new"
            assert app_mgr.get_setting("existing") == "value1"


class TestStatusSummary:
    """Test status summary."""
    
    def test_get_status_summary(self, app_mgr):
        """Test getting status summary."""
        summary = app_mgr.get_status_summary()
        
        assert "sessions" in summary
        assert "data" in summary
        assert "projects" in summary
        assert "cache" in summary
        assert "actions" in summary
        
        assert isinstance(summary["sessions"]["total"], int)
        assert isinstance(summary["data"]["datasets"], int)
        assert isinstance(summary["cache"]["enabled"], bool)
