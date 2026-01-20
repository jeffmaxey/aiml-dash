# Utils Module

The `aiml_dash.utils` module contains utility functions and classes used throughout the aiml-dash application.

## Overview

This module provides reusable components for data management, transformations, statistics, and configuration management.

## Components

### Constants (`constants.py`)

Contains application-wide constants and configuration values.

**Example:**
```python
from aiml_dash.utils.constants import SOME_CONSTANT

# Use constants in your code
value = SOME_CONSTANT
```

### Transforms (`transforms.py`)

Data transformation utilities for preprocessing and feature engineering.

**Example:**
```python
from aiml_dash.utils.transforms import transform_data

# Transform your data
transformed_data = transform_data(raw_data)
```

### Data Manager (`data_manager.py`)

Handles data loading, caching, and management operations.

**Example:**
```python
from aiml_dash.utils.data_manager import DataManager

# Initialize data manager
dm = DataManager()
data = dm.load_data("dataset_name")
```

### Statistics (`statistics.py`)

Statistical analysis utilities and helper functions.

**Example:**
```python
from aiml_dash.utils.statistics import calculate_statistics

# Calculate statistics for your dataset
stats = calculate_statistics(data)
```

### Pagination (`paginate_df.py`)

Utilities for paginating dataframes in the UI.

**Example:**
```python
from aiml_dash.utils.paginate_df import paginate_dataframe

# Paginate a large dataframe
page = paginate_dataframe(df, page_number=1, page_size=100)
```

### Database (`database.py`)

Database connection and query utilities.

**Example:**
```python
from aiml_dash.utils.database import get_connection

# Get database connection
conn = get_connection()
```

### Logging (`logging.py`)

Logging configuration and utilities.

**Example:**
```python
from aiml_dash.utils.logging import setup_logger

# Setup logger for your module
logger = setup_logger(__name__)
logger.info("Operation completed")
```

### Config (`config.py`)

Application configuration management.

**Example:**
```python
from aiml_dash.utils.config import get_config

# Get configuration
config = get_config()
```

## Contributing

When adding new utilities:

1. Keep functions focused and single-purpose
2. Add comprehensive docstrings
3. Include type hints
4. Write unit tests in `tests/utils/`
5. Update this documentation

## Testing

All utilities have corresponding tests in `tests/utils/`. Run tests with:

```bash
pytest tests/utils/
```
