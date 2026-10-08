"""Small package to generate clean type stubs and column accessors for polars dataframes."""

import keyword
import re
from pathlib import Path

import polars as pl

__all__ = [
    'ColumnExprAccessor',
    'ColumnNameAccessor',
    'ColumnSeriesAccessor',
    'LazyColumnExprAccessor',
    'LazyColumnNameAccessor',
    # Backwards compatibility aliases
    'ColumnAccessor',
    'ColumnStringAccessor',
    'LazyColumnAccessor',
    'LazyColumnStringAccessor',
    'generate_stubs',
]


@pl.api.register_dataframe_namespace('x')
class ColumnExprAccessor:
    """Provides dot notation access to polars dataframe column expressions i.e. `df.x.col_name`."""

    def __init__(self, df: pl.DataFrame) -> None:
        """Initializes column expression accessor.

        Args:
            df (pl.DataFrame): Polars dataframe to wrap
        """
        self._df = df

    def __getattr__(self, col_name: str) -> pl.Expr:
        """Gets named column and returns a polars expression.

        Args:
            col_name (str): name of dataframe column

        Returns:
            pl.Expr: Polars expression representing the named column
        """
        if col_name.startswith('__') or col_name not in self._df.columns:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{col_name}'"
            )
        return pl.col(col_name)

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in dataframe
        """
        return self._df.columns


@pl.api.register_lazyframe_namespace('x')
class LazyColumnExprAccessor:
    """Provides dot notation access to polars lazyframe column expressions i.e. `df.x.col_name`."""

    def __init__(self, df: pl.LazyFrame) -> None:
        """Initializes column expression accessor.

        Args:
            df (pl.LazyFrame): Polars lazyframe to wrap
        """
        self._df = df

    def __getattr__(self, col_name: str) -> pl.Expr:
        """Gets named column and returns a polars expression.

        Args:
            col_name (str): name of lazyframe column

        Returns:
            pl.Expr: Polars expression representing the named column
        """
        if (
            col_name.startswith('__')
            or col_name not in self._df.collect_schema().names()
        ):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{col_name}'"
            )
        return pl.col(col_name)

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in lazyframe
        """
        return self._df.collect_schema().names()


@pl.api.register_dataframe_namespace('n')
class ColumnNameAccessor:
    """Provides dot notation access to polars dataframe column names as strings i.e. `df.n.col_name`."""

    def __init__(self, df: pl.DataFrame) -> None:
        """Initializes column name string accessor.

        Args:
            df (pl.DataFrame): Polars dataframe to wrap
        """
        self._df = df

    def __getattr__(self, col_name: str) -> str:
        """Gets column name as a string and returns it.

        Args:
            col_name (str): name of dataframe column

        Returns:
            str: name of column as a string
        """
        if col_name.startswith('__') or col_name not in self._df.columns:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{col_name}'"
            )
        return col_name

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in dataframe
        """
        return self._df.columns


@pl.api.register_lazyframe_namespace('n')
class LazyColumnNameAccessor:
    """Provides dot notation access to polars lazyframe column names as strings i.e. `df.n.col_name`."""

    def __init__(self, df: pl.LazyFrame) -> None:
        """Initializes column name string accessor.

        Args:
            df (pl.LazyFrame): Polars lazyframe to wrap
        """
        self._df = df

    def __getattr__(self, col_name: str) -> str:
        """Gets column name as a string and returns it.

        Args:
            col_name (str): name of lazyframe column

        Returns:
            str: name of column as a string
        """
        if (
            col_name.startswith('__')
            or col_name not in self._df.collect_schema().names()
        ):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{col_name}'"
            )
        return col_name

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in lazyframe
        """
        return self._df.collect_schema().names()


@pl.api.register_dataframe_namespace('s')
class ColumnSeriesAccessor:
    """Provides dot notation access to polars dataframe column Series i.e. `df.s.col_name`."""

    def __init__(self, df: pl.DataFrame) -> None:
        """Initializes column series accessor.

        Args:
            df (pl.DataFrame): Polars dataframe to wrap
        """
        self._df = df

    def __getattr__(self, col_name: str) -> pl.Series:
        """Gets named column and returns a polars Series.

        Args:
            col_name (str): name of dataframe column

        Returns:
            pl.Series: Polars Series containing column data
        """
        if col_name.startswith('__') or col_name not in self._df.columns:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{col_name}'"
            )
        return self._df.get_column(col_name)

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in dataframe
        """
        return self._df.columns


# Backwards compatibility aliases
ColumnAccessor = ColumnExprAccessor
ColumnStringAccessor = ColumnNameAccessor
LazyColumnAccessor = LazyColumnExprAccessor
LazyColumnStringAccessor = LazyColumnNameAccessor


def generate_stubs(
    df: pl.DataFrame | pl.LazyFrame,
    class_name: str,
    file_path: Path | str = 'polaroids_stubs.py',
    lowercase: bool = False,
    verbose: bool = True,
) -> tuple[pl.DataFrame | pl.LazyFrame, dict[str, str]]:
    """Generate stubs for polars dataframe or lazyframe schema for IDE autocompletion.

    Also cleans column names to valid python identifiers and returns original object
    with updated column names.

    Args:
        df (pl.DataFrame | pl.LazyFrame): Polars dataframe or lazyframe from which
            to generate stubs
        class_name (str): name of class in generated stub files. Should also be used in
            code as type hint for dataframes with these columns
        file_path (Path | str): path to write stub file. Defaults to
            "polaroids_stubs.py"
        lowercase (bool): will lowercase column names when transforming to valid python
            identifiers. Defaults to False
        verbose (bool): whether to print renamed column mappings to console. Defaults to
            True

    Returns:
        tuple[pl.DataFrame | pl.LazyFrame, dict[str, str]]: Original dataframe/lazyframe
            with the columns renamed to valid python identifiers, and dictionary
            containing the mapping of original column names to the modified (cleaned)
            names. Has format `original: new`
    """
    is_lazy = isinstance(df, pl.LazyFrame)
    schema = df.collect_schema() if is_lazy else df.schema

    lines = [f'# --- START {class_name} ---']
    rename_mapping = {}
    all_col_names = set()
    col_classes = []
    col_expr_attributes = [f'class {class_name}ExprCols:']
    col_name_attributes = [f'class {class_name}NameCols:']
    col_series_attributes = [f'class {class_name}SeriesCols:'] if not is_lazy else []

    for col_name, dtype in schema.items():
        safe_col_name = re.sub(r'[^0-9a-zA-Z_]', '_', col_name)
        safe_col_name = re.sub(r'_+', '_', safe_col_name).strip('_')

        if not safe_col_name:
            safe_col_name = '_empty_'
        if safe_col_name[0].isdigit():
            safe_col_name = f'_{safe_col_name}'
        if lowercase:
            safe_col_name = safe_col_name.lower()
        if keyword.iskeyword(safe_col_name):
            safe_col_name = f'{safe_col_name}_'

        suffix = 1
        original = safe_col_name
        while safe_col_name in all_col_names:
            safe_col_name = f'{original}_{suffix}'
            suffix += 1

        all_col_names.add(safe_col_name)

        escaped_col_name = (
            col_name.replace('\\', '\\\\')
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
        )
        if safe_col_name != col_name:
            rename_mapping[col_name] = safe_col_name
            doc_str = f"dtype: {dtype}, original name: '{escaped_col_name}'"
        else:
            doc_str = f'dtype: {dtype}'

        col_expr_class_name = f'{class_name}_{safe_col_name}_Expr'
        col_name_class_name = f'{class_name}_{safe_col_name}_Name'

        col_classes.extend(
            [
                f'class {col_expr_class_name}(pl.Expr):',
                f'    """{doc_str}"""',
                '    ...',
                f'class {col_name_class_name}(str):',
                f'    """{doc_str}"""',
                '    ...',
            ]
        )
        col_expr_attributes.append(f'    {safe_col_name}: {col_expr_class_name}')
        col_name_attributes.append(f'    {safe_col_name}: {col_name_class_name}')

        if not is_lazy:
            col_series_class_name = f'{class_name}_{safe_col_name}_Series'
            col_classes.extend(
                [
                    f'class {col_series_class_name}(pl.Series):',
                    f'    """{doc_str}"""',
                    '    ...',
                ]
            )
            col_series_attributes.append(
                f'    {safe_col_name}: {col_series_class_name}'
            )

    lines.extend(col_classes)
    lines.append('')
    lines.extend(col_expr_attributes)
    lines.append('')
    lines.extend(col_name_attributes)
    if not is_lazy:
        lines.append('')
        lines.extend(col_series_attributes)

    base_class = 'pl.LazyFrame' if is_lazy else 'pl.DataFrame'
    class_def = [
        '',
        f'class {class_name}({base_class}):',
        '    @property',
        f'    def x(self) -> {class_name}ExprCols:',
        '        ...',
        '    @property',
        f'    def n(self) -> {class_name}NameCols:',
        '        ...',
    ]
    if not is_lazy:
        class_def.extend(
            [
                '    @property',
                f'    def s(self) -> {class_name}SeriesCols:',
                '        ...',
            ]
        )
    class_def.extend(
        [
            f'# --- END {class_name} ---',
            '',
        ]
    )
    lines.extend(class_def)

    new_text = '\n'.join(lines)
    path = Path(file_path)

    if path.exists():
        content = path.read_text(encoding='utf-8')
    else:
        content = '\n'.join(
            ['# Stub file generated by polaroids', 'import polars as pl', '', '']
        )

    search_pattern = re.compile(
        rf'# --- START {class_name} ---.*?# --- END {class_name} ---\n*', re.DOTALL
    )

    if search_pattern.search(content):
        new_content = search_pattern.sub(new_text + '\n', content)
    else:
        new_content = content + new_text + '\n'

    if not (path.exists() and content == new_content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_content, encoding='utf-8')

    if rename_mapping:
        if verbose:
            print(f'--- Renamed Columns for {class_name} ---')
            for old, new in rename_mapping.items():
                print(f"    '{old}' -> '{new}'")
        df = df.rename(rename_mapping)

    return df, rename_mapping
