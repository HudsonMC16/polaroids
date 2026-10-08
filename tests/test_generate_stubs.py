from pathlib import Path

import polars as pl
from polaroids import generate_stubs


def test_generate_stubs_basic(sample_df: pl.DataFrame, tmp_path: Path):
    stub_file = tmp_path / 'polaroids_stubs.py'
    renamed_df, rename_mapping = generate_stubs(
        sample_df, 'MyData', file_path=stub_file
    )

    # Check returned dataframe & mapping
    assert 'col b' in rename_mapping
    assert rename_mapping['col b'] == 'col_b'
    assert rename_mapping['123_num'] == '_123_num'
    assert rename_mapping[''] == '_empty_'
    assert renamed_df.columns == ['col_a', 'col_b', '_123_num', '_empty_']

    # Check generated stub file contents
    content = stub_file.read_text(encoding='utf-8')
    assert '# --- START MyData ---' in content
    assert '# --- END MyData ---' in content
    assert 'class MyData(pl.DataFrame):' in content
    assert 'class MyDataExprCols:' in content
    assert 'class MyDataNameCols:' in content
    assert 'class MyDataSeriesCols:' in content
    assert 'col_b: MyData_col_b_Expr' in content
    assert 'col_b: MyData_col_b_Name' in content
    assert 'col_b: MyData_col_b_Series' in content
    assert '_123_num: MyData__123_num_Expr' in content
    assert '_empty_: MyData__empty__Expr' in content
    assert 'def x(self) -> MyDataExprCols:' in content
    assert 'def n(self) -> MyDataNameCols:' in content
    assert 'def s(self) -> MyDataSeriesCols:' in content

    # Ensure generated stub is valid Python code
    compile(content, str(stub_file), 'exec')


def test_column_sanitization_edge_cases(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame(
        {
            'Spaces & % Symbols!': [1],
            '123StartWithDigit': [2],
            '___': [3],
            'UPPERCASE': [4],
        }
    )

    renamed_df, mapping = generate_stubs(
        df, 'EdgeCases', file_path=stub_file, lowercase=True
    )

    assert mapping['Spaces & % Symbols!'] == 'spaces_symbols'
    assert mapping['123StartWithDigit'] == '_123startwithdigit'
    assert mapping['___'] == '_empty_'
    assert mapping['UPPERCASE'] == 'uppercase'
    assert renamed_df.columns == [
        'spaces_symbols',
        '_123startwithdigit',
        '_empty_',
        'uppercase',
    ]

    content = stub_file.read_text(encoding='utf-8')
    compile(content, str(stub_file), 'exec')


def test_name_collision_deduplication(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame(
        {
            'col a': [1],
            'col-a': [2],
            'col_a': [3],
        }
    )

    renamed_df, mapping = generate_stubs(df, 'Collisions', file_path=stub_file)

    assert renamed_df.columns == ['col_a', 'col_a_1', 'col_a_2']
    assert mapping['col a'] == 'col_a'
    assert mapping['col-a'] == 'col_a_1'


def test_single_quote_docstring_escaping(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame(
        {
            "user's_column": [1],
        }
    )

    _, mapping = generate_stubs(df, 'QuoteTest', file_path=stub_file)

    content = stub_file.read_text(encoding='utf-8')
    assert "user\\'s_column" in content
    compile(content, str(stub_file), 'exec')


def test_double_quote_and_backslash_escaping(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame(
        {
            'user"\\"\\"\\"col': [1],
        }
    )

    _, mapping = generate_stubs(df, 'SpecialEscapeTest', file_path=stub_file)

    content = stub_file.read_text(encoding='utf-8')
    compile(content, str(stub_file), 'exec')


def test_update_existing_class_block(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'

    # Generate initial stubs
    df_v1 = pl.DataFrame({'old_col': [1]})
    generate_stubs(df_v1, 'Schema', file_path=stub_file)

    initial_content = stub_file.read_text(encoding='utf-8')
    assert 'old_col' in initial_content

    # Update with new schema for same class name
    df_v2 = pl.DataFrame({'new_col': [10]})
    generate_stubs(df_v2, 'Schema', file_path=stub_file)

    updated_content = stub_file.read_text(encoding='utf-8')
    assert 'new_col' in updated_content
    assert 'old_col' not in updated_content
    assert updated_content.count('# --- START Schema ---') == 1
    compile(updated_content, str(stub_file), 'exec')


def test_append_multiple_classes(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'

    df1 = pl.DataFrame({'first': [1]})
    df2 = pl.DataFrame({'second': [2]})

    generate_stubs(df1, 'ClassOne', file_path=stub_file)
    generate_stubs(df2, 'ClassTwo', file_path=stub_file)

    content = stub_file.read_text(encoding='utf-8')
    assert '# --- START ClassOne ---' in content
    assert '# --- START ClassTwo ---' in content
    assert 'class ClassOne(pl.DataFrame):' in content
    assert 'class ClassTwo(pl.DataFrame):' in content
    compile(content, str(stub_file), 'exec')


def test_lazyframe_support(sample_lazy_df: pl.LazyFrame, tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    renamed_lazy, mapping = generate_stubs(
        sample_lazy_df, 'LazyData', file_path=stub_file
    )

    assert isinstance(renamed_lazy, pl.LazyFrame)
    assert 'col b' in mapping
    assert renamed_lazy.collect_schema().names() == [
        'col_a',
        'col_b',
        '_123_num',
        '_empty_',
    ]

    content = stub_file.read_text(encoding='utf-8')
    assert 'class LazyData(pl.LazyFrame):' in content
    assert 'class LazyDataExprCols:' in content
    assert 'class LazyDataNameCols:' in content
    assert 'class LazyDataSeriesCols:' not in content
    assert 'def x(self) -> LazyDataExprCols:' in content
    assert 'def n(self) -> LazyDataNameCols:' in content
    assert 'def s(self)' not in content
    compile(content, str(stub_file), 'exec')


def test_reserved_keywords_sanitization(tmp_path: Path):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame(
        {
            'class': [1],
            'import': [2],
            'def': [3],
            'FOR': [4],
        }
    )

    renamed_df, mapping = generate_stubs(
        df, 'KwData', file_path=stub_file, lowercase=True
    )

    assert mapping['class'] == 'class_'
    assert mapping['import'] == 'import_'
    assert mapping['def'] == 'def_'
    assert mapping['FOR'] == 'for_'
    assert renamed_df.columns == ['class_', 'import_', 'def_', 'for_']


def test_verbose_flag(tmp_path: Path, capsys):
    stub_file = tmp_path / 'stubs.py'
    df = pl.DataFrame({'col a': [1]})

    generate_stubs(df, 'Quiet', file_path=stub_file, verbose=False)
    captured = capsys.readouterr()
    assert captured.out == ''

    generate_stubs(df, 'Loud', file_path=stub_file, verbose=True)
    captured = capsys.readouterr()
    assert '--- Renamed Columns for Loud ---' in captured.out
