"""Small package to generated clean type stubs for polars dataframe columns."""

import keyword
import re
from pathlib import Path
from typing import Union

import polars as pl


@pl.api.register_dataframe_namespace('c')
class ColumnAccessor:
    """Provides dot notation access to polars dataframe columns i.e. `df.c.col_name`."""

    def __init__(self, df: pl.DataFrame) -> None:
        """Initializes column accessor.

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
        return pl.col(col_name)

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in dataframe
        """
        return self._df.columns


@pl.api.register_lazyframe_namespace('c')
class LazyColumnAccessor:
    """Provides dot notation access to polars lazyframe columns i.e. `df.c.col_name`."""

    def __init__(self, df: pl.LazyFrame) -> None:
        """Initializes column accessor.

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
        return pl.col(col_name)

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in lazyframe
        """
        return self._df.collect_schema().names()


@pl.api.register_dataframe_namespace('s')
class ColumnStringAccessor:
    """Provides dot notation access to polars dataframe column names as strings."""

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
        return col_name

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in dataframe
        """
        return self._df.columns


@pl.api.register_lazyframe_namespace('s')
class LazyColumnStringAccessor:
    """Provides dot notation access to polars lazyframe column names as strings."""

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
        return col_name

    def __dir__(self) -> list[str]:
        """Returns list of column names for environments which need it.

        Returns:
            list[str]: list of column names in lazyframe
        """
        return self._df.collect_schema().names()


def generate_stubs(
    df: Union[pl.DataFrame, pl.LazyFrame],
    class_name: str,
    file_path: Union[Path, str] = 'polaroids_stubs.py',
    lowercase: bool = False,
) -> tuple[Union[pl.DataFrame, pl.LazyFrame], dict[str, str]]:
    """Generate stubs for polars dataframe schema for IDE autocompletion.

    Also cleans column names to valid python identifiers returns original object with
    updated column names

    Args:
        df (Union[pl.DataFrame, pl.LazyFrame]): Polars dataframe or lazyframe from which
            to generate stubs
        class_name (str): name of class in generated stub files. Should also be used in
            code as type hint for dataframes with these columns
        file_path (Union[Path, str]):path to write stub file. Defaults to
            "polaroids_stubs.py"
        lowercase (bool): will lowercase columns names when transforming to valid python
            identifiers. Defaults to False

    Returns:
        Union[pl.DataFrame, pl.LazyFrame]: Original dataframe/lazyframe with the columns
            renamed to valid python identifiers
        dict[str, str]: dictionary containing the mapping of original column names to
            the modified (cleaned) names. Has format `original: new`
    """
    schema = df.schema if isinstance(df, pl.DataFrame) else df.collect_schema()

    lines = [f'# --- START {class_name} ---']
    rename_mapping = {}
    all_col_names = set()
    col_classes = []
    col_attributes = [f'class {class_name}Cols:']
    col_str_attributes = [f'class {class_name}StrCols:']
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

        if safe_col_name != col_name:
            rename_mapping[col_name] = safe_col_name
            escaped_col_name = col_name.replace("'", "\\'")
            doc_str = f'dtype: {dtype}, original name: {escaped_col_name}'
        else:
            doc_str = f'dtype: {dtype}'

        col_class_name = f'{class_name}_{safe_col_name}'
        col_str_class_name = f'{class_name}_{safe_col_name}_Str'

        col_classes.extend(
            [
                f'class {col_class_name}(pl.Expr):',
                f'    """{doc_str}"""',
                '    ...',
                f'class {col_str_class_name}(str):',
                f'    """{doc_str}"""',
                '    ...',
            ]
        )
        col_attributes.append(f'    {safe_col_name}: {col_class_name}')
        col_str_attributes.append(f'    {safe_col_name}: {col_str_class_name}')

    lines.extend(col_classes)
    lines.append('')
    lines.extend(col_attributes)
    lines.append('')
    lines.extend(col_str_attributes)
    lines.extend(
        [
            '',
            f'class {class_name}(pl.DataFrame):',
            '    @property',
            f'    def c(self) -> {class_name}Cols:',
            '        ...',
            '    @property',
            f'    def s(self) -> {class_name}StrCols:',
            '        ...',
            f'# --- END {class_name} ---',
            '',
        ]
    )
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
        print(f'--- Renamed Columns for {class_name} ---')
        for old, new in rename_mapping.items():
            print(f"    '{old}' -> '{new}'")
        df = df.rename(rename_mapping)

    return df, rename_mapping
