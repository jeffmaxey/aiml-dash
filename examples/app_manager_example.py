"""
Example demonstrating AppManager usage.

Shows how to use the AppManager for centralized application management,
including settings, sessions, actions, and integration with DataManager
and ProjectManager.
"""

import pandas as pd
from aiml_dash.managers.app_manager import app_manager


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print('=' * 80)


def example_1_settings_management():
    """Example 1: Managing application settings."""
    print_section("EXAMPLE 1: Settings Management")
    
    # Get current settings
    print("\nCurrent theme:", app_manager.get_setting("theme"))
    print("Page size:", app_manager.get_setting("page_size"))
    print("Debug mode:", app_manager.get_setting("debug_mode"))
    
    # Update settings
    app_manager.set_setting("theme", "dark")
    app_manager.set_setting("page_size", 25)
    print("\n✓ Settings updated")
    print("New theme:", app_manager.get_setting("theme"))
    print("New page size:", app_manager.get_setting("page_size"))
    
    # Update multiple settings
    app_manager.update_settings({
        "show_code": False,
        "animation_enabled": False,
        "confidence_level": 0.99
    })
    print("\n✓ Multiple settings updated")
    print("Show code:", app_manager.get_setting("show_code"))
    print("Confidence level:", app_manager.get_setting("confidence_level"))


def example_2_session_management():
    """Example 2: Managing user sessions."""
    print_section("EXAMPLE 2: Session Management")
    
    # Create sessions
    session1 = app_manager.create_session("alice@example.com")
    session2 = app_manager.create_session("bob@example.com")
    
    print(f"\n✓ Created sessions:")
    print(f"  - {session1.user_id}: {session1.id}")
    print(f"  - {session2.user_id}: {session2.id}")
    
    # Set active session
    app_manager.set_active_session(session1.id)
    print(f"\n✓ Active session: {session1.user_id}")
    
    # Store session-specific data
    active_session = app_manager.get_session()
    active_session.set_data("selected_dataset", "diamonds")
    active_session.set_data("analysis_type", "regression")
    active_session.set_setting("preferred_theme", "dark")
    
    print(f"\nSession data for {active_session.user_id}:")
    print(f"  - Dataset: {active_session.get_data('selected_dataset')}")
    print(f"  - Analysis: {active_session.get_data('analysis_type')}")
    print(f"  - Theme: {active_session.get_setting('preferred_theme')}")
    
    # List all sessions
    print(f"\n✓ Total sessions: {len(app_manager.list_sessions())}")


def example_3_action_logging():
    """Example 3: Logging and tracking actions."""
    print_section("EXAMPLE 3: Action Logging")
    
    # Log various actions
    app_manager.log_action("dataset_loaded", {
        "dataset": "diamonds",
        "rows": 200,
        "columns": 10
    })
    
    app_manager.log_action("analysis_started", {
        "type": "linear_regression",
        "features": ["carat", "cut"]
    })
    
    app_manager.log_action("analysis_completed", {
        "r2_score": 0.85,
        "duration_ms": 125
    })
    
    print("\n✓ Actions logged")
    
    # Get recent actions
    recent_actions = app_manager.get_action_history(limit=5)
    print(f"\nRecent actions ({len(recent_actions)}):")
    for action in recent_actions[-3:]:
        print(f"  - {action['timestamp']}: {action['action']}")
        if action['details']:
            for key, value in list(action['details'].items())[:2]:
                print(f"    • {key}: {value}")
    
    # Get actions by type
    analysis_actions = app_manager.get_action_history(
        action_type="analysis_completed"
    )
    print(f"\n✓ Analysis actions found: {len(analysis_actions)}")


def example_4_cache_usage():
    """Example 4: Using the application cache."""
    print_section("EXAMPLE 4: Cache Management")
    
    # Store computed results in cache
    app_manager.cache_set("correlation_matrix", [
        [1.0, 0.85, 0.72],
        [0.85, 1.0, 0.63],
        [0.72, 0.63, 1.0]
    ])
    
    app_manager.cache_set("model_results", {
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.87
    })
    
    app_manager.cache_set("chart_data", {
        "x": [1, 2, 3, 4, 5],
        "y": [10, 20, 15, 25, 30]
    })
    
    print("\n✓ Data cached")
    print(f"Cache keys: {app_manager.cache_keys()}")
    
    # Retrieve from cache
    model_results = app_manager.cache_get("model_results")
    print(f"\nModel results from cache:")
    print(f"  - Accuracy: {model_results['accuracy']}")
    print(f"  - Precision: {model_results['precision']}")
    
    # Cache statistics
    print(f"\n✓ Total cached items: {len(app_manager.cache_keys())}")


def example_5_data_integration():
    """Example 5: Integration with DataManager."""
    print_section("EXAMPLE 5: DataManager Integration")
    
    # Access DataManager through AppManager
    dm = app_manager.data_manager
    
    print(f"\n✓ Available datasets: {dm.get_dataset_names()}")
    
    # Get current dataset
    df = app_manager.get_current_dataset()
    print(f"\nCurrent dataset: {dm.get_active_dataset_name()}")
    print(f"  - Shape: {df.shape}")
    print(f"  - Columns: {list(df.columns)[:5]}...")
    
    # Log dataset action
    app_manager.log_action("dataset_viewed", {
        "name": dm.get_active_dataset_name(),
        "shape": str(df.shape)
    })
    
    # Create a new dataset and add to DataManager
    custom_data = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['x', 'y', 'x', 'y', 'x']
    })
    
    dm.add_dataset("custom_analysis", custom_data, description="Custom data for analysis")
    app_manager.log_action("dataset_created", {
        "name": "custom_analysis",
        "rows": len(custom_data)
    })
    
    print(f"\n✓ Dataset created: custom_analysis ({custom_data.shape})")


def example_6_project_integration():
    """Example 6: Integration with ProjectManager."""
    print_section("EXAMPLE 6: ProjectManager Integration")
    
    # Access ProjectManager through AppManager
    pm = app_manager.project_manager
    
    # Create a project
    project = pm.create_project(
        name="Sales Analysis 2026",
        description="Q1 Sales data analysis",
        project_type="Business Analytics"
    )
    
    app_manager.log_action("project_created", {
        "project_id": project.id,
        "name": project.name
    })
    
    print(f"\n✓ Project created: {project.name}")
    print(f"  - ID: {project.id}")
    print(f"  - Type: {project.project_type}")
    
    # Set as active and get info
    pm.set_active_project(project.id)
    current_project = app_manager.get_current_project()
    
    print(f"\n✓ Active project: {current_project.name}")
    
    # Add datasets to project from DataManager
    dm = app_manager.data_manager
    success, msg = dm.add_dataset_to_project("diamonds")
    
    if success:
        print(f"\n✓ {msg}")
        app_manager.log_action("dataset_added_to_project", {
            "project": project.name,
            "dataset": "diamonds"
        })


def example_7_status_summary():
    """Example 7: Getting application status."""
    print_section("EXAMPLE 7: Application Status Summary")
    
    summary = app_manager.get_status_summary()
    
    print("\nApplication Status:")
    print(f"\nSessions:")
    print(f"  - Total: {summary['sessions']['total']}")
    print(f"  - Active ID: {summary['sessions']['active_id']}")
    
    print(f"\nData:")
    print(f"  - Datasets: {summary['data']['datasets']}")
    print(f"  - Active: {summary['data']['active_dataset']}")
    
    print(f"\nProjects:")
    print(f"  - Total: {summary['projects']['total']}")
    print(f"  - Active: {summary['projects']['active']}")
    
    print(f"\nCache:")
    print(f"  - Items: {summary['cache']['size']}")
    print(f"  - Enabled: {summary['cache']['enabled']}")
    
    print(f"\nActions:")
    print(f"  - Total logged: {summary['actions']['total']}")
    print(f"  - Logging enabled: {summary['actions']['logging']}")


def example_8_state_persistence():
    """Example 8: Saving and loading application state."""
    print_section("EXAMPLE 8: State Persistence")
    
    import tempfile
    from pathlib import Path
    
    # Create some state
    app_manager.set_setting("custom_setting", "important_value")
    session = app_manager.create_session("persistent_user")
    session.set_data("important_data", [1, 2, 3, 4, 5])
    
    print("\n✓ Application state created")
    print(f"  - Custom setting: {app_manager.get_setting('custom_setting')}")
    print(f"  - Session data: {session.get_data('important_data')}")
    
    # Export state
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "app_state.pkl"
        
        success, msg = app_manager.export_state(
            filepath,
            include_sessions=True,
            include_data=False
        )
        
        if success:
            print(f"\n✓ State exported: {filepath.name}")
            print(f"  Size: {filepath.stat().st_size} bytes")
            
            # Modify state
            app_manager.set_setting("custom_setting", "changed")
            
            # Reload
            success, msg = app_manager.import_state(filepath, restore_sessions=True)
            
            if success:
                print(f"\n✓ State imported successfully")
                print(f"  - Restored setting: {app_manager.get_setting('custom_setting')}")
                restored_session = app_manager.get_session(session.id)
                if restored_session:
                    print(f"  - Restored data: {restored_session.get_data('important_data')}")


def example_9_workflow():
    """Example 9: Complete workflow example."""
    print_section("EXAMPLE 9: Complete Workflow")
    
    # 1. Start a new session
    session = app_manager.create_session("analyst@company.com")
    app_manager.set_active_session(session.id)
    print(f"\n1. ✓ Session started for {session.user_id}")
    
    # 2. Configure preferences
    session.set_setting("preferred_viz", "plotly")
    session.set_setting("auto_save", True)
    print(f"2. ✓ User preferences set")
    
    # 3. Load and analyze data
    dm = app_manager.data_manager
    df = dm.get_dataset("diamonds")
    app_manager.log_action("analysis_initiated", {"dataset": "diamonds"})
    print(f"3. ✓ Data loaded: {df.shape}")
    
    # 4. Cache analysis results
    correlation = df[['carat', 'price']].corr().values[0, 1]
    app_manager.cache_set("diamond_correlation", correlation)
    print(f"4. ✓ Results cached (correlation: {correlation:.3f})")
    
    # 5. Create project for this analysis
    pm = app_manager.project_manager
    project = pm.create_project("Diamond Price Analysis")
    dm.add_dataset_to_project("diamonds")
    app_manager.log_action("project_finalized", {"project": project.name})
    print(f"5. ✓ Project created: {project.name}")
    
    # 6. Review history
    recent = app_manager.get_action_history(limit=3)
    print(f"\n6. ✓ Recent actions:")
    for action in recent:
        print(f"   - {action['action']}")
    
    print(f"\n✓ Workflow completed successfully!")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" AppManager Examples - AIML Dash")
    print("=" * 80)
    
    try:
        example_1_settings_management()
        example_2_session_management()
        example_3_action_logging()
        example_4_cache_usage()
        example_5_data_integration()
        example_6_project_integration()
        example_7_status_summary()
        example_8_state_persistence()
        example_9_workflow()
        
        print("\n" + "=" * 80)
        print(" ✓ All examples completed successfully!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
