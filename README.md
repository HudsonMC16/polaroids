# Polaroids

Allows one to easily generate stub files containing column names and data types for polars dataframes and lazyframes so that users get IDE autocompletion for column names. Also cleans column names to make them valid python identifiers.

Polaroids provides three ergonomic accessors:
- **`df.x.col_name`**: Column expression accessor returning a `pl.Expr` for query contexts (`select`, `filter`, `with_columns`, etc.). Available on both `DataFrame` and `LazyFrame`.
- **`df.s.col_name`**: Column Series accessor returning the `pl.Series` data directly (`df.get_column(...)`). Available ONLY on `DataFrame`.
- **`df.n.col_name`**: Column name accessor returning the column name as a `str` for libraries expecting column strings (e.g., Plotly). Available on both `DataFrame` and `LazyFrame`.

Example usage, purposefully verbose for clarity:

```python
from typing import cast
import polars as pl

# import package to register the column accessors in the polars api and get the function
# to generate stub files
from polaroids import generate_stubs

# Load data, generate stubs, and get data frame with cleaned names and the mapping of
# renamed columns
df, rename_mapping = generate_stubs(
    pl.read_csv('MyData.csv'), class_name='MyData'
)  # file_path defaults to polaroids_stubs.py in same directory

# You can store multiple schemas in the same file
extended_df, extended_rename_mapping = generate_stubs(
    df.with_columns(col_c=df.x.col_a + df.x.col_b), 'ExtendedMyData'
)

# import types, but protect the import with a try/except block for the first time this
# code is run
try:
    from polaroids_stubs import MyData, ExtendedMyData
except ImportError:
    MyData = ExtendedMyData = pl.DataFrame

# type cast our final data frames for use in the rest of the script
df = cast(MyData, df)
extended_df = cast(ExtendedMyData, extended_df)

# The "x" accessor can be used anywhere a polars expression is valid with
# IDE autocompletion for column names. Docstrings indicate underlying
# polars datatype and original column name if it was changed.
filtered_df: MyData = df.filter(df.x.col_a > 5, df.x.col_b <= 100)

# The "s" accessor provides direct access to the column data as a polars Series:
first_val = df.s.col_a[0]
val_list = df.s.col_b.to_list()

# The "n" accessor provides the column names as strings for use in libraries
# which expect strings, like plotly for plotting:
import plotly.express as px

px.line(df, x=df.n.col_a, y=df.n.col_b, color=df.n.col_c).show()
```

Things to be aware of when using columns from the returned data frame:
1. Spaces and other non-alphanumeric characters ($, %, &, etc.) will be replaced with
   underscores. The dataframe returned from `generate_stubs()` will have the updated
   column names, and the changes will be printed to console when this function is run so
   the user is aware.
2. Columns with empty strings as names (which is valid in Polars, it turns out) will be
   renamed as "\_empty\_"
3. Column names which begin with a digit will be prefixed with an underscore
4. Column names matching Python reserved keywords (e.g. `class`, `import`, `def`) will be suffixed with an underscore (e.g. `class_`, `import_`, `def_`) to prevent invalid Python syntax in generated stubs.


If the original column names are critical for plotting or other downstream applications,
databases, or processes, the user can rename the dataframe back to the original names
before exporting by reversing the mapping used returned from the `generate_stubs()`
function:
```python
reverse_mapping = {clean: orig for orig, clean in rename_mapping.items() if clean in df.columns}
df.rename(reverse_mapping).write_csv('ExportMyData.csv')
```
