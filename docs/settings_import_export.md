# Settings Import/Export

The AIML Dash application now supports importing and exporting settings to and from `.yaml`, `.yml`, and `.json` files. This feature makes it easy to:

- Backup your current configuration
- Share settings between environments
- Version control your application settings
- Quickly switch between different configurations

## Features

- **JSON Support**: Export/import settings in JSON format with customizable indentation
- **YAML Support**: Export/import settings in YAML format (requires PyYAML)
- **Automatic Format Detection**: File format is automatically detected from extension
- **Type-Safe**: Uses Pydantic models to ensure settings validity
- **Global Settings Management**: Can update global settings instances or create new ones
- **Error Handling**: Comprehensive error handling for invalid files and formats

## Quick Start

### Basic Export

```python
from aiml_dash.utils.settings import export_settings

# Export current settings (format determined by extension)
export_settings("my_settings.json")
export_settings("my_settings.yaml")
```

### Basic Import

```python
from aiml_dash.utils.settings import import_settings

# Import settings (format determined by extension)
settings, app_settings = import_settings("my_settings.json")
```

## API Reference

### Export Functions

#### `export_settings(filepath, settings_obj=None, app_settings_obj=None)`

Generic export function that determines format from file extension.

**Parameters:**
- `filepath` (str | Path): Output file path (.json, .yaml, or .yml)
- `settings_obj` (Settings, optional): Settings instance to export (defaults to global)
- `app_settings_obj` (AppSettings, optional): AppSettings instance to export (defaults to global)

**Raises:**
- `ValueError`: If file extension is not supported

**Example:**
```python
export_settings("config.json")
export_settings("config.yaml")
```

#### `export_settings_to_json(filepath, settings_obj=None, app_settings_obj=None, indent=2)`

Export settings to JSON format.

**Parameters:**
- `filepath` (str | Path): Output JSON file path
- `settings_obj` (Settings, optional): Settings instance to export
- `app_settings_obj` (AppSettings, optional): AppSettings instance to export
- `indent` (int): JSON indentation level (default: 2)

**Example:**
```python
export_settings_to_json("config.json", indent=4)
```

#### `export_settings_to_yaml(filepath, settings_obj=None, app_settings_obj=None)`

Export settings to YAML format.

**Parameters:**
- `filepath` (str | Path): Output YAML file path
- `settings_obj` (Settings, optional): Settings instance to export
- `app_settings_obj` (AppSettings, optional): AppSettings instance to export

**Raises:**
- `ImportError`: If PyYAML is not installed

**Example:**
```python
export_settings_to_yaml("config.yaml")
```

### Import Functions

#### `import_settings(filepath, update_global=True)`

Generic import function that determines format from file extension.

**Parameters:**
- `filepath` (str | Path): Input file path (.json, .yaml, or .yml)
- `update_global` (bool): Whether to update global settings instances (default: True)

**Returns:**
- Tuple of (Settings, AppSettings) instances

**Raises:**
- `ValueError`: If file extension is not supported
- `FileNotFoundError`: If file does not exist

**Example:**
```python
settings, app_settings = import_settings("config.json")
```

#### `import_settings_from_json(filepath, update_global=True)`

Import settings from JSON format.

**Parameters:**
- `filepath` (str | Path): Input JSON file path
- `update_global` (bool): Whether to update global settings instances

**Returns:**
- Tuple of (Settings, AppSettings) instances

**Raises:**
- `FileNotFoundError`: If file does not exist
- `json.JSONDecodeError`: If file is not valid JSON
- `ValueError`: If file structure is invalid

**Example:**
```python
settings, app_settings = import_settings_from_json("config.json")
```

#### `import_settings_from_yaml(filepath, update_global=True)`

Import settings from YAML format.

**Parameters:**
- `filepath` (str | Path): Input YAML file path
- `update_global` (bool): Whether to update global settings instances

**Returns:**
- Tuple of (Settings, AppSettings) instances

**Raises:**
- `ImportError`: If PyYAML is not installed
- `FileNotFoundError`: If file does not exist
- `yaml.YAMLError`: If file is not valid YAML
- `ValueError`: If file structure is invalid

**Example:**
```python
settings, app_settings = import_settings_from_yaml("config.yaml")
```

## Usage Examples

### Export Custom Settings

```python
from aiml_dash.utils.settings import Settings, AppSettings, export_settings_to_json

# Create custom settings
custom_settings = Settings(
    app_name="My App",
    debug=True,
    port=9000
)

custom_app_settings = AppSettings(
    theme="dark",
    page_size=100
)

# Export to JSON
export_settings_to_json(
    "custom_config.json",
    custom_settings,
    custom_app_settings
)
```

### Import Without Updating Globals

```python
from aiml_dash.utils.settings import import_settings_from_json

# Import settings without modifying global instances
settings, app_settings = import_settings_from_json(
    "config.json",
    update_global=False
)

print(f"Loaded app: {settings.app_name}")
print(f"Theme: {app_settings.theme}")
```

### Environment-Specific Configuration

```python
import os
from pathlib import Path
from aiml_dash.utils.settings import import_settings

# Load configuration based on environment
env = os.getenv("APP_ENV", "development")
config_file = f"config/{env}_settings.yaml"

if Path(config_file).exists():
    settings, app_settings = import_settings(config_file)
    print(f"Loaded {env} configuration")
else:
    print(f"Using default settings for {env}")
```

### Configuration Management

```python
from aiml_dash.utils.settings import (
    export_settings,
    import_settings,
    settings,
    app_settings
)

# Backup current settings
export_settings("backup/settings_backup.json")

# Modify settings
settings.debug = True
app_settings.theme = "dark"

# Export modified settings
export_settings("config/development.json")

# Later, restore from backup
import_settings("backup/settings_backup.json")
```

## File Format Examples

### JSON Format

```json
{
  "settings": {
    "app_name": "AIML Dash",
    "app_version": "1.0.0",
    "debug": false,
    "host": "127.0.0.1",
    "port": 8050,
    "database_url": null,
    "database_echo": false,
    "secret_key": null,
    "allowed_hosts": ["*"],
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "app_settings": {
    "theme": "light",
    "page_size": 50,
    "max_upload_size_mb": 100,
    "max_datasets": 100,
    "auto_save": true,
    "cache_enabled": true,
    "cache_timeout": 3600,
    "default_confidence_level": 0.95,
    "default_random_seed": 1234,
    "max_iterations": 10000,
    "default_plot_height": 600,
    "default_plot_width": null,
    "plot_template": "plotly_white",
    "enable_compression": true,
    "enable_caching": true,
    "callback_timeout": 300
  }
}
```

### YAML Format

```yaml
settings:
  app_name: AIML Dash
  app_version: 1.0.0
  debug: false
  host: 127.0.0.1
  port: 8050
  database_url: null
  database_echo: false
  secret_key: null
  allowed_hosts:
  - '*'
  log_level: INFO
  log_format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

app_settings:
  theme: light
  page_size: 50
  max_upload_size_mb: 100
  max_datasets: 100
  auto_save: true
  cache_enabled: true
  cache_timeout: 3600
  default_confidence_level: 0.95
  default_random_seed: 1234
  max_iterations: 10000
  default_plot_height: 600
  default_plot_width: null
  plot_template: plotly_white
  enable_compression: true
  enable_caching: true
  callback_timeout: 300
```

## Error Handling

```python
from aiml_dash.utils.settings import import_settings, export_settings

# Handle file not found
try:
    import_settings("nonexistent.json")
except FileNotFoundError as e:
    print(f"Config file not found: {e}")

# Handle unsupported format
try:
    export_settings("config.txt")
except ValueError as e:
    print(f"Unsupported format: {e}")

# Handle invalid JSON
try:
    import_settings("invalid.json")
except Exception as e:
    print(f"Failed to import: {e}")
```

## Best Practices

1. **Version Control**: Store environment-specific settings in version control
2. **Sensitive Data**: Don't store secrets in config files - use environment variables
3. **Backup**: Regularly backup your settings before making changes
4. **Validation**: Settings are validated by Pydantic when imported
5. **Partial Updates**: You can provide partial settings - missing fields use defaults

## Testing

Comprehensive tests are available in `tests/utils/test_settings_import_export.py`. Run them with:

```bash
pytest tests/utils/test_settings_import_export.py -v
```

## Dependencies

- **JSON Support**: Built-in (no additional dependencies)
- **YAML Support**: Requires PyYAML (already included in project dependencies)

## See Also

- [Example Script](../examples/settings_import_export_example.py)
- [Settings Module](../aiml_dash/utils/settings.py)
- [Tests](../tests/utils/test_settings_import_export.py)
