# Pages Module

The `aiml_dash.pages` module contains the main application pages organized by functional area.

## Overview

Pages are organized into categories based on their purpose:

- **Basics**: Fundamental statistical analyses
- **Data**: Data management and exploration
- **Design**: Experimental design and sampling
- **Model**: Machine learning models
- **Multivariate**: Multivariate analysis techniques

## Page Categories

### Basics (`pages/basics/`)

Statistical analysis pages for basic inferential statistics:

- **Central Limit Theorem (clt.py)**: Demonstration of CLT
- **Compare Means (compare_means.py)**: Two-sample t-tests and ANOVA
- **Compare Proportions (compare_props.py)**: Proportion comparison tests
- **Correlation (correlation.py)**: Correlation analysis
- **Cross Tabs (cross_tabs.py)**: Contingency table analysis
- **Goodness of Fit (goodness.py)**: Chi-square goodness of fit
- **Probability Calculator (prob_calc.py)**: Probability distributions
- **Single Mean (single_mean.py)**: One-sample t-test
- **Single Proportion (single_prop.py)**: One-sample proportion test

**Example:**
```python
from aiml_dash.pages.basics import single_mean

# Access page components
layout = single_mean.create_layout()
```

### Data (`pages/data/`)

Data manipulation and exploration pages:

- **Combine (combine.py)**: Merge and join datasets
- **Explore (explore.py)**: Exploratory data analysis
- **Manage (manage.py)**: Data management operations
- **Pivot (pivot.py)**: Pivot table creation
- **Report (report.py)**: Generate data reports
- **SQL Query (sql_query.py)**: Execute SQL queries
- **Transform (transform.py)**: Data transformations
- **View (view.py)**: View datasets
- **Visualize (visualize.py)**: Data visualization

### Design (`pages/design/`)

Experimental design and sampling pages:

- **DOE (doe.py)**: Design of Experiments
- **Randomizer (randomizer.py)**: Random assignment
- **Sample Size (sample_size.py)**: Sample size calculation
- **Sample Size Comparison (sample_size_comp.py)**: Compare sample sizes
- **Sampling (sampling.py)**: Sampling techniques

### Model (`pages/model/`)

Machine learning and predictive modeling pages:

- **Collaborative Filtering (collaborative_filtering.py)**: Recommendation systems
- **Decision Analysis (decision_analysis.py)**: Decision trees analysis
- **Decision Tree (decision_tree.py)**: Decision tree classifier
- **Evaluate Classification (evaluate_classification.py)**: Classification metrics
- **Evaluate Regression (evaluate_regression.py)**: Regression metrics
- **Gradient Boosting (gradient_boosting.py)**: Gradient boosting models
- **Linear Regression (linear_regression.py)**: Linear regression
- **Logistic Regression (logistic.py, logistic_regression.py)**: Logistic models
- **Multinomial Logit (multinomial_logit.py)**: Multinomial classification
- **Naive Bayes (naive_bayes.py)**: Naive Bayes classifier
- **Neural Network (neural_network.py)**: Neural networks
- **Random Forest (random_forest.py)**: Random forest models
- **Simulator (simulator.py)**: Model simulation

### Multivariate (`pages/multivariate/`)

Multivariate analysis pages:

- **Conjoint (conjoint.py)**: Conjoint analysis
- **Full Factor (full_factor.py)**: Full factorial analysis
- **Hierarchical Cluster (hierarchical_cluster.py)**: Hierarchical clustering
- **K-Means Cluster (kmeans_cluster.py)**: K-means clustering
- **MDS (mds.py)**: Multidimensional scaling
- **Perceptual Map (perceptual_map.py)**: Perceptual mapping
- **Pre-Factor (pre_factor.py)**: Factor analysis preparation

## Creating a New Page

1. **Choose the appropriate category** based on functionality
2. **Create the page file** in the category directory
3. **Define the page structure:**

```python
from dash import html, dcc, Input, Output, callback
import plotly.express as px

def create_layout():
    """Create the page layout."""
    return html.Div([
        html.H1("My Analysis Page"),
        dcc.Dropdown(
            id="my-dropdown",
            options=[{"label": i, "value": i} for i in range(10)]
        ),
        html.Div(id="my-output")
    ])

@callback(
    Output("my-output", "children"),
    Input("my-dropdown", "value")
)
def update_output(value):
    """Update output based on dropdown selection."""
    return f"Selected: {value}"
```

4. **Register the page** in the plugin system
5. **Add tests** in `tests/pages/`
6. **Update documentation**

## Page Structure Best Practices

### Layout Organization

```python
def create_layout():
    return html.Div([
        create_header(),
        create_controls(),
        create_output_area(),
        create_footer()
    ])

def create_header():
    """Page header with title and description."""
    return html.Div([
        html.H1("Page Title"),
        html.P("Page description")
    ])

def create_controls():
    """Input controls for user interaction."""
    return html.Div([
        # Input components
    ])

def create_output_area():
    """Output display area."""
    return html.Div([
        # Output components
    ])
```

### Callback Organization

```python
# Separate data processing from UI updates
def process_data(input_data):
    """Process input data (controller)."""
    # Business logic
    return processed_data

def create_visualization(data):
    """Create visualization (view)."""
    # Visualization logic
    return figure

@callback(
    Output("output", "figure"),
    Input("input", "value")
)
def update_visualization(input_value):
    """Callback combining controller and view."""
    data = process_data(input_value)
    return create_visualization(data)
```

## Testing

Test pages in `tests/pages/`:

```bash
pytest tests/pages/
```

## Navigation

Pages are automatically added to navigation based on their plugin registration. Configure in the plugin's `get_plugin()` function:

```python
PluginPage(
    id="my_page",
    path="/my-page",
    name="My Page",
    section="Model",  # Navigation section
    group="Supervised",  # Optional group
    order=10  # Display order
)
```

## Best Practices

1. **Keep pages focused**: One analysis per page
2. **Use consistent layouts**: Follow existing page patterns
3. **Validate inputs**: Check user inputs before processing
4. **Handle errors gracefully**: Show user-friendly error messages
5. **Optimize performance**: Use caching for expensive operations
6. **Document parameters**: Include tooltips and help text
7. **Test thoroughly**: Cover all user interactions
8. **Follow accessibility guidelines**: Use semantic HTML and ARIA labels
