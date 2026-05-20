# Polaroids
## Package is UNTESTED right now. Waiting on an opportunity to try it out

Allows one to easily generate stub files containing column names and data types for polars dataframes and lazyframes so that users get IDE autocompletion for column names. Also cleans column names to make them valid python identifiers.

Example usage, purposefully verbose for clarity:


```python
import polars as pl

# import package to register the column accessors in the polars api and get the function
# to generate stub files
from polaroids import generate_stubs

# load data and generate
df = pl.read_csv('MyData.csv')

# Load data generate stubs and get data frame with cleaned names and the mapping of
# renamed columns
df, rename_mapping = generate_stubs(
    pl.read_csv('MyData.csv'), class_name='MyData'
)  # file_path defaults to polaroids_stubs.py in same directory

# You can store multiple schemas in the same file
extended_df, extended_rename_mapping = generate_stubs(
    df.with_columns(col_c=df.c.col_a + df.c.col_b), 'ExtendedMyData'
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

# now the "c" column accessor can be used anywhere a polars expression is valid and you
# will get IDE autocompletion for the column names. Doc strings indicate underlying
# polars datatype and original column name if it was changed.
filtered_df: MyData = df.filter(df.c.col_a > 5, df.c.col_b <= 100)

```

Things to be aware of when using columns from the returned data frame:
1. Spaces and other non-alphanumeric characters ($, %, &, etc.) will be replaced with underscores
2. Columns with empty strings as names (which is valid in Polars, it turns out) will be renamed as "\_empty\_"
3. Column names which begin with a digit will be prefixed with an underscore

If the original column names are critical for plotting or other downstream applications, databases, or processes, the user can rename the dataframe back to the original names before exporting by reversing the mapping used returned from the `generate_stubs` function:
```python
reverse_mapping = {clean: orig for orig, clean in rename_mapping.items() if clean in df.columns}
df.rename(reverse_mapping).write_csv('ExportMyData.csv')
```
