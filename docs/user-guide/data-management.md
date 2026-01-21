# Data Management

This guide covers all aspects of working with data in AIML Dash, from importing to exporting.

## Importing Data

### From CSV File

CSV (Comma-Separated Values) is the most common format:

1. Navigate to **Data → Manage**
2. Click **Load Data** or **Import CSV**
3. Select your CSV file
4. Configure import options:
   - **Delimiter**: Comma, semicolon, tab, etc.
   - **Encoding**: UTF-8, Latin-1, etc.
   - **Header**: First row contains column names
   - **Index**: Use first column as index
5. Preview the data
6. Click **Import**

**Supported options:**

- Custom delimiters
- Skip rows
- Select specific columns
- Date parsing
- NA value handling

### From Excel File

Import Excel workbooks:

1. Navigate to **Data → Manage**
2. Click **Import Excel**
3. Select your Excel file (.xlsx, .xls)
4. Choose sheet to import
5. Configure options:
   - Sheet name
   - Header row
   - Skip rows
6. Preview and import

**Features:**

- Multiple sheet support
- Formula evaluation
- Date/time recognition
- Merged cell handling

### From Database

Connect to SQL databases:

1. Navigate to **Data → SQL Query**
2. Configure connection:
   - **Database Type**: SQLite, PostgreSQL, MySQL
   - **Connection String**: Database URL
   - **Query**: SQL SELECT statement
3. Test connection
4. Execute query
5. Import results

**Example connection strings:**

```
# SQLite
sqlite:///path/to/database.db

# PostgreSQL
postgresql://user:password@localhost:5432/database

# MySQL
mysql://user:password@localhost:3306/database
```

### From JSON

Import JSON data:

1. Navigate to **Data → Manage**
2. Click **Import JSON**
3. Select JSON file
4. Configure options:
   - **Orient**: records, split, index, columns
   - **Lines**: Line-delimited JSON
5. Preview and import

### Sample Datasets

AIML Dash includes built-in sample datasets:

1. Navigate to **Data → Manage**
2. Click **Load Sample Dataset**
3. Choose from available datasets:
   - **diamonds**: Diamond characteristics and prices
   - **iris**: Iris flower measurements
   - **mtcars**: Motor vehicle characteristics
   - **titanic**: Titanic passenger data
4. Click **Load**

## Viewing Data

### Data Table View

Navigate to **Data → View** to see your data:

**Features:**

- **Sorting**: Click column headers to sort
- **Filtering**: Use filter boxes to search
- **Pagination**: Navigate large datasets
- **Column Selection**: Show/hide columns
- **Export**: Download visible data

**Keyboard shortcuts:**

- Arrow keys: Navigate cells
- Home/End: Jump to first/last column
- Page Up/Down: Navigate pages

### Data Explorer

Navigate to **Data → Explore** for detailed analysis:

**Sections:**

1. **Summary Statistics**
   - Count, mean, std, min, max
   - Quartiles (25%, 50%, 75%)
   - Missing values
   - Unique values

2. **Variable Information**
   - Variable names
   - Data types
   - Memory usage
   - Value ranges

3. **Frequency Tables**
   - Value counts
   - Percentages
   - Bar charts

4. **Distribution Plots**
   - Histograms
   - Density plots
   - Box plots

## Dataset Selection

### Active Dataset

The active dataset is used by all analysis pages:

1. Use the dropdown in the **right sidebar**
2. Select from loaded datasets
3. Active dataset is highlighted

**Quick statistics** are shown for the active dataset:

- Number of rows
- Number of columns  
- Column types (numeric, categorical, datetime)
- Missing values

### Multiple Datasets

Load and work with multiple datasets:

- Each dataset has a unique name
- Switch between datasets using the selector
- Combine datasets using **Data → Combine**

## Transforming Data

### Creating New Variables

Navigate to **Data → Transform**:

1. Click **Create Variable**
2. Enter variable name
3. Define calculation:
   ```python
   # Examples:
   price / carat          # Division
   log(price)            # Log transformation
   price * 100           # Multiplication
   carat ** 2            # Squaring
   ```
4. Preview result
5. Click **Create**

**Supported functions:**

- Math: `+`, `-`, `*`, `/`, `**`, `%`
- Functions: `log`, `sqrt`, `abs`, `round`
- Conditionals: `if-else`
- String: `upper`, `lower`, `strip`

### Filtering Data

Filter rows based on conditions:

1. Click **Filter Rows**
2. Enter filter expression:
   ```python
   # Examples:
   carat > 1.0
   price < 1000
   cut == 'Ideal'
   carat > 1 & price < 5000
   cut.isin(['Ideal', 'Premium'])
   ```
3. Preview filtered data
4. Click **Apply**
5. Option to save as new dataset

**Operators:**

- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical: `&` (and), `|` (or), `~` (not)
- Membership: `.isin([...])`
- String: `.str.contains()`

### Selecting Columns

Keep only specific columns:

1. Click **Select Columns**
2. Choose columns to keep
3. Preview result
4. Click **Apply**

### Sorting Data

Sort by one or more columns:

1. Click **Sort**
2. Select column(s)
3. Choose ascending/descending
4. Click **Apply**

### Handling Missing Values

Deal with missing data:

1. Click **Handle Missing**
2. Choose method:
   - **Drop rows** with any missing values
   - **Drop rows** with all missing values
   - **Fill** with value (mean, median, mode, constant)
   - **Forward fill**: Use previous value
   - **Backward fill**: Use next value
3. Select columns to apply to
4. Preview and apply

### Grouping and Aggregation

Aggregate data by groups:

1. Click **Group By**
2. Select grouping variables
3. Choose columns to aggregate
4. Select functions:
   - count, sum, mean, median
   - min, max, std, var
5. Preview and create

Example: Average price by cut:

```
Group by: cut
Aggregate: price
Function: mean
```

### Pivoting

Reshape data with pivot tables:

1. Click **Pivot Table**
2. Configure:
   - **Index**: Row labels
   - **Columns**: Column labels  
   - **Values**: Values to aggregate
   - **Aggfunc**: Aggregation function
3. Preview and create

## Combining Datasets

Navigate to **Data → Combine**:

### Merge (Join)

Combine datasets based on common columns:

1. Select two datasets
2. Choose join type:
   - **Inner**: Only matching rows
   - **Left**: All from left, matching from right
   - **Right**: All from right, matching from left
   - **Outer**: All rows from both
3. Select join key(s)
4. Preview and merge

### Concatenate

Stack datasets vertically or horizontally:

1. Select datasets to combine
2. Choose axis:
   - **Rows** (vertical): Stack datasets
   - **Columns** (horizontal): Side by side
3. Handle mismatched columns
4. Preview and concatenate

## Data Types

### Viewing Types

See column data types in **Data → Explore**:

- **Numeric**: int64, float64
- **Categorical**: object, category
- **Datetime**: datetime64
- **Boolean**: bool

### Converting Types

Change column data types:

1. Click **Convert Type**
2. Select column
3. Choose target type:
   - Numeric (int, float)
   - String
   - Category
   - Datetime
   - Boolean
4. Handle errors
5. Apply

### Categorical Data

Convert to categorical for memory efficiency:

```python
# Example: cut, color, clarity
cut: object → category
color: object → category
```

Benefits:

- Reduced memory usage
- Faster operations
- Preserve order for ordinal variables

## Exporting Data

### Export Active Dataset

Navigate to **Data → Manage**:

1. Click **Export Data**
2. Choose format:
   - **CSV**: Comma-separated
   - **Excel**: .xlsx workbook
   - **JSON**: JSON format
   - **Parquet**: Columnar format (fast)
3. Configure options:
   - Include index
   - Date format
   - Encoding
4. Click **Download**

### Export Subset

Export filtered or transformed data:

1. Apply filters/transforms
2. Click **Export Current View**
3. Choose format and download

### Export Multiple Datasets

Export all loaded datasets:

1. Click **Export All Data**
2. Downloads as ZIP file
3. Each dataset as separate file

## Best Practices

### Data Import

- **Preview first**: Always preview before importing
- **Check types**: Verify data types are correct
- **Handle missing**: Address missing values early
- **Document**: Note data sources and versions

### Data Exploration

- **Start broad**: Overview with summary statistics
- **Then detailed**: Examine specific variables
- **Visualize**: Use plots to understand distributions
- **Check quality**: Look for errors and outliers

### Data Transformation

- **Non-destructive**: Keep original data
- **Document changes**: Note transformations applied
- **Validate results**: Check transformed data makes sense
- **Save intermediate**: Save important transformation steps

### Performance

- **Filter early**: Reduce dataset size before analysis
- **Use categories**: Convert strings to categories
- **Drop unused**: Remove unnecessary columns
- **Sample for testing**: Use subset for initial exploration

## Troubleshooting

### Import Issues

**File not found:**
- Check file path
- Verify file permissions

**Encoding errors:**
- Try different encoding (UTF-8, Latin-1, ASCII)
- Use file viewer to check encoding

**Parse errors:**
- Check delimiter is correct
- Verify file format matches extension
- Look for malformed rows

### Memory Issues

**Dataset too large:**
- Import only needed columns
- Filter rows during import
- Use sampling
- Convert to categories

### Type Conversion

**Conversion fails:**
- Check for non-numeric values
- Handle missing values first
- Use `errors='coerce'` option

## Next Steps

- [Analysis Tools](analysis-tools.md) - Analyze your data
- [Visualization](visualization.md) - Create visualizations
- [Export & Import](export-import.md) - Save your work
