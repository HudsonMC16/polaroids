# Polaroids

Allows one to easily generate stub files containing column names and data types for polars dataframes and lazyframes so that users get IDE autocompletion for column names. Also cleans column names to make them valid python identifiers.

Example usage, purposefully verbose for clarity:

```python
import polars as pl
# import package to register the column accessors in the polars api and get the function to generate stub files
from polaroids import generate_stubs

# load data
raw_df = pl.read_csv('MyData.csv')

# Generate stubs
clean_df = generate_stubs(df, class_name='MyData') # file_path defaults to polaroids.py in same directory

# import stubs, but protect the import with a try/except block for the first time this code is run
try:
    from polaroids import MyData
except ImportError:
    MyData = pl.DataFrame

# type hint our final data frame for use in the rest of the script
df: MyData = clean_df

# now the "c" column accessor can be used anywhere a polars expression is valid and you will get IDE autocompletion for the column names
filtered_df: MyData = df.filter(df.c.col_a > 5, df.c.col_b <= 100)
```
