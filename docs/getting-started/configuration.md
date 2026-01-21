# Configuration

AIML Dash can be configured through environment variables, configuration files, and runtime settings.

## Environment Variables

### Application Settings

```bash
# Server configuration
DASH_HOST="0.0.0.0"
DASH_PORT="8050"
DASH_DEBUG="false"

# Application settings
APP_TITLE="AIML Dash"
APP_ENV="production"  # or "development"

# Data storage
DATA_DIR="./data"
UPLOAD_DIR="./uploads"
```

### Database Configuration

```bash
# Database connection
DATABASE_URL="sqlite:///aiml_dash.db"
# or for PostgreSQL
DATABASE_URL="postgresql://user:pass@localhost/aiml_dash"
# or for MySQL
DATABASE_URL="mysql://user:pass@localhost/aiml_dash"
```

### Security Settings

```bash
# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY="your-secret-key-here"

# Enable/disable features
ENABLE_FILE_UPLOAD="true"
MAX_UPLOAD_SIZE="100MB"
ALLOWED_EXTENSIONS="csv,xlsx,json"
```

### Performance Settings

```bash
# Cache configuration
CACHE_TYPE="filesystem"
CACHE_DIR="./cache"
CACHE_DEFAULT_TIMEOUT="300"

# Worker configuration (for production)
WORKERS="4"
THREADS="2"
TIMEOUT="120"
```

## Configuration File

Create a `config.yaml` file in the project root:

```yaml
# config.yaml
app:
  title: "AIML Dash"
  debug: false
  host: "0.0.0.0"
  port: 8050

data:
  storage_dir: "./data"
  upload_dir: "./uploads"
  max_upload_size: 104857600  # 100MB in bytes

database:
  url: "sqlite:///aiml_dash.db"
  echo: false
  pool_size: 5

cache:
  type: "filesystem"
  directory: "./cache"
  default_timeout: 300

plugins:
  enabled:
    - core
    - data_plugin
    - basics_plugin
    - model_plugin
  disabled:
    - example_plugin

security:
  secret_key: "${SECRET_KEY}"
  enable_uploads: true
  allowed_extensions:
    - csv
    - xlsx
    - json

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/aiml_dash.log"
```

Load the configuration in your application:

```python
from utils.config import load_config

config = load_config("config.yaml")
```

## Runtime Settings

### In-App Configuration

Access settings through the web interface:

1. Navigate to **Settings** page
2. Configure options:
   - Theme preferences
   - Plugin management
   - Display settings
   - Data preferences
3. Click **Save Settings**

Settings are stored in browser local storage.

## Plugin Configuration

Configure individual plugins:

```yaml
# config/plugins/data_plugin.yaml
data_plugin:
  default_page_size: 25
  max_rows_display: 10000
  enable_export: true
  export_formats:
    - csv
    - excel
    - json
```

## Production Configuration

### Using Gunicorn

Create a `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8050"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = "./logs/access.log"
errorlog = "./logs/error.log"
loglevel = "info"

# Process naming
proc_name = "aiml-dash"

# Server mechanics
daemon = False
pidfile = "./aiml_dash.pid"
```

Run with:

```bash
gunicorn aiml_dash.app:server -c gunicorn.conf.py
```

### Docker Configuration

Override settings in `docker-compose.yml`:

```yaml
version: '3.8'

services:
  aiml-dash:
    build: .
    ports:
      - "8050:8050"
    environment:
      - DASH_DEBUG=false
      - DATABASE_URL=postgresql://user:pass@db:5432/aiml_dash
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=aiml_dash
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Advanced Configuration

### Custom Themes

Create a custom theme configuration:

```python
# config/theme.py
CUSTOM_THEME = {
    "fontFamily": "'Inter', sans-serif",
    "primaryColor": "blue",
    "colors": {
        "blue": [
            "#e7f5ff",
            "#d0ebff",
            "#a5d8ff",
            "#74c0fc",
            "#4dabf7",
            "#339af0",
            "#228be6",
            "#1c7ed6",
            "#1971c2",
            "#1864ab",
        ],
    },
    "components": {
        "Button": {"defaultProps": {"fw": 400}},
        "Card": {"defaultProps": {"p": "md", "withBorder": True}},
    },
}
```

### Logging Configuration

Configure detailed logging:

```python
# config/logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/aiml_dash.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  aiml_dash:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

## Configuration Validation

AIML Dash validates configuration on startup:

```python
from utils.config import validate_config

# Validate configuration
errors = validate_config(config)
if errors:
    for error in errors:
        print(f"Configuration error: {error}")
    sys.exit(1)
```

## Environment-Specific Configuration

Use different configurations for different environments:

```bash
# Load development config
AIML_DASH_ENV=development python aiml_dash/run.py

# Load production config
AIML_DASH_ENV=production python aiml_dash/run.py
```

```python
# config/__init__.py
import os
from pathlib import Path

env = os.getenv("AIML_DASH_ENV", "development")
config_file = Path(__file__).parent / f"{env}.yaml"

config = load_config(config_file)
```

## Next Steps

- [Quick Start Guide](quick-start.md)
- [User Guide](../user-guide/overview.md)
- [Development Guide](../development/contributing.md)
