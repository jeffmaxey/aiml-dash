# Architecture

This document describes the architecture of AIML Dash, including its key components, design patterns, and how they work together.

## Overview

AIML Dash is built on a modular, plugin-based architecture that promotes extensibility, maintainability, and separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Dash Frontend (React)                   │  │
│  │  - DMC Components                                 │  │
│  │  - Plotly Graphs                                  │  │
│  │  - Client-side Callbacks                         │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/WebSocket
                   │
┌──────────────────▼──────────────────────────────────────┐
│                 Flask/Dash Server                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Application Core                     │  │
│  │  - App Initialization (app.py)                   │  │
│  │  - Routing                                       │  │
│  │  - State Management                              │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │            Plugin Framework                       │  │
│  │  - Plugin Registry                               │  │
│  │  - Plugin Loader                                 │  │
│  │  - Hot Reload                                    │  │
│  │  - Dependency Manager                            │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │               Plugins                             │  │
│  │  - Core Plugin                                   │  │
│  │  - Data Plugin                                   │  │
│  │  - Basics Plugin                                 │  │
│  │  - Model Plugin                                  │  │
│  │  - ... (extensible)                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │            Component Library                      │  │
│  │  - Shell Components (Header, Navbar, Footer)    │  │
│  │  - Common Components                             │  │
│  │  - Reusable Layouts                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │               Utilities                           │  │
│  │  - Data Manager                                  │  │
│  │  - Statistics                                    │  │
│  │  - Database                                      │  │
│  │  - Configuration                                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                   │
                   │ File I/O, Database
                   │
┌──────────────────▼──────────────────────────────────────┐
│              Data Storage Layer                         │
│  - File System (CSV, Excel, JSON)                      │
│  - Database (SQLite, PostgreSQL, MySQL)                │
│  - Browser Storage (LocalStorage, SessionStorage)      │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### Application Core (app.py)

The main application file that:

- Initializes the Dash app
- Configures the MantineProvider theme
- Sets up the AppShell layout
- Registers plugins and callbacks
- Manages routing

**Key responsibilities:**
- App initialization and configuration
- Layout structure (header, navbar, aside, footer)
- Page routing
- State management
- Plugin integration

### Plugin Framework

The plugin system enables modular extension of the application.

#### Plugin Registry

- Discovers plugins from `plugins/` directory
- Maintains plugin metadata
- Tracks enabled/disabled plugins
- Manages plugin dependencies
- Provides plugin querying API

**Location:** `aiml_dash/plugins/registry.py`

#### Plugin Loader

- Dynamically imports plugin modules
- Validates plugin structure
- Registers plugin pages
- Loads plugin callbacks
- Handles plugin errors

**Location:** `aiml_dash/plugins/loader.py`

#### Plugin Models

- Defines plugin data structures
- Page metadata
- Plugin configuration
- Type definitions

**Location:** `aiml_dash/plugins/models.py`

#### Hot Reload

- Watches plugin files for changes
- Automatically reloads modified plugins
- Updates app without full restart (in debug mode)

**Location:** `aiml_dash/plugins/hot_reload.py`

### Data Manager

Centralized data storage and management.

**Features:**
- Store multiple datasets
- Track active dataset
- Dataset metadata
- Query and filter operations
- Export/import functionality

**Location:** `aiml_dash/utils/data_manager.py`

**Pattern:** Singleton

```python
from utils.data_manager import data_manager

# Add dataset
data_manager.add_data("my_data", df, "My Dataset")

# Get dataset
df = data_manager.get_data("my_data")

# List datasets
datasets = data_manager.list_datasets()
```

### Component Library

Reusable UI components built with dash-mantine-components.

#### Shell Components

- **Header**: Branding, navigation toggle, theme switch, state menu
- **Navbar**: Collapsible navigation with accordion sections
- **Aside**: Dataset selector and quick statistics
- **Footer**: Credits and links

**Location:** `aiml_dash/components/shell.py`

#### Common Components

Reusable component builders:

- Page headers with icons
- Variable selectors
- Filter sections
- Download buttons
- Info cards
- Tabs

**Location:** `aiml_dash/components/common.py`

### Utilities

#### Statistics Module

Statistical functions and calculations:

- Descriptive statistics
- Hypothesis tests
- Correlation analysis
- Regression

**Location:** `aiml_dash/utils/statistics.py`

#### Transform Module

Data transformation functions:

- Data cleaning
- Variable creation
- Filtering
- Aggregation

**Location:** `aiml_dash/utils/transforms.py`

#### Database Module

Database connectivity:

- SQL query execution
- Connection management
- Multiple database support

**Location:** `aiml_dash/utils/database.py`

## Design Patterns

### Plugin Pattern

Plugins follow a standardized structure enabling dynamic extension:

```python
# Plugin structure
plugins/
└── my_plugin/
    ├── __init__.py       # Registration
    ├── constants.py      # Metadata
    ├── layout.py         # UI
    ├── components.py     # Reusable UI
    ├── callbacks.py      # Logic
    └── styles.py         # Styling
```

### Singleton Pattern

Used for DataManager to ensure single source of truth:

```python
class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Factory Pattern

Used for creating common UI components:

```python
def create_page_header(title, description, icon):
    """Factory function for page headers."""
    return dmc.Group([...])
```

### Observer Pattern

Dash callbacks implement observer pattern:

```python
@callback(
    Output("output", "children"),
    Input("input", "value"),
)
def update_output(value):
    return process(value)
```

## Data Flow

### User Interaction Flow

```
User Action → Input Component → Callback → 
Business Logic → Data/State Update → 
Output Component → UI Update
```

### Plugin Loading Flow

```
App Start → Discover Plugins → Load Metadata →
Validate Structure → Register Pages →
Register Callbacks → Ready
```

### Data Management Flow

```
Import Data → Store in DataManager →
Select Active Dataset → Transform/Filter →
Analyze/Visualize → Export Results
```

## State Management

### Client-Side State

Stored in browser using `dcc.Store`:

- Color scheme preference
- Active dataset
- Plugin configuration
- UI state (navbar/aside open/closed)
- Page state

### Server-Side State

- DataManager (in-memory datasets)
- Configuration
- Session data

### Persistent State

- User preferences (local storage)
- Datasets (file system or database)
- Application configuration (config files)

## Security Considerations

### Input Validation

- Validate all user inputs
- Sanitize file uploads
- Prevent code injection

### Data Protection

- Secure database connections
- Encrypt sensitive data
- Implement access controls (future)

### HTTPS

- Use HTTPS in production
- Enable Flask-Talisman

## Performance Optimization

### Caching

- Cache expensive computations
- Use Flask-Caching
- Memoize callback results

### Lazy Loading

- Load data on demand
- Paginate large datasets
- Stream large files

### Code Splitting

- Plugins loaded independently
- Callbacks registered per plugin
- Minimize initial bundle size

## Testing Architecture

### Unit Tests

Test individual functions and components:

```python
# tests/utils/test_statistics.py
def test_calculate_mean():
    assert calculate_mean([1, 2, 3]) == 2.0
```

### Integration Tests

Test component interactions:

```python
# tests/plugins/test_loader.py
def test_plugin_loading():
    plugins = load_plugins()
    assert "core" in plugins
```

### End-to-End Tests

Test complete user workflows (future):

```python
# tests/e2e/test_data_workflow.py
def test_import_analyze_export():
    # Import data
    # Run analysis
    # Export results
    pass
```

## Deployment Architecture

### Development

```
Local Machine → UV → Python → Dash Dev Server
```

### Production

```
Server → Nginx → Gunicorn → Multiple Workers → Dash App
```

### Docker

```
Container → UV → Python → Dash App
```

### Cloud Deployment Options

- **AWS**: EC2, ECS, Elastic Beanstalk
- **Azure**: App Service, Container Instances
- **GCP**: App Engine, Cloud Run
- **Heroku**: Web Dyno

## Future Architecture Considerations

### Microservices

Split into services:
- Frontend service
- API service
- Data service
- Model service

### Authentication

- User authentication
- Role-based access control
- OAuth integration

### Real-time Collaboration

- WebSocket for live updates
- Shared sessions
- Concurrent editing

### Scalability

- Horizontal scaling
- Load balancing
- Database clustering
- Caching layer (Redis)

## References

- [Dash Architecture](https://dash.plotly.com/architecture)
- [Flask Patterns](https://flask.palletsprojects.com/en/2.3.x/patterns/)
- [Design Patterns](https://refactoring.guru/design-patterns)
