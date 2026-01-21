# User Guide Overview

Welcome to the AIML Dash user guide. This comprehensive guide will help you make the most of AIML Dash's features for data analysis and machine learning.

## What is AIML Dash?

AIML Dash is a web-based application for predictive analytics and machine learning. It provides:

- **Interactive Data Analysis**: Explore and visualize datasets through an intuitive interface
- **Statistical Tools**: Perform hypothesis tests, correlation analysis, and more
- **Machine Learning**: Build and evaluate predictive models
- **Reproducible Workflows**: Save and restore your analysis state

## Who is it For?

AIML Dash is designed for:

- **Data Scientists**: Quick prototyping and exploratory analysis
- **Analysts**: Statistical analysis and reporting
- **Researchers**: Experimental design and hypothesis testing
- **Students**: Learning data analysis and ML concepts
- **Teams**: Collaborative data exploration

## Key Concepts

### Datasets

Datasets are the foundation of your analysis. AIML Dash supports:

- Multiple datasets loaded simultaneously
- Various formats (CSV, Excel, JSON, SQL)
- Dataset transformations and filtering
- Active dataset selection

### Pages

The application is organized into pages, grouped by functionality:

- **Data**: Import, explore, transform, visualize
- **Basics**: Statistical tests and analysis
- **Design**: Experimental design tools
- **Model**: Machine learning models
- **Multivariate**: Advanced analysis

### State Management

Your work is preserved through:

- **Browser Storage**: Settings and preferences
- **Export/Import**: Save and restore complete sessions
- **Downloads**: Export data and results

## Getting Started

### 1. Loading Data

Start by loading a dataset:

- Navigate to **Data → Manage**
- Import from file or database
- Or load a sample dataset

See: [Data Management](data-management.md)

### 2. Exploring Data

Understand your data:

- View data table
- Generate summary statistics
- Create visualizations
- Check for missing values

See: [Data Management](data-management.md)

### 3. Analyzing Data

Perform analysis:

- Statistical tests
- Correlation analysis
- Regression models
- Machine learning

See: [Analysis Tools](analysis-tools.md)

### 4. Visualizing Results

Create visualizations:

- Scatter plots
- Bar charts
- Histograms
- Box plots
- Custom plots

See: [Visualization](visualization.md)

### 5. Exporting Results

Save your work:

- Export transformed data
- Download plots
- Save analysis state
- Generate reports

See: [Export & Import](export-import.md)

## Interface Overview

### Header

The top bar contains:

- **Logo**: Return to home page
- **Navigation Toggle**: Show/hide sidebar
- **Theme Switch**: Toggle light/dark mode
- **State Menu**: Export/import application state

### Left Sidebar (Navbar)

Navigation organized by category:

- **Core**: Home, Settings, Help
- **Data**: Data management pages
- **Basics**: Statistical analysis pages
- **Design**: Experimental design pages
- **Model**: Machine learning pages
- **Multivariate**: Advanced analysis pages

Collapse/expand sections by clicking on them.

### Main Content Area

The active page content:

- Page-specific controls and options
- Results and visualizations
- Interactive elements

### Right Sidebar (Aside)

Quick access to:

- **Dataset Selector**: Choose active dataset
- **Quick Statistics**: 
  - Number of rows
  - Number of columns
  - Column types
  - Missing values

### Footer

Links to:

- Documentation
- GitHub repository
- Contact information

## Common Workflows

### Exploratory Data Analysis

1. Load dataset
2. View data structure
3. Generate summary statistics
4. Create visualizations
5. Check correlations
6. Identify patterns

### Hypothesis Testing

1. Load dataset
2. Define hypothesis
3. Select appropriate test
4. Run analysis
5. Interpret results
6. Export findings

### Predictive Modeling

1. Load and prepare data
2. Select features and target
3. Choose model type
4. Train model
5. Evaluate performance
6. Make predictions
7. Export model

### Data Transformation

1. Load raw data
2. Handle missing values
3. Create new variables
4. Filter rows
5. Aggregate data
6. Export cleaned data

## Tips and Best Practices

### Data Preparation

- Check for missing values before analysis
- Understand your variable types (numeric, categorical)
- Look for outliers that might affect results
- Consider data transformations when needed

### Analysis

- Start with descriptive statistics
- Visualize before formal testing
- Choose appropriate statistical tests
- Check assumptions before applying tests
- Interpret results in context

### Visualization

- Choose appropriate chart types
- Use clear labels and titles
- Consider color-blind friendly palettes
- Test in both light and dark themes
- Keep visualizations simple and focused

### Performance

- Filter large datasets before visualization
- Use pagination for large tables
- Sample data for initial exploration
- Export and reload for session persistence

## Keyboard Shortcuts

While not extensively implemented, some useful shortcuts:

- **/** - Focus search (if available)
- **Esc** - Close modals and dialogs
- **Arrow Keys** - Navigate dropdowns

## Getting Help

### In-App Help

- Look for info icons (ℹ️) throughout the interface
- Navigate to **Help** page for documentation
- Check the Settings page for configuration options

### Documentation

- Read this user guide
- Explore the [API Reference](../api-reference/core.md)
- Check [Plugin Development](../plugin-development/overview.md) to extend

### Support

- Report issues on [GitHub](https://github.com/jeffmaxey/aiml-dash/issues)
- Email: aiml-dash@proton.me

## What's Next?

Explore specific topics:

- [Data Management](data-management.md) - Importing, exploring, transforming data
- [Analysis Tools](analysis-tools.md) - Statistical tests and models
- [Visualization](visualization.md) - Creating charts and plots
- [Export & Import](export-import.md) - Saving and sharing work

Or jump right in with the [Quick Start Guide](../getting-started/quick-start.md)!
