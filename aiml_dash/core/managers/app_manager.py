"""
App Manager Utility
===================

Handles all settings, actions, and session management for the AIML Dash application.
Uses a singleton pattern to maintain state and objects across callbacks.
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from dash_aiml.core.managers.data_manager import DataManager, data_manager
from dash_aiml.core.managers.project_manager import ProjectManager, project_manager


class Session:
    """
    Represents a user session in the application.

    Attributes
    ----------
    id : str
        Unique session identifier
    user_id : str
        User identifier (can be anonymous)
    created : str
        Session creation timestamp
    last_active : str
        Last activity timestamp
    data : dict
        Session-specific data storage
    settings : dict
        Session-specific settings
    """

    def __init__(self, session_id: Optional[str] = None, user_id: str = "anonymous"):
        """Initialize a new session."""
        self.id = session_id or f"session-{uuid4().hex[:12]}"
        self.user_id = user_id
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_active = self.created
        self.data: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_active = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_to_history(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Add an action to session history.

        Parameters
        ----------
        action : str
            Action name/type
        details : dict, optional
            Action details
        """
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details or {},
        })
        self.update_activity()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get session data by key."""
        return self.data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set session data."""
        self.data[key] = value
        self.update_activity()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get session setting by key."""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set session setting."""
        self.settings[key] = value
        self.update_activity()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created": self.created,
            "last_active": self.last_active,
            "data": self.data,
            "settings": self.settings,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        session = cls(session_id=data["id"], user_id=data.get("user_id", "anonymous"))
        session.created = data.get("created", session.created)
        session.last_active = data.get("last_active", session.last_active)
        session.data = data.get("data", {})
        session.settings = data.get("settings", {})
        session.history = data.get("history", [])
        return session


class AppManager:
    """
    Singleton class to manage application state, settings, and sessions.

    Orchestrates DataManager and ProjectManager while providing
    centralized settings, session management, and action tracking.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Managers
        self._data_manager: Optional[DataManager] = None
        self._project_manager: Optional[ProjectManager] = None

        # Sessions
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None

        # Application settings
        self.app_settings: Dict[str, Any] = self._default_settings()

        # Action history (global)
        self.action_history: List[Dict[str, Any]] = []

        # Persistent objects (cache for computed results, etc.)
        self.cache: Dict[str, Any] = {}

        # Storage directory
        self.storage_dir = Path.home() / ".aiml_dash" / "app"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize default session
        self._create_default_session()

        self._initialized = True

    def _default_settings(self) -> Dict[str, Any]:
        """Get default application settings."""
        return {
            # Display settings
            "theme": "light",
            "page_size": 10,
            "max_rows_display": 1000,
            "precision": 2,
            "show_index": True,
            # Data settings
            "auto_save": False,
            "auto_save_interval": 300,  # seconds
            "max_memory_mb": 1024,
            "cache_enabled": True,
            # Analysis settings
            "confidence_level": 0.95,
            "random_seed": 42,
            "n_jobs": -1,
            # Export settings
            "default_export_format": "csv",
            "include_index_export": False,
            # UI settings
            "show_code": True,
            "show_tooltips": True,
            "animation_enabled": True,
            # Advanced
            "debug_mode": False,
            "log_actions": True,
            "session_timeout": 3600,  # seconds
        }

    def _create_default_session(self):
        """Create default session."""
        session = Session(user_id="default")
        self.sessions[session.id] = session
        self.active_session_id = session.id

    @property
    def data_manager(self) -> DataManager:
        """Get DataManager instance (lazy initialization)."""
        if self._data_manager is None:
            self._data_manager = data_manager
        return self._data_manager

    @property
    def project_manager(self) -> ProjectManager:
        """Get ProjectManager instance (lazy initialization)."""
        if self._project_manager is None:
            self._project_manager = ProjectManager()
        return self._project_manager

    # Session Management
    # ==================

    def create_session(self, user_id: str = "anonymous") -> Session:
        """
        Create a new session.

        Parameters
        ----------
        user_id : str, optional
            User identifier

        Returns
        -------
        Session
            The created session
        """
        session = Session(user_id=user_id)
        self.sessions[session.id] = session
        self.log_action("session_created", {"session_id": session.id, "user_id": user_id})
        return session

    def get_session(self, session_id: Optional[str] = None) -> Optional[Session]:
        """
        Get session by ID, or active session if None.

        Parameters
        ----------
        session_id : str, optional
            Session ID

        Returns
        -------
        Session or None
            The requested session
        """
        if session_id is None:
            session_id = self.active_session_id

        return self.sessions.get(session_id)

    def set_active_session(self, session_id: str) -> bool:
        """
        Set active session.

        Parameters
        ----------
        session_id : str
            Session ID to activate

        Returns
        -------
        bool
            True if successful
        """
        if session_id in self.sessions:
            self.active_session_id = session_id
            self.sessions[session_id].update_activity()
            return True
        return False

    def list_sessions(self) -> List[Session]:
        """Get list of all sessions."""
        return list(self.sessions.values())

    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session.

        Parameters
        ----------
        session_id : str
            Session ID to remove

        Returns
        -------
        bool
            True if successful
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

            # If active session was removed, set to first available
            if self.active_session_id == session_id:
                remaining = list(self.sessions.keys())
                self.active_session_id = remaining[0] if remaining else None

            self.log_action("session_removed", {"session_id": session_id})
            return True
        return False

    def cleanup_inactive_sessions(self, timeout_seconds: int = 3600) -> int:
        """
        Remove sessions inactive for longer than timeout.

        Parameters
        ----------
        timeout_seconds : int
            Timeout in seconds

        Returns
        -------
        int
            Number of sessions removed
        """
        now = datetime.now()
        removed = []

        for session_id, session in list(self.sessions.items()):
            last_active = datetime.strptime(session.last_active, "%Y-%m-%d %H:%M:%S")
            delta = (now - last_active).total_seconds()

            if delta > timeout_seconds:
                removed.append(session_id)

        for session_id in removed:
            self.remove_session(session_id)

        return len(removed)

    # Settings Management
    # ===================

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get application setting.

        Parameters
        ----------
        key : str
            Setting key
        default : Any, optional
            Default value if not found

        Returns
        -------
        Any
            Setting value
        """
        return self.app_settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """
        Set application setting.

        Parameters
        ----------
        key : str
            Setting key
        value : Any
            Setting value
        """
        self.app_settings[key] = value
        self.log_action("setting_changed", {"key": key, "value": str(value)})

    def update_settings(self, settings: Dict[str, Any]):
        """
        Update multiple settings at once.

        Parameters
        ----------
        settings : dict
            Dictionary of settings to update
        """
        self.app_settings.update(settings)
        self.log_action("settings_updated", {"count": len(settings)})

    def reset_settings(self):
        """Reset all settings to defaults."""
        self.app_settings = self._default_settings()
        self.log_action("settings_reset", {})

    def export_settings(self, filepath: Union[str, Path]) -> bool:
        """
        Export settings to JSON file.

        Parameters
        ----------
        filepath : str or Path
            Output file path

        Returns
        -------
        bool
            True if successful
        """
        try:
            filepath = Path(filepath)
            with open(filepath, "w") as f:
                json.dump(self.app_settings, f, indent=2)
            self.log_action("settings_exported", {"path": str(filepath)})
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False

    def import_settings(self, filepath: Union[str, Path]) -> bool:
        """
        Import settings from JSON file.

        Parameters
        ----------
        filepath : str or Path
            Input file path

        Returns
        -------
        bool
            True if successful
        """
        try:
            filepath = Path(filepath)
            with open(filepath, "r") as f:
                settings = json.load(f)
            self.app_settings.update(settings)
            self.log_action("settings_imported", {"path": str(filepath)})
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False

    # Action Logging
    # ==============

    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None):
        """
        Log an action.

        Parameters
        ----------
        action : str
            Action name/type
        details : dict, optional
            Action details
        session_id : str, optional
            Session ID (uses active if None)
        """
        if not self.get_setting("log_actions", True):
            return

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details or {},
            "session_id": session_id or self.active_session_id,
        }

        self.action_history.append(log_entry)

        # Also add to session history
        session = self.get_session(session_id)
        if session:
            session.add_to_history(action, details)

    def get_action_history(
        self, limit: Optional[int] = None, action_type: Optional[str] = None, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get action history.

        Parameters
        ----------
        limit : int, optional
            Maximum number of actions to return
        action_type : str, optional
            Filter by action type
        session_id : str, optional
            Filter by session ID

        Returns
        -------
        list
            List of action entries
        """
        history = self.action_history

        # Filter by action type
        if action_type:
            history = [h for h in history if h["action"] == action_type]

        # Filter by session
        if session_id:
            history = [h for h in history if h["session_id"] == session_id]

        # Apply limit
        if limit:
            history = history[-limit:]

        return history

    def clear_action_history(self, session_id: Optional[str] = None):
        """
        Clear action history.

        Parameters
        ----------
        session_id : str, optional
            If provided, clear only for that session
        """
        if session_id:
            self.action_history = [h for h in self.action_history if h["session_id"] != session_id]
            session = self.get_session(session_id)
            if session:
                session.history.clear()
        else:
            self.action_history.clear()
            for session in self.sessions.values():
                session.history.clear()

    # Cache Management
    # ================

    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache.

        Parameters
        ----------
        key : str
            Cache key
        value : Any
            Value to cache
        ttl : int, optional
            Time to live in seconds (not implemented yet)
        """
        if not self.get_setting("cache_enabled", True):
            return

        self.cache[key] = {"value": value, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ttl": ttl}

    def cache_get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Parameters
        ----------
        key : str
            Cache key
        default : Any, optional
            Default value if not found

        Returns
        -------
        Any
            Cached value or default
        """
        if key in self.cache:
            return self.cache[key]["value"]
        return default

    def cache_delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if key was deleted
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def cache_clear(self):
        """Clear entire cache."""
        self.cache.clear()
        self.log_action("cache_cleared", {})

    def cache_keys(self) -> List[str]:
        """Get list of all cache keys."""
        return list(self.cache.keys())

    # State Management
    # ================

    def export_state(
        self,
        filepath: Union[str, Path],
        include_sessions: bool = True,
        include_data: bool = False,
        include_projects: bool = False,
    ) -> tuple[bool, str]:
        """
        Export complete application state.

        Parameters
        ----------
        filepath : str or Path
            Output file path
        include_sessions : bool, optional
            Include session data
        include_data : bool, optional
            Include datasets from DataManager
        include_projects : bool, optional
            Include projects from ProjectManager

        Returns
        -------
        tuple
            (success: bool, message: str)
        """
        try:
            state = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "settings": self.app_settings,
                "action_history": self.action_history,
                "cache": {k: v["value"] for k, v in self.cache.items()},
            }

            if include_sessions:
                state["sessions"] = {sid: session.to_dict() for sid, session in self.sessions.items()}
                state["active_session_id"] = self.active_session_id

            if include_data:
                state["data_state"] = self.data_manager.export_all_state()

            if include_projects:
                # Export project summaries
                state["projects"] = [
                    self.project_manager.get_project_summary(p.id) for p in self.project_manager.list_projects()
                ]

            filepath = Path(filepath)
            with open(filepath, "wb") as f:
                pickle.dump(state, f)

            self.log_action("state_exported", {"path": str(filepath)})
            return True, f"State exported to {filepath}"

        except Exception as e:
            return False, f"Error exporting state: {str(e)}"

    def import_state(
        self, filepath: Union[str, Path], restore_sessions: bool = True, restore_data: bool = False, merge: bool = False
    ) -> tuple[bool, str]:
        """
        Import application state.

        Parameters
        ----------
        filepath : str or Path
            Input file path
        restore_sessions : bool, optional
            Restore session data
        restore_data : bool, optional
            Restore datasets
        merge : bool, optional
            Merge with current state (vs replace)

        Returns
        -------
        tuple
            (success: bool, message: str)
        """
        try:
            filepath = Path(filepath)
            with open(filepath, "rb") as f:
                state = pickle.load(f)

            if not merge:
                self.app_settings = state.get("settings", self._default_settings())
                self.action_history = state.get("action_history", [])
                self.cache = {
                    k: {"value": v, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    for k, v in state.get("cache", {}).items()
                }
            else:
                self.app_settings.update(state.get("settings", {}))
                self.action_history.extend(state.get("action_history", []))

            if restore_sessions and "sessions" in state:
                if not merge:
                    self.sessions.clear()

                for sid, session_data in state["sessions"].items():
                    self.sessions[sid] = Session.from_dict(session_data)

                active_sid = state.get("active_session_id")
                if active_sid and active_sid in self.sessions:
                    self.active_session_id = active_sid

            if restore_data and "data_state" in state:
                success, msg = self.data_manager.import_all_state(state["data_state"])
                if not success:
                    return False, f"Error restoring data: {msg}"

            self.log_action("state_imported", {"path": str(filepath)})
            return True, f"State imported from {filepath}"

        except Exception as e:
            return False, f"Error importing state: {str(e)}"

    # Quick Access Methods
    # ====================

    def get_current_dataset(self):
        """Get current active dataset from DataManager."""
        return self.data_manager.get_dataset()

    def get_current_project(self):
        """Get current active project from ProjectManager."""
        return self.project_manager.get_active_project()

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of application status.

        Returns
        -------
        dict
            Status summary
        """
        return {
            "sessions": {
                "total": len(self.sessions),
                "active_id": self.active_session_id,
            },
            "data": {
                "datasets": len(self.data_manager.get_dataset_names()),
                "active_dataset": self.data_manager.get_active_dataset_name(),
            },
            "projects": {
                "total": len(self.project_manager.list_projects()),
                "active": self.project_manager.active_project_id,
            },
            "cache": {
                "size": len(self.cache),
                "enabled": self.get_setting("cache_enabled", True),
            },
            "actions": {
                "total": len(self.action_history),
                "logging": self.get_setting("log_actions", True),
            },
        }


# Global instance
app_manager = AppManager()
