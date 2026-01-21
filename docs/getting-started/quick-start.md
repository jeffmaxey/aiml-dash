# Quick Start

This guide will walk you through your first data analysis session with AIML Dash.

## Starting the Application

After installation, start AIML Dash:

```bash
uv run python aiml_dash/run.py
```

Open your browser and navigate to `http://127.0.0.1:8050`

## Understanding the Interface

### Layout Overview

AIML Dash uses a three-panel layout:

- **Left Sidebar (Navbar)**: Navigation menu organized by categories
- **Main Content Area**: Active page content
- **Right Sidebar (Aside)**: Dataset selector and quick statistics

### Navigation

The navigation menu is organized into sections:

- **Core**: Home, Settings, Help
- **Data**: Data management tools
- **Basics**: Statistical analysis
- **Design**: Experimental design
- **Model**: Machine learning models
- **Multivariate**: Advanced analysis

## Loading Data

### From CSV File

1. Navigate to **Data → Manage**
2. Click **Load Data**
3. Select your CSV file
4. Configure import options (separator, encoding)
5. Click **Import**

### From Built-in Datasets

AIML Dash includes sample datasets for testing:

1. Navigate to **Data → Manage**
2. Click **Load Example Dataset**
3. Select a dataset (e.g., `diamonds`, `iris`)
4. Click **Load**

## Exploring Data

### View Dataset

1. Select a dataset from the dropdown in the right sidebar
2. Navigate to **Data → View**
3. Browse the data in an interactive table
4. Sort and filter columns

### Summary Statistics

The right sidebar shows quick statistics:

- Number of rows
- Number of columns
- Column types
- Missing values

### Detailed Exploration

1. Navigate to **Data → Explore**
2. Select variables to analyze
3. View descriptive statistics
4. Generate frequency tables
5. Visualize distributions

## Creating Visualizations

### Scatter Plot

1. Navigate to **Data → Visualize**
2. Select visualization type: **Scatter Plot**
3. Choose X and Y variables
4. (Optional) Add color grouping
5. Click **Create Plot**

### Bar Chart

1. Navigate to **Data → Visualize**
2. Select visualization type: **Bar Chart**
3. Choose categorical variable
4. Select aggregation function
5. Click **Create Plot**

## Basic Statistical Analysis

### Compare Means (t-test)

1. Navigate to **Basics → Compare Means**
2. Select numerical variable
3. Select grouping variable
4. Choose test type (independent/paired)
5. Click **Run Analysis**
6. View results and interpretation

### Correlation Analysis

1. Navigate to **Basics → Correlation**
2. Select multiple numerical variables
3. Choose correlation method (Pearson/Spearman)
4. Click **Calculate**
5. View correlation matrix and p-values

## Building a Simple Model

### Linear Regression

1. Navigate to **Model → Linear Regression**
2. Select dependent variable (Y)
3. Select independent variables (X)
4. Click **Run Model**
5. View results:
   - Model summary
   - Coefficients
   - R-squared
   - Residual plots

### Making Predictions

1. After running a model, scroll to **Predictions**
2. Enter values for independent variables
3. Click **Predict**
4. View predicted value and confidence interval

## Transforming Data

### Creating New Variables

1. Navigate to **Data → Transform**
2. Click **Create Variable**
3. Enter variable name
4. Define calculation (e.g., `price / carat`)
5. Click **Create**

### Filtering Data

1. Navigate to **Data → Transform**
2. Click **Filter Rows**
3. Enter filter expression (e.g., `carat > 1.0`)
4. Click **Apply Filter**
5. Preview filtered data

## Saving Your Work

### Export Data

1. Navigate to **Data → Manage**
2. Select dataset to export
3. Click **Export Data**
4. Choose format (CSV, Excel, JSON)
5. Click **Download**

### Export State

Save your entire session including data and settings:

1. Click the menu icon in the header
2. Select **Export State**
3. Choose what to include:
   - Datasets
   - Settings
   - Plugin configuration
4. Click **Download State**

### Import State

Restore a previous session:

1. Click the menu icon in the header
2. Select **Import State**
3. Upload your state file
4. Click **Import**

## Customizing the Interface

### Theme Toggle

Switch between light and dark modes:

1. Click the theme icon in the header
2. Theme preference is automatically saved

### Enable/Disable Plugins

Customize which pages are available:

1. Navigate to **Settings**
2. Scroll to **Plugin Management**
3. Toggle plugins on/off
4. Click **Save Settings**

## Next Steps

- Explore more [Analysis Tools](../user-guide/analysis-tools.md)
- Learn about [Data Management](../user-guide/data-management.md)
- Try [Advanced Visualizations](../user-guide/visualization.md)
- Create your own [Plugins](../plugin-development/overview.md)

## Tips and Tricks

!!! tip "Keyboard Shortcuts"
    - Press `/` to focus the search bar
    - Use arrow keys to navigate the sidebar
    - Press `Esc` to close modals

!!! tip "Data Persistence"
    Datasets are stored in browser memory. Use Export/Import State to save your work between sessions.

!!! warning "Large Datasets"
    For datasets with more than 100,000 rows, some visualizations may be slow. Consider filtering or sampling your data.

!!! info "Documentation"
    Hover over the info icons (ℹ️) throughout the interface for contextual help.
