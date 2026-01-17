# Settings Consolidation & Refactoring

## Summary

Successfully consolidated `settings.py` and `config.py` into a single unified settings module with import/export functionality implemented as class methods.

## Key Changes

### 1. Consolidated Settings (settings.py)

**Modified: [aiml_dash/utils/settings.py](aiml_dash/utils/settings.py)**

- Merged `Settings` and `AppSettings` into a single `Settings` class
- Combined all configuration from both modules:
  - Application metadata (name, version, title, description, github_url)
  - Server configuration (debug, host, port)
  - Database settings (database_url, database_echo)
  - Security (secret_key, allowed_hosts, enable_talisman)
  - Logging (log_level, log_format)
  - UI settings (theme, page_size, max_upload_size_mb)
  - Data management (max_datasets, data_cache_size, auto_save)
  - Cache configuration (cache_enabled, cache_type, cache_timeout)
  - Analysis settings (default_confidence_level, default_random_seed, max_iterations)
  - Plot settings (default_plot_height, default_plot_width, plot_template)
  - Performance (enable_compression, enable_caching, callback_timeout)
  - Session configuration (session_lifetime_hours)

- Added properties:
  - `base_dir`: Base directory of the application
  - `assets_dir`: Assets directory path
  - `data_dir`: Data directory path (auto-creates if missing)

### 2. Import/Export as Class Methods

Transformed module-level functions into class methods:

#### Export Methods
- `export_to_json(filepath, indent=2)` - Export to JSON
- `export_to_yaml(filepath)` - Export to YAML
- `export_to(filepath)` - Auto-detect format from extension

#### Import Methods (Class Methods)
- `Settings.from_json(filepath)` - Import from JSON
- `Settings.from_yaml(filepath)` - Import from YAML
- `Settings.from_file(filepath)` - Auto-detect format from extension

#### Benefits of Class Methods
- ✅ More object-oriented design
- ✅ No need for separate settings objects as parameters
- ✅ Cleaner API: `settings.export_to('config.json')`
- ✅ Factory pattern for imports: `Settings.from_json('config.json')`
- ✅ Better encapsulation

### 3. Backward Compatibility (config.py)

**Modified: [aiml_dash/utils/config.py](aiml_dash/utils/config.py)**

- Deprecated but maintained for backward compatibility
- Re-exports from `settings.py`:
  - `Settings`
  - `AppSettings` (alias to Settings)
  - `get_settings()`
  - `settings`

### 4. Updated Tests

**Recreated: [tests/utils/test_settings_import_export.py](tests/utils/test_settings_import_export.py)**

- 27 comprehensive tests
- All tests updated to use new class methods
- Added property tests for `base_dir`, `assets_dir`, `data_dir`
- ✅ All tests passing

### 5. Updated Examples

**Modified: [examples/settings_import_export_example.py](examples/settings_import_export_example.py)**

- Updated all examples to use new class method API
- Simplified code by removing separate Settings/AppSettings
- ✅ Example runs successfully

## New API Usage

### Export Settings

```python
from aiml_dash.utils.settings import Settings, get_settings

# Get settings instance
settings = get_settings()

# Export to JSON
settings.export_to_json("config.json")

# Export to YAML
settings.export_to_yaml("config.yaml")

# Auto-detect format
settings.export_to("config.yml")
```

### Import Settings

```python
from aiml_dash.utils.settings import Settings

# Import from JSON
settings = Settings.from_json("config.json")

# Import from YAML
settings = Settings.from_yaml("config.yaml")

# Auto-detect format
settings = Settings.from_file("config.yml")
```

### Create Custom Settings

```python
from aiml_dash.utils.settings import Settings

# Create settings with custom values
settings = Settings(
    app_name="My App",
    debug=True,
    port=9000,
    theme="dark",
    page_size=100,
)

# Export
settings.export_to("custom_config.json")
```

## Improvements

1. **Unified Configuration**: Single source of truth for all settings
2. **Cleaner API**: Methods on the class instead of module-level functions
3. **Better OOP**: Factory methods for imports, instance methods for exports
4. **Type Safety**: Full Pydantic validation throughout
5. **Cached Settings**: `get_settings()` uses `@lru_cache` for efficiency
6. **Properties**: Direct access to computed paths
7. **Backward Compatibility**: Old imports still work via config.py

## Migration Guide

### Old API → New API

```python
# OLD: Module-level functions
from aiml_dash.utils.settings import (
    Settings,
    AppSettings,
    export_settings_to_json,
    import_settings_from_json,
)

# Create instances
settings = Settings(...)
app_settings = AppSettings(...)

# Export
export_settings_to_json("config.json", settings, app_settings)

# Import
loaded_settings, loaded_app_settings = import_settings_from_json("config.json")
```

```python
# NEW: Class methods
from aiml_dash.utils.settings import Settings, get_settings

# Create instance (all settings in one class)
settings = Settings(
    app_name="My App",
    theme="dark",  # Previously in AppSettings
    port=9000,     # Previously in Settings
)

# Export (instance method)
settings.export_to_json("config.json")

# Import (class method)
loaded_settings = Settings.from_json("config.json")
```

## Testing Results

```bash
pytest tests/utils/test_settings_import_export.py -v
```

**Result**: ✅ 27 passed in 0.35s

## Files Modified

- ✏️ Modified: `aiml_dash/utils/settings.py` (consolidated & refactored)
- ✏️ Modified: `aiml_dash/utils/config.py` (deprecated, backward compatibility)
- ✏️ Recreated: `tests/utils/test_settings_import_export.py` (updated tests)
- ✏️ Modified: `examples/settings_import_export_example.py` (updated examples)
- ✨ Created: `SETTINGS_CONSOLIDATION.md` (this document)

## Status

✅ **Complete** - All functionality working, tests passing, examples running successfully.
