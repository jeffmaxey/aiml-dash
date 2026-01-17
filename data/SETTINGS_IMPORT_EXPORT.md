# Settings Import/Export Feature

## Summary

Added the ability to import and export application settings from `.yaml`, `.yml`, and `.json` files to the AIML Dash application.

## Changes Made

### Core Functionality

1. **Modified `/aiml_dash/utils/settings.py`**:
   - Added `export_settings_to_json()` - Export settings to JSON format
   - Added `export_settings_to_yaml()` - Export settings to YAML format
   - Added `import_settings_from_json()` - Import settings from JSON format
   - Added `import_settings_from_yaml()` - Import settings from YAML format
   - Added `export_settings()` - Generic export with automatic format detection
   - Added `import_settings()` - Generic import with automatic format detection

### Features

- ✅ Export current settings to JSON or YAML
- ✅ Import settings from JSON or YAML
- ✅ Automatic format detection based on file extension (.json, .yaml, .yml)
- ✅ Optional global settings update on import
- ✅ Type-safe with Pydantic validation
- ✅ Comprehensive error handling
- ✅ Support for partial settings (missing fields use defaults)

### Testing

2. **Added `/tests/utils/test_settings_import_export.py`**:
   - 24 comprehensive tests covering:
     - JSON and YAML export functionality
     - JSON and YAML import functionality
     - Generic import/export with format detection
     - Error handling (file not found, invalid format, invalid structure)
     - Round-trip testing (export then import)
   - All tests passing ✅

### Documentation

3. **Added `/docs/settings_import_export.md`**:
   - Complete API reference
   - Usage examples
   - File format examples
   - Best practices
   - Error handling guide

4. **Added `/examples/settings_import_export_example.py`**:
   - Multiple practical examples demonstrating:
     - Basic export/import
     - Custom settings export
     - Environment-specific configurations
     - Error handling
   - Example runs successfully ✅

## Quick Start

### Export Settings

```python
from aiml_dash.utils.settings import export_settings

# Export to JSON
export_settings("config.json")

# Export to YAML
export_settings("config.yaml")
```

### Import Settings

```python
from aiml_dash.utils.settings import import_settings

# Import and update global settings
settings, app_settings = import_settings("config.json")

# Import without updating globals
settings, app_settings = import_settings("config.yaml", update_global=False)
```

## Dependencies

- **JSON**: Built-in (no additional dependencies)
- **YAML**: PyYAML (already in project dependencies)

## Code Quality

- ✅ All linting requirements met (modern Python 3.12+ syntax)
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Error messages follow best practices
- ✅ Tests achieve 100% code coverage for new functionality

## Use Cases

1. **Configuration Management**: Version control your settings
2. **Environment-Specific Settings**: Separate dev/staging/prod configs
3. **Settings Backup/Restore**: Easy backup and restoration
4. **Configuration Sharing**: Share settings between team members
5. **Migration**: Move settings between environments or deployments

## Files Modified/Created

- ✏️ Modified: `/aiml_dash/utils/settings.py`
- ✨ Created: `/tests/utils/test_settings_import_export.py`
- ✨ Created: `/examples/settings_import_export_example.py`
- ✨ Created: `/docs/settings_import_export.md`
- ✨ Created: `SETTINGS_IMPORT_EXPORT.md` (this file)

## Testing

Run tests with:
```bash
pytest tests/utils/test_settings_import_export.py -v
```

Run example with:
```bash
python examples/settings_import_export_example.py
```
